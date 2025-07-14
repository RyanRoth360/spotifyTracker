from lib.spotipy_client import get_sp_client

def clean_albums_data(albums, limit=50):
    cleaned_albums = []
    for i, album in enumerate(albums):
        cleaned = {
            "name": album.get("name"),
            "albumId": album.get("id"),
            "release_date": album.get("release_date"),
            "artists": [artist["name"] for artist in album.get("artists", [])],
            "image": album["images"][0]["url"] if album.get("images") else None,
            "external_url": album.get("external_urls", {}).get("spotify"),
            "tracks": album.get("tracks", [])
        }
        cleaned_albums.append(cleaned)
        if i == limit:
            break
    return cleaned_albums


def add_album_data(data):
    """Populate album data from ids in profile"""
    sp = get_sp_client()  
    
    for album in data.get("albums", []):
        album.update(sp.get_album_data(album["albumId"]))
   