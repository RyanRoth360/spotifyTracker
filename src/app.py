import os
from flask import Flask, jsonify, request, session, redirect
from lib.spotipy_client import SpotipyClient
from lib.pymongo_client import create_pymongo_client
from flask_cors import CORS
from dotenv import load_dotenv

import routes.profile as profile
import routes.spotify as spotify

app = Flask(__name__)
CORS(app)

# LOAD SECRET KEY
load_dotenv()
app.secret_key = os.getenv("SECRET_APP_KEY")

CLIENT = SpotipyClient()


# AUTH FLOW
@app.route("/api/login", methods=["GET"])
def login():
    return jsonify({"auth_url": CLIENT.get_auth_url()}), 200

# Spotify calls this after oauth
@app.route("/callback")
def callback():
    print("callback")
    code = request.args.get("code")
    token_data = CLIENT.save_token_from_code(code)
    session["token_info"] = token_data
    # redirect back to your single-page app (React root)
    return redirect("http://localhost:3000/") 

# Called after refresh is triggered in the UI
@app.route("/api/me", methods=["GET"])
def me():
    # Check if the user has a valid token in the session
    token_info = session.get("token_info")
    sp = CLIENT.get_spotify_client(token_info)
    if not sp:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        user = sp.current_user()  # Fetch Spotify profile
        return jsonify(user), 200
    except Exception:
        return jsonify({"error": "Failed to fetch user info"}), 500
    
    
def get_spotify_client():
    token_info = session.get("token_info")
    if not token_info:
        raise ValueError("No token info")
    return CLIENT.get_spotify_client(token_info)

    
# USER DATA ENDPOINTS
@app.route('/api/profile/get/<username>', methods=["GET"])
def get_profile_data(username):
    """Return profile data given username"""
    sp = get_spotify_client()
    mongo_db = create_pymongo_client("users") 
    return profile.get_profile_data(username, mongo_db, CLIENT, sp)

@app.route('/api/profile/update-flag/', methods=["POST"])
def update_album_flag():
    """Update favorites or bookmarked data"""
    mongo_db = create_pymongo_client("users")
    return profile.update_flag(mongo_db, request.json)

# SPOTIFY DATA ENDPOINTS
@app.route('/api/spotify/track-data/<album_id>', methods=["GET"])
def get_track_data(album_id):
    """Return track data given album id"""
    sp = get_spotify_client()
    return CLIENT.get_track_data(album_id, sp)
    
@app.route("/api/spotify/search", methods=["GET"])
def spotify_search():
    """Seach via album, artist, or track"""
    sp = get_spotify_client()
    return spotify.spotify_search(request, sp)
  

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)
