from lib.spotify_helpers import clean_albums_data
from lib.spotipy_client import SpotipyClient


def spotify_search(request, client: SpotipyClient):
    query = request.args.get("q", "").strip()
    if not query:
        return []

    res = client.generic_search(query)
    album_items = res.get("albums", {}).get("items", [])
    track_items = res.get("tracks", {}).get("items", [])
    artist_items = res.get("artists", {}).get("items", [])

    track_albums = [t.get("album") for t in track_items if t.get("album")]

    artist_albums = []
    for artist in artist_items:
        artist_id = artist.get("id")
        if artist_id:
            artist_album_res = client.get_artist_albums(artist_id)
            artist_albums.extend(artist_album_res.get("items", []))

    all_albums = album_items + track_albums + artist_albums

    return clean_albums_data(all_albums, limit=10)
