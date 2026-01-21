from flask import jsonify

from lib.enums import DatabaseError, ReturnTypes, SpotifyAPIError
from lib.spotipy_client import SpotipyClient


def get_profile_data(username, mongo_db, client: SpotipyClient):
    """Query mongo for profile data and Spotify for album data"""

    # Query DB
    try:
        query = {"username": username}
        data = mongo_db.find_one(query)
    except Exception as exc:
        return str(DatabaseError(exc)), 500

    if not data:
        return ReturnTypes.UserDataNotFound, 404

    # Query spotify
    try:
        for album in data.get("albums", []):
            album.update(client.get_album_data(album["albumId"]))
    except Exception as exc:
        print(exc)
        return str(SpotifyAPIError(exc)), 500

    # Process spotify results
    ranked, bookmarked, rank_sum = 0, 0, 0
    for album in data.get("albums", []):
        if album.get("bookmarked", False):
            bookmarked += 1
        else:
            rank_sum += album.get("rank", 0)
            ranked += 1

    data["rankedCount"] = ranked
    data["bookmarkedCount"] = bookmarked
    data["avgRank"] = round(rank_sum / ranked, 2) if ranked > 0 else 0.0

    return jsonify(data), 200


def update_favorite_or_bookmarked(mongo_db, username, payload):
    album_id = payload.get("albumId")
    update = payload.get("update")
    flag = payload.get("flag")

    # Add new bookmarked album
    if update == "bookmarked" and flag:
        new_bookmark = {"albumId": album_id, "bookmarked": True}
        result = mongo_db.update_one(
            {"username": username},
            {"$addToSet": {"albums": new_bookmark}},
        )
        return "Update successful", 200

    # Unbookmark - remove the album if it only has bookmarked flag
    elif update == "bookmarked" and not flag:
        # First try to update if album exists
        result = mongo_db.update_one(
            {"username": username, "albums.albumId": album_id},
            {"$set": {"albums.$.bookmarked": False}},
        )
        # If album was updated, check if it should be removed entirely
        if result.modified_count > 0:
            # Remove album if it has no rank and is not favorited
            mongo_db.update_one(
                {"username": username},
                {
                    "$pull": {
                        "albums": {
                            "albumId": album_id,
                            "bookmarked": False,
                            "$or": [{"rank": {"$exists": False}}, {"rank": 0}],
                        }
                    }
                },
            )
        return "Update successful", 200

    # Update other flags (favorite, etc)
    else:
        update_data = {f"albums.$.{update}": flag}
        result = mongo_db.update_one(
            {"username": username, "albums.albumId": album_id},
            {"$set": update_data},
        )
        if result.modified_count > 0:
            return "Update successful", 200
        else:
            return "Update unsuccessful", 404


def edit_album(mongo_db, username, payload):
    album_id = payload["albumId"]
    rank = payload["rank"]
    description = payload["description"]

    # First try to update existing album
    update_data = {
        "albums.$.rank": int(rank),
        "albums.$.description": description,
        "albums.$.bookmarked": False,  # Remove from bookmarked when ranking
    }
    result = mongo_db.update_one(
        {"username": username, "albums.albumId": album_id},
        {"$set": update_data},
    )

    # If album doesn't exist, add it
    if result.matched_count == 0:
        new_album = {
            "albumId": album_id,
            "rank": int(rank),
            "description": description,
            "bookmarked": False,
            "favorite": False,
        }
        result = mongo_db.update_one(
            {"username": username},
            {"$push": {"albums": new_album}},
        )
        if result.modified_count > 0:
            return "Album added successfully", 200
        else:
            return "Update unsuccessful", 404
    elif result.modified_count > 0:
        return "Update successful", 200
    else:
        return "Update unsuccessful", 404


def delete_album(mongo_db, username, album_id):
    """Delete an album"""
    result = mongo_db.update_one(
        {"username": username},
        {"$pull": {"albums": {"albumId": album_id}}},
    )
    if result.modified_count > 0:
        return "Update successful", 200
    else:
        return "Update unsuccessful", 404
