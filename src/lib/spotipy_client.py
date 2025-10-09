# spotify_client.py
import json
import os
import time

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from lib.enums import SpotifyClientNotAuthenticated


def create_spotify_client(token_info=None):
    """Return a new spotify client class instance,
    authenticate client if token_info is passed in"""
    client = SpotipyClient()
    tokens = None
    if token_info:
        tokens = client.refresh_token(token_info)
    return client, tokens


class SpotipyClient:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.scope = os.getenv("SCOPE")
        self.auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_handler=None,  # disable default cache system
        )
        self.sp = None

    # AUTHORIZATION FUNCTIONS
    def get_auth_url(self):
        """Return URL to UI to authenticate Spotify"""
        return self.auth_manager.get_authorize_url()

    def get_token_from_auth_code(self, auth_code: str):
        """Return token info from authorization code"""
        token_info = self.auth_manager.get_access_token(auth_code, as_dict=True)
        return {
            "access_token": token_info["access_token"],
            "refresh_token": token_info["refresh_token"],
            "expires_at": token_info["expires_at"],
        }

    def refresh_token(self, token_info):
        """Check if token is expired, if so refresh it"""
        if token_info["expires_at"] - int(time.time()) < 60:
            refreshed = self.auth_manager.refresh_access_token(
                token_info["refresh_token"]
            )
            token_info["access_token"] = refreshed["access_token"]
            token_info["expires_at"] = refreshed["expires_at"]

        self.sp = spotipy.Spotify(auth=token_info["access_token"])
        return token_info

    def _check_authentication(self):
        if not self.sp:
            raise SpotifyClientNotAuthenticated()

    # PUBLIC METHODS
    def get_username(self):
        self._check_authentication()
        return self.sp.current_user()

    def get_album_data(self, album_id):
        """Return album data given an album id"""
        self._check_authentication()
        album = self.sp.album(album_id)
        cover_url = album.get("images", [{}])[0].get("url")
        return {
            "name": album["name"],
            "release_date": album["release_date"],
            "artists": [a["name"] for a in album.get("artists", [])],
            "image": cover_url,
            "external_url": album.get("external_urls", {}).get("spotify"),
        }

    def get_track_data(self, album_id):
        """Return track data given an album id"""
        self._check_authentication()
        results = self.sp.album_tracks(album_id, limit=50)
        tracks = []

        for item in results.get("items", []):
            tracks.append(
                {
                    "name": item.get("name"),
                    "id": item.get("id"),
                    "duration_ms": item.get("duration_ms"),
                    "track_number": item.get("track_number"),
                    "preview_url": item.get("preview_url"),
                    "artists": [a.get("name") for a in item.get("artists", [])],
                }
            )
        return tracks

    def generic_search(self, query, limit=10):
        self._check_authentication()
        return self.sp.search(q=query, type="album,track,artist", limit=limit)

    def get_artist_albums(self, artist_id, limit=10):
        self._check_authentication()
        return self.sp.artist_albums(artist_id, album_type="album", limit=limit)

    # def search_album(self, album_query):
    #     self._check_authentication()
    #     return self.sp.search(q=album_query, type="album", limit=10)

    # def get_all_songs(self, playlist_id):
    #     self._require_client()
    #     tracks = []
    #     results = self.get_client().playlist_tracks(playlist_id)
    #     while results:
    #         for item in results["items"]:
    #             track = item["track"]
    #             artist_str = ", ".join(a["name"] for a in track["artists"])
    #             img_url = (
    #                 track["album"]["images"][0]["url"]
    #                 if track["album"]["images"]
    #                 else ""
    #             )
    #             tracks.append(
    #                 {
    #                     "title": track["name"],
    #                     "artist": artist_str,
    #                     "image_url": img_url,
    #                     "date_added": item["added_at"],
    #                 }
    #             )
    #         results = self.get_client().next(results)
    #     return tracks, 200

    # def get_all_playlists(self):
    #     self._require_client()
    #     try:
    #         playlists = self.get_client().current_user_playlists()
    #         data = []
    #         for p in playlists["items"]:
    #             img_url = p["images"][0]["url"] if p["images"] else ""
    #             data.append({"name": p["name"], "id": p["id"], "image_url": img_url})
    #         return data, 200
    #     except Exception:
    #         return [], 500

    # def get_playlist_id(self, name):
    #     playlists = self.get_client().current_user_playlists()
    #     return next((p["id"] for p in playlists["items"] if p["name"] == name), None)

    # def get_top_albums(self, count=15):
    #     results = self.get_client().new_releases(limit=count)["albums"]["items"]
    #     for album in results:
    #         album["tracks"] = self.get_tracklist(album["id"])
    #     with open("albums.json", "w", encoding="utf-8") as fp:
    #         json.dump(results, fp, ensure_ascii=False, indent=2)
    #     return results


if __name__ == "__main__":
    client1 = SpotipyClient()
    user, status = client1.authorize_user()
    print("First auth:", status)

    client2 = SpotipyClient()
    user2, status2 = client2.authorize_user()
    print("Second auth:", status2)

    print(client1.sp is client2.sp)  # → False now
