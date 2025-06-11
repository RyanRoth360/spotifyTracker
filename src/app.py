from flask import Flask, jsonify
from lib.spotipy_client import SpotipyClient
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

CLIENT = SpotipyClient()

@app.route('/api/auth', methods=["POST"])
def auth():
    msg, status = CLIENT.authorize_user()
    return jsonify(msg), status

@app.route('/api/playlists', methods=["GET"])
def get_all_playlists():
    result, status = CLIENT.get_all_playlists()
    return jsonify(result), status

from flask import request, jsonify

@app.route('/api/songs', methods=["GET"])
def get_all_songs():
    try:
        CLIENT.authorize_user()
        playlist_id = request.args.get('id')

        if not playlist_id:
            return jsonify({"error": "Playlist ID is required"}), 400  # Return error if ID is missing

        result, status = CLIENT.get_all_songs(playlist_id)
        return jsonify(result), status
    except Exception as e:
        return str(e), 500



if __name__ == '__main__':
    app.run(debug=True)
