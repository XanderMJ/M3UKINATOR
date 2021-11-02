from client_info import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


import tekore as tk
from rich.console import Console
from simple_term_menu import TerminalMenu
import os
import time
import sys

def fetch_token():
    file = 'tekore.cfg'
    if os.path.isfile(file):
        # print(f"{file} found!")
        conf = tk.config_from_file(file, return_refresh=True)
        token = tk.refresh_user_token(*conf[:2], conf[3])
    else:
        print(f"{file} not found, log-in to spotify and paste URL")
        conf = (CLIENT_ID,CLIENT_SECRET,REDIRECT_URI)
        token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
        tk.config_to_file(file, conf + (token.refresh_token,))
    return token



# def artist_search(name, search_lim=5):
#     print(f"searching for artist {name}")
#     artists_object, = spotify.search(name, types=('artist',), limit=search_lim)

#     options = [artist.name for artist in artists_object]

#     for artist in artists_object.items:
#         display_artist(artist, search_top_songs=True)
#     return



# def display_artist(artist, search_top_songs):
#     console.print(f"Artist name: [bold red]{artist.name}[/bold red]")

#     if search_top_songs:
#         tracks = spotify.artist_top_tracks(artist.id, 'from_token')
#         for track in tracks:
#             print(track)
#             console.print(f"track: [link={track.href}]{track.name}[/link]")


#     return


def search_artists(term, search_lim=5):
    obj, = spotify.search(term, types=('artist',), limit=search_lim)
    return obj

def show_indu(artist):
    tracks = spotify.artist_top_tracks(artist.id, 'from_token')
    track_title = f"Top songs of {artist.name}!" 
    track_items = [track.name for track in tracks]
    track_cursor = "> "
    track_cursor_style = ("fg_red", "bold")
    track_style = ("bg_red", "fg_yellow")
    track_exit = False

    tracks_menu = TerminalMenu(
        menu_entries=track_items,
        title=track_title,
        menu_cursor=track_cursor,
        menu_cursor_style=track_cursor_style,
        menu_highlight_style=track_style,
        cycle_cursor=True,
        clear_screen=True,
    )
    
    while not track_exit:
        track_sel = tracks_menu.show()


        spotify.playback_start_tracks([tracks[track_sel].id])
        # time.sleep(5)
        track_exit = True



def search_results(results):
    results_title = "Search Results from the MEUKINATOR3"
    result_items = [result.name for result in results.items]
    result_cursor = "> "
    result_cursor_style = ("fg_red", "bold")
    result_style = ("bg_red", "fg_yellow")
    result_exit = False

    result_menu = TerminalMenu(
        menu_entries=result_items,
        title=results_title,
        menu_cursor=result_cursor,
        menu_cursor_style=result_cursor_style,
        menu_highlight_style=result_style,
        cycle_cursor=True,
        clear_screen=True,
    )

    while not result_exit:
        result_sel = result_menu.show()
        show_indu(results.items[result_sel])
        # print(result_sel)
        # print(results.items[result_sel])
        # time.sleep(3)
        result_exit = True




    # return result_menu


def main():
    console.print(f"Welcome {str(spotify.current_user().display_name).upper()} to [bold green]SpotiMeuk[/bold green]")

    main_menu_title = " SpotiyMeuk Main Menu\n"
    main_menu_items = ["Search!", "Settings", "Quit"]
    main_menu_cursor = "> "
    main_menu_cursor_style = ("fg_red", "bold")
    main_menu_style = ("bg_red", "fg_yellow")
    main_menu_exit = False

    main_menu = TerminalMenu(
        menu_entries=main_menu_items,
        title=main_menu_title,
        menu_cursor=main_menu_cursor,
        menu_cursor_style=main_menu_cursor_style,
        menu_highlight_style=main_menu_style,
        cycle_cursor=True,
        clear_screen=True,
    )

    search_menu_title = "  Search MEUK! based on:"
    search_menu_items = ["Artist" , "Album", "Song", "Back to Main Menu"]
    search_menu_back = False
    search_menu = TerminalMenu(
        search_menu_items,
        title=search_menu_title,
        menu_cursor=main_menu_cursor,
        menu_cursor_style=main_menu_cursor_style,
        menu_highlight_style=main_menu_style,
        cycle_cursor=True,
        clear_screen=True,
    )

    edit_menu_title = "  Edit MEUK search parameters\n"
    edit_menu_items = ["Followers","Genres", "Back to Main Menu"]
    edit_menu_back = False
    edit_menu = TerminalMenu(
        edit_menu_items,
        title=edit_menu_title,
        menu_cursor=main_menu_cursor,
        menu_cursor_style=main_menu_cursor_style,
        menu_highlight_style=main_menu_style,
        cycle_cursor=True,
        clear_screen=True,
    )

    while not main_menu_exit:
        main_sel = main_menu.show()
        if main_sel == 0:
            while not search_menu_back:
                search_sel = search_menu.show()
                if search_sel == 0:
                    search_term = input("Search for artist name: ")
                    artists =  search_artists(search_term)
                    search_results(artists)
                    # res_menu.show()
                elif search_sel == 1:
                    print("Albums Not Implemented Yet" )
                    # time.sleep(5)
                    search_menu_back = True
                elif search_sel == 2:
                    print("Songs Not Implemented Yet" )
                    # time.sleep(5)
                    search_menu_back = True
                elif search_sel == 3:
                    search_menu_back = True
                    print("Back Selected")
            search_menu_back = False
        elif main_sel == 1:
            while not edit_menu_back:
                edit_sel = edit_menu.show()
                if edit_sel == 0:
                    print("Followers")
                    time.sleep(5)
                elif edit_sel == 1:
                    print("SGenres" )
                    time.sleep(5)
                elif edit_sel == 2:
                    edit_menu_back = True
                    print("Back Selected")
            edit_menu_back = False
        elif main_sel == 2:
            main_menu_exit = True
            print("Quit Selected")
            sys.exit()
    return


if __name__ == "__main__":
    console = Console()
    token = fetch_token()
    spotify = tk.Spotify(token)

    if spotify:
        main()