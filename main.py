from src.search import SearchEngine
from src.interface import CLI
from src.login import fetch_token

import tekore as tk
import sys


def main():
    search = SearchEngine(client=spotify)

    main_menu = CLI().create_menu(
        title="Main Menu M3UKINATOR",
        entries={
            "Search Artist":search.search_artists,
            "Random Dutch Artist": search.search_dutch,
            "Search Song": search.search_song,
            "Settings": search.view_settings
        },
        return_label="Quit")


if __name__ == "__main__":
    token = fetch_token()
    spotify = tk.Spotify(token)
    if spotify:
        main()
    else:
        print("No Spotify Client ")
        sys.exit()

