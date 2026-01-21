from lib.spotify_helpers import clean_albums_data
from lib.spotipy_client import SpotipyClient
from datetime import datetime


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


def get_trending_albums(client: SpotipyClient):
    """Get albums from user's recently played tracks"""
    res = client.get_recently_played(limit=50)
    items = res.get("items", [])

    # Extract unique albums from recently played tracks
    albums_dict = {}
    for item in items:
        track = item.get("track")
        if track:
            album = track.get("album")
            if album and album.get("id"):
                # Use dict to avoid duplicates
                albums_dict[album["id"]] = album

                # Stop when we have 15 unique albums
                if len(albums_dict) >= 15:
                    break

    albums = list(albums_dict.values())
    return clean_albums_data(albums, limit=15)


def get_popular_albums(client: SpotipyClient):
    """Get popular albums by searching for popular terms"""
    popular_terms = ["top hits", "popular", "viral", "chart", "trending"]
    albums_dict = {}

    for term in popular_terms:
        try:
            res = client.generic_search(term, limit=5)
            album_items = res.get("albums", {}).get("items", [])

            for album in album_items:
                if album and album.get("id"):
                    # Use dict to avoid duplicates
                    albums_dict[album["id"]] = album

            # Stop if we have enough albums
            if len(albums_dict) >= 15:
                break
        except:
            continue

    # Convert to list and limit to 12
    albums = list(albums_dict.values())[:12]
    return clean_albums_data(albums, limit=12)
