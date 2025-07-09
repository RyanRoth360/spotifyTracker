from flask import Flask, jsonify
from lib.spotipy_client import SpotipyClient
from lib.pymongo_client import create_pymongo_client
from flask_cors import CORS

import routes.profile as profile
import routes.spotify as spotify

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

CLIENT = SpotipyClient()

@app.route('/api/auth', methods=["POST"])
def auth():
    msg, status = CLIENT.authorize_user()
    return jsonify(msg), status

# @app.route('/api/playlists', methods=["GET"])
# def get_all_playlists():
#     result, status = CLIENT.get_all_playlists()
#     return jsonify(result), status

# from flask import request, jsonify

# @app.route('/api/songs', methods=["GET"])
# def get_all_songs():
#     try:
#         CLIENT.authorize_user()
#         playlist_id = request.args.get('id')

#         if not playlist_id:
#             return jsonify({"error": "Playlist ID is required"}), 400 

#         result, status = CLIENT.get_all_songs(playlist_id)
#         return jsonify(result), status
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/api/profile/get/<username>', methods=["GET"])
def get_profile_data(username):
    """Return profile data given username"""
    mongo_db = create_pymongo_client("users")
    return profile.get_profile_data(mongo_db, username)

@app.route('/api/spotify/get/<album_id>', methods=["GET"])
def get_album_data(album_id):
    """Return album data given album id"""
    mongo_db = create_pymongo_client("albums")
    return spotify.get_album_data(mongo_db, album_id)
    


if __name__ == '__main__':
    app.run(debug=True)
