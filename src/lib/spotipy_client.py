from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotipyClient():
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.scope = os.getenv("SCOPE")
        self.sp = ""


    def authorize_user(self):
        """Authorize user and return a Spotify client."""
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.client_id,
                                                    client_secret=self.client_secret,
                                                    redirect_uri=self.redirect_uri,
                                                    scope=self.scope))
        result, status = self.check_authentication(sp)
        if status == 200:
            self.sp = sp
        return result, status

    def check_authentication(self, sp):
        """Check if authentication is successful by fetching the user's Spotify profile."""
        try:
            user = sp.current_user()
            if user:

                return user, 200
            else:
                return "User profile not found", 404
        except Exception as exc:
            return str(exc), 500


    def get_all_songs(self, id):
        """
        Fetch all tracks from a Spotify playlist, including the date they were added.
        """
        tracks = []
        results = self.sp.playlist_tracks(id)

        while results:
            for item in results['items']:
                song = item['track']
                artist_str = ', '.join([artist['name'] for artist in song['artists']])
                img_url = song['album']['images'][0]['url'] if song['album']['images'] else ""
                date_added = item['added_at']
                tracks.append({
                    "title": song['name'],
                    "artist": artist_str,
                    "image_url": img_url,
                    "date_added": date_added
                })

            results = self.sp.next(results)

        return tracks, 200



    def get_all_playlists(self):
        """Returns list of playlist names and ids"""
        try:
            playlists = self.sp.current_user_playlists()
            playlist_data = []
            for playlist in playlists['items']:
                img_url = playlist['images'][0]['url'] if playlist['images'] else ""
                playlist_data.append({
                    'name': playlist['name'],
                    'id': playlist['id'],
                    'image_url': img_url
                })
            return playlist_data, 200

        except Exception as exc:
            print(exc)
            return [], 500


    def get_playlist_id(self, name):
        """Fetch playlist id via name"""
        playlists = self.sp.current_user_playlists()
        for playlist in playlists['items']:
            if name == playlist['name']:
                return playlist['id']


    def search_album(self, album):
        results = self.sp.search(q=album, type="album", limit=10)
        print(results)
        return results


if __name__ == "__main__":
    sp = SpotipyClient()
    sp.authorize_user()
    r = sp.search_album('Dark Side of the Moon')
    print(r)