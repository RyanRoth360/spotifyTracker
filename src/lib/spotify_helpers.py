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
            "tracks": album.get("tracks", []),
        }
        cleaned_albums.append(cleaned)
        if i == limit:
            break
    return cleaned_albums
