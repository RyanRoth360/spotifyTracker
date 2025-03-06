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
        return self.check_authentication(sp)

    def check_authentication(self, sp):
        """Check if authentication is successful by fetching the user's Spotify profile."""
        try:
            user = sp.current_user()
            if user:
                return "", 200
            else:
                return "User profile not found", 404
        except Exception as exc:
            return str(exc), 500


    def get_playlist_tracks(self, id):
        """
        Fetch all tracks from a Spotify playlist.
        """
        tracks = []
        results = self.sp.playlist_tracks(id)
        
        while results:
            for item in results['items']:
                track = item['track']
                tracks.append(track['name'])
            
            results = sp.next(results)  
        
        return tracks
    
    def get_all_playlists(self):
        """Returns list of playlist names and ids"""
        try:
            playlists = self.sp.current_user_playlists()
            return [{'name' : playlist['name'], 'id': playlist['id']} for playlist in playlists['items']], 200
        except Exception:
            return [], 500
            

    def get_playlist_id(self, name):
        """Fetch playlist id via name"""
        playlists = self.sp.current_user_playlists()
        for playlist in playlists['items']:
            if name == playlist['name']:
                return playlist['id']


# if __name__ == "__main__":
#     sp = SpotipyClient()