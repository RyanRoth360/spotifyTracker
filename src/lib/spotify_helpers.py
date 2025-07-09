
def clean_albums_data(albums):
    cleaned_albums = []
    for album in albums:
        cleaned = {
            "name": album.get("name"),
            "id": album.get("id"),
            "release_date": album.get("release_date"),
            "artist": album["artists"][0]["name"] if album.get("artists") else None,
            "image": album["images"][0]["url"] if album.get("images") else None,
            "external_url": album.get("external_urls", {}).get("spotify"),
            "tracks": album.get("tracks", [])
        }
        cleaned_albums.append(cleaned)
    return cleaned_albums
