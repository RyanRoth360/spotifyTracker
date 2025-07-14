from flask import jsonify
from lib.spotify_helpers import add_album_data

def get_profile_data(mongo_db, username):
    try:
        query = {"username": username}
        data = mongo_db.find_one(query)

        if not data:
            return jsonify({"error": "User not found"}), 404

        add_album_data(data)

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

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def update_flag(mongo_db, payload):
    try:
        username = payload.get("username")
        album_id = payload.get("albumId")
        update = payload.get("update")
        flag = payload.get("flag")

        if not username or not album_id or update not in ["favorite", "bookmarked"]:
            return jsonify({"error": "Invalid request data"}), 400

        result = mongo_db.collection.update_one(
            {"username": username, "albums.albumId": album_id},
            {"$set": {f"albums.$.{update}": flag}}
        )

        if result.modified_count > 0:
            return jsonify({"message": f"{update.capitalize()} flag updated"}), 200
        else:
            return jsonify({"warning": "No document updated"}), 404

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
