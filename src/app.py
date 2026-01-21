import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, session
from flask_cors import CORS

from lib.enums import ReturnTypes, SpotifyClientNotAuthenticated
from lib.pymongo_client import create_pymongo_client
from lib.spotipy_client import create_spotify_client
from routes import profile, social, spotify

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000", "http://127.0.0.1:3000"],
)

# LOAD SECRET KEY
load_dotenv()
app.secret_key = os.getenv("SECRET_APP_KEY")

MONGO_DB = create_pymongo_client("users")


# AUTH FLOW
@app.route("/api/login", methods=["GET"])
def login():
    client, _ = create_spotify_client()
    return jsonify({"auth_url": client.get_auth_url()}), 200


# Spotify calls this after oauth
@app.route("/callback")
def callback():
    client, _ = create_spotify_client()
    auth_code = request.args.get("code")
    token_data = client.get_token_from_auth_code(auth_code)
    session["token_info"] = token_data
    # redirect back to your single-page app (React root)
    return redirect("http://127.0.0.1:3000/")


# Called after refresh is triggered in the UI
@app.route("/api/me", methods=["GET"])
def me():
    # Check if the user has a valid token in the session
    token_info = session.get("token_info")
    if not token_info:
        return jsonify({"error": "Not logged in"}), 401

    client, _ = create_spotify_client(token_info)
    try:
        user = client.get_username()["display_name"]
        session["username"] = user
        return jsonify(user), 200
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Failed to fetch user info"}), 500


# USER DATA ENDPOINTS
@app.route("/api/profile/<username>", methods=["GET"])
def get_profile_data(username):
    """Return profile data and status code given username"""
    client, token_info = create_spotify_client(session.get("token_info"))
    if token_info:
        session["token_info"] = token_info
    try:
        return profile.get_profile_data(username, MONGO_DB, client)
    except SpotifyClientNotAuthenticated:
        return ReturnTypes.UserNotAuthenticated, 401
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/profile/update-flag", methods=["POST"])
def update_favorite_or_bookmarked():
    username = session.get("username", "")
    try:
        return profile.update_favorite_or_bookmarked(MONGO_DB, username, request.json)
    except Exception as exc:
        return str(exc), 500


@app.route("/api/profile/delete-album/<album_id>", methods=["DELETE"])
def delete_album(album_id):
    username = session.get("username", "")
    try:
        return profile.delete_album(MONGO_DB, username, album_id)
    except Exception as exc:
        return str(exc), 500


@app.route("/api/profile/edit", methods=["POST"])
def edit_album():
    username = session.get("username", "")
    try:
        return profile.edit_album(MONGO_DB, username, request.json)
    except Exception as exc:
        print(exc)
        return str(exc), 500


# SPOTIFY DATA ENDPOINTS
@app.route("/api/spotify/track-data/<album_id>", methods=["GET"])
def get_track_data(album_id):
    """Return track data given album id"""
    client, token_info = create_spotify_client(session.get("token_info"))
    if token_info:
        session["token_info"] = token_info
    try:
        return jsonify(client.get_track_data(album_id)), 200
    except SpotifyClientNotAuthenticated:
        return ReturnTypes.UserNotAuthenticated, 401
    except Exception as exc:
        return str(exc), 500


@app.route("/api/spotify/search", methods=["GET"])
def spotify_search():
    """Seach via album, artist, or track"""
    client, token_info = create_spotify_client(session.get("token_info"))
    if token_info:
        session["token_info"] = token_info
    return jsonify(spotify.spotify_search(request, client)), 200


@app.route("/api/spotify/trending", methods=["GET"])
def trending_albums():
    """Get trending/new release albums"""
    client, token_info = create_spotify_client(session.get("token_info"))
    if token_info:
        session["token_info"] = token_info
    try:
        return jsonify(spotify.get_trending_albums(client)), 200
    except SpotifyClientNotAuthenticated:
        return ReturnTypes.UserNotAuthenticated, 401
    except Exception as exc:
        return str(exc), 500


@app.route("/api/spotify/popular", methods=["GET"])
def popular_albums():
    """Get popular albums from featured playlists"""
    client, token_info = create_spotify_client(session.get("token_info"))
    if token_info:
        session["token_info"] = token_info
    try:
        return jsonify(spotify.get_popular_albums(client)), 200
    except SpotifyClientNotAuthenticated:
        return ReturnTypes.UserNotAuthenticated, 401
    except Exception as exc:
        return str(exc), 500


# SOCIAL ENDPOINTS
@app.route("/api/social/feed", methods=["GET"])
def get_feed():
    """Get feed of posts from followed users"""
    username = session.get("username", "")
    limit = request.args.get("limit", 20, type=int)
    skip = request.args.get("skip", 0, type=int)
    
    client, token_info = create_spotify_client(session.get("token_info"))
    if token_info:
        session["token_info"] = token_info
    try:
        return social.get_feed(username, MONGO_DB, client, limit, skip)
    except SpotifyClientNotAuthenticated:
        return ReturnTypes.UserNotAuthenticated, 401
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/social/post", methods=["POST"])
def create_post():
    """Create a new post"""
    username = session.get("username", "")
    try:
        return social.create_post(username, MONGO_DB, request.json)
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/social/post/<album_id>", methods=["DELETE"])
def delete_post(album_id):
    """Delete a post"""
    username = session.get("username", "")
    try:
        return social.delete_post(username, MONGO_DB, album_id)
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/social/follow/<target_username>", methods=["POST"])
def follow_user(target_username):
    """Follow a user"""
    username = session.get("username", "")
    try:
        return social.follow_user(username, MONGO_DB, target_username)
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/social/unfollow/<target_username>", methods=["POST"])
def unfollow_user(target_username):
    """Unfollow a user"""
    username = session.get("username", "")
    try:
        return social.unfollow_user(username, MONGO_DB, target_username)
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/social/like", methods=["POST"])
def like_post():
    """Like a post"""
    username = session.get("username", "")
    post_owner = request.json.get("postOwner")
    album_id = request.json.get("albumId")
    try:
        return social.like_post(username, MONGO_DB, post_owner, album_id)
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/social/unlike", methods=["POST"])
def unlike_post():
    """Unlike a post"""
    username = session.get("username", "")
    post_owner = request.json.get("postOwner")
    album_id = request.json.get("albumId")
    try:
        return social.unlike_post(username, MONGO_DB, post_owner, album_id)
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/social/users/search", methods=["GET"])
def search_users():
    """Search for users"""
    query = request.args.get("q", "")
    limit = request.args.get("limit", 10, type=int)
    try:
        return social.search_users(MONGO_DB, query, limit)
    except Exception as exc:
        print(exc)
        return str(exc), 500


@app.route("/api/social/users/<username>", methods=["GET"])
def get_user_profile_public(username):
    """Get public profile for any user"""
    current_user = session.get("username", "")
    try:
        return social.get_user_profile_public(MONGO_DB, username, current_user)
    except Exception as exc:
        print(exc)
        return str(exc), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
