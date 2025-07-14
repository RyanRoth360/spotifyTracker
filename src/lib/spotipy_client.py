# spotify_client.py
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json


def get_sp_client():
    """Factory helper: always returns a SpotipyClient that
    already points at the shared (authorized) Spotipy object
    if one exists."""
    return SpotipyClient()


class SpotipyClient:
    """
    Wrapper around Spotipy with a class‑level cache so all
    instances share the same underlying Spotify client once
    the user has authenticated.
    """
    _shared_sp: spotipy.Spotify | None = None  # <-- class variable

    def __init__(self):
        load_dotenv()

        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.scope = os.getenv("SCOPE")

        # If a client was already authorized earlier, reuse it
        self.sp: spotipy.Spotify | None = SpotipyClient._shared_sp

    # ------------------------------------------------------------------ #
    #  Authorization helpers
    # ------------------------------------------------------------------ #
    def authorize_user(self):
        """
        Authorize once and cache the Spotipy client at class level.
        Subsequent instances will skip the OAuth flow.
        """
        if SpotipyClient._shared_sp:                      # already authorized
            self.sp = SpotipyClient._shared_sp
            user, status = self._check_authentication(self.sp)
            return user, status

        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        user, status = self._check_authentication(sp)
        if status == 200:                                # success → cache it
            SpotipyClient._shared_sp = sp
            self.sp = sp
        return user, status

    @staticmethod
    def _check_authentication(sp):
        """Verify we really have a valid token by fetching the user profile."""
        try:
            user = sp.current_user()
            return (user or "User profile not found"), 200 if user else 404
        except Exception as exc:
            return str(exc), 500

    # ------------------------------------------------------------------ #
    #  Spotify data helpers
    # ------------------------------------------------------------------ #
    def _require_client(self):
        if not self.sp:
            raise RuntimeError("Spotify client not authorized. Call authorize_user() first.")

    def get_all_songs(self, playlist_id):
        self._require_client()

        tracks = []
        results = self.sp.playlist_tracks(playlist_id)

        while results:
            for item in results["items"]:
                track = item["track"]
                artist_str = ", ".join(a["name"] for a in track["artists"])
                img_url = track["album"]["images"][0]["url"] if track["album"]["images"] else ""
                tracks.append(
                    {
                        "title": track["name"],
                        "artist": artist_str,
                        "image_url": img_url,
                        "date_added": item["added_at"],
                    }
                )
            results = self.sp.next(results)
        return tracks, 200

    def get_all_playlists(self):
        self._require_client()

        try:
            playlists = self.sp.current_user_playlists()
            data = []
            for p in playlists["items"]:
                img_url = p["images"][0]["url"] if p["images"] else ""
                data.append({"name": p["name"], "id": p["id"], "image_url": img_url})
            return data, 200
        except Exception as exc:
            return [], 500

    def get_playlist_id(self, name):
        self._require_client()

        playlists = self.sp.current_user_playlists()
        return next((p["id"] for p in playlists["items"] if p["name"] == name), None)

    def search_album(self, album_query):
        self._require_client()
        return self.sp.search(q=album_query, type="album", limit=10)
    
    def generic_search(self, query, limit=10):
        self._require_client()
        return self.sp.search(q=query, type="album,track,artist", limit=limit)
    
    def get_artist_albums(self, artist_id, limit=5):
        self._require_client()
        return self.sp.artist_albums(artist_id, album_type="album", limit=limit)


    def get_top_albums(self, count=15):
        self._require_client()

        results = self.sp.new_releases(limit=count)["albums"]["items"]
        for album in results:
            album["tracks"] = self.get_tracklist(album["id"])
        with open("albums.json", "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)
        return results

    def get_album_data(self, album_id):
        self._require_client()
        album = self.sp.album(album_id)
        
        cover_url = album.get("images", [{}])[0].get("url")
        return {
            "name": album["name"],
            "release_date": album["release_date"],
            "artists": [a["name"] for a in album.get("artists", [])],
            "image": cover_url,
            "external_url": album.get("external_urls", {}).get("spotify")
        }
        
    def get_track_data(self, album_id):
        self._require_client()
        
        tracks = []
        results = self.sp.album_tracks(album_id, limit=50)
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


# ---------------------------------------------------------------------- #
#  Demo / manual test
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    client1 = SpotipyClient()
    user, status = client1.authorize_user()
    print("First auth:", status)

    # Second instance reuses the token — no OAuth prompt
    client2 = SpotipyClient()
    user2, status2 = client2.authorize_user()
    print("Second auth:", status2)

    # Verify both clients point to the same underlying Spotipy object
    print(client1.sp is client2.sp)  # → True
