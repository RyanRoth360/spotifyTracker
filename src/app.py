import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, session
from flask_cors import CORS

from lib.enums import ReturnTypes, SpotifyClientNotAuthenticated
from lib.pymongo_client import create_pymongo_client
from lib.spotipy_client import create_spotify_client
from routes import profile, spotify

app = Flask(__name__)
CORS(app)

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
    return redirect("http://localhost:3000/")


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
@app.route("/api/get-profile", methods=["GET"])
def get_profile_data():
    """Return profile data and status code given username"""
    client, token_info = create_spotify_client(session.get("token_info"))
    if token_info:
        session["token_info"] = token_info
    username = session.get("username", "")
    try:
        return profile.get_profile_data(username, MONGO_DB, client)
    except SpotifyClientNotAuthenticated:
        return ReturnTypes.UserNotAuthenticated, 401
    except Exception as exc:
        return str(exc), 500


@app.route("/api/profile/update-flag", methods=["POST"])
def update_favorite_or_bookmarked():
    username = session.get("username", "")
    try:
        return profile.update_favorite_or_bookmarked(MONGO_DB, username, request.json)
    except Exception as exc:
        print(exc)
        return "Server error", 500


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
