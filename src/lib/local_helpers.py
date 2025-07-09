import json
from spotify_helpers import clean_albums_data

def write_data_from_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        albums = json.load(f)

    cleaned = clean_albums_data(albums)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    write_data_from_file("albums.json", "albums_clean.json")