from flask import Flask, jsonify
from lib.spotipy_client import SpotipyClient

app = Flask(__name__)
CLIENT = SpotipyClient()

@app.route('/api/auth')
def auth():
    msg, status = CLIENT.authorize_user()
    return jsonify(msg), status

@app.route('/api/playlists', methods=["GET"])
def auth():
    result, status = CLIENT.get_all_playlists()
    return jsonify(result), status


if __name__ == '__main__':
    app.run(debug=True)  
