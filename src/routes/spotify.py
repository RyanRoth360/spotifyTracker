from bson import ObjectId
from flask import Flask, jsonify, request
from lib.spotify_helpers import clean_albums_data
from lib.spotipy_client import get_sp_client

def get_album_data(mongo_db, album_id):
    result = mongo_db.find_one({"_id": ObjectId(album_id)})
    if not result:
        pass
        # query spotify API
    return result


def spotify_search(request):
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    sp = get_sp_client()
    sp.authorize_user()
    try:
        res = sp.generic_search(query)
        album_items = res.get("albums", {}).get("items", [])
        track_items = res.get("tracks", {}).get("items", [])
        artist_items = res.get("artists", {}).get("items", [])

        track_albums = [t.get("album") for t in track_items if t.get("album")]

        artist_albums = []
        for artist in artist_items:
            artist_id = artist.get("id")
            if artist_id:
                artist_album_res = sp.get_artist_albums(artist_id)
                artist_albums.extend(artist_album_res.get("items", []))

        all_albums = album_items + track_albums + artist_albums

        cleaned = clean_albums_data(all_albums, limit=10)
        return jsonify(cleaned)

    except Exception as exc:
        return jsonify([]), 500


def get_track_data(album_id):
    sp = get_sp_client()
    sp.authorize_user()
    try:
        res = sp.get_track_data(album_id)
        return jsonify(res), 200
    except Exception as exc:
        return jsonify([]), 500