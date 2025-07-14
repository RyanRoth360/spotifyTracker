from flask import Flask, jsonify, request
from lib.spotipy_client import SpotipyClient
from lib.pymongo_client import create_pymongo_client
from flask_cors import CORS

import routes.profile as profile
import routes.spotify as spotify

app = Flask(__name__)
from flask_cors import CORS

CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}},
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"],        
    allow_headers=["Content-Type", "Authorization"],  
)


CLIENT = SpotipyClient()

@app.route('/api/auth', methods=["POST"])
def auth():
    msg, status = CLIENT.authorize_user()
    return jsonify(msg), status

# USER DATA ENDPOINTS
@app.route('/api/profile/get/<username>', methods=["GET"])
def get_profile_data(username):
    """Return profile data given username"""
    mongo_db = create_pymongo_client("users")
    return profile.get_profile_data(mongo_db, username)

@app.route('/api/profile/update-flag/', methods=["POST"])
def update_album_flag():
    """Update favorites or bookmarked data"""
    mongo_db = create_pymongo_client("users")
    return profile.update_flag(mongo_db, request.json)

# SPOTIFY DATA ENDPOINTS
@app.route('/api/spotify/track-data/<album_id>', methods=["GET"])
def get_track_data(album_id):
    """Return track data given album id"""
    return spotify.get_track_data(album_id)
    
@app.route("/api/spotify/search", methods=["GET"])
def spotify_search():
    """Seach via album, artist, or track"""
    return spotify.spotify_search(request)
  

if __name__ == '__main__':
    app.run(debug=True)
