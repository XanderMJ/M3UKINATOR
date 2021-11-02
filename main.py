from client_info import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

import tekore as tk
from rich.console import Console
from simple_term_menu import TerminalMenu
import os,time,sys

desired_playlist = 'Heren Ver3tig'


def fetch_token():
    file = 'tekore.cfg'
    if os.path.isfile(file):
        conf = tk.config_from_file(file, return_refresh=True)
        token = tk.refresh_user_token(*conf[:2], conf[3])
    else:
        console.print(f"{file} not found, log-in to spotify and paste URL in commandline", style='bold red')
        conf = (CLIENT_ID,CLIENT_SECRET,REDIRECT_URI)
        token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
        tk.config_to_file(file, conf + (token.refresh_token,))
    return token

def search_songs(term, search_lim=50, max_search=1_000, max_followers=10_000, max_results=33):
    results = []
    offset_count = 0
    while offset_count < max_search:
        obj, = spotify.search(term, types=('track',), limit=search_lim, offset=offset_count)
        results.extend([ob for ob in obj.items])
        offset_count += search_lim
        if len(results) >= max_results:
            offset_count = 9e9
    return results

def search_artists(term, search_lim=50, max_search=1_000, max_followers=10_000, max_results=33):
    results = []
    offset_count = 0
    while offset_count < max_search:
        obj, = spotify.search(term, types=('artist',), limit=search_lim, offset=offset_count)
        results.extend([ob for ob in obj.items if (0 < ob.followers.total <= max_followers)])
        offset_count += search_lim
        if len(results) >= max_results:
            offset_count = 9e9
    return results

def show_artist_tracks(artist):
    tracks = spotify.artist_top_tracks(artist.id, 'from_token')
    if tracks:
        track_title = f"Top songs of {artist.name}!" 
        track_items = [track.name for track in tracks]
        track_exit = False
        track_items.append("<- Return")
        tracks_menu = TerminalMenu(
            menu_entries=track_items,
            title=track_title,
            cycle_cursor=True,
            clear_screen=False,
        )
        
        while not track_exit:
            track_sel = tracks_menu.show()
            if track_sel != (len(track_items)-1):
                player(tracks[track_sel], show_controls=True)
            else:
                track_exit = True
    else:
        console.print(f"No tracks found for {artist.name}", style='bold red')
        track_exit = True


def _result_formatter(results, type, offset=3):
    n = max([len(a.name) for a in results]) + offset

    if type == 'artist':
        m = max([len(str(a.followers.total)) for a in results]) +1
        formatted_list = [f"{result.name}{' '*(n-len(result.name))} Followers:{' '*(m-len(str(result.followers.total)))}{result.followers.total}  Genres: {[g for g in result.genres]}" for result in results]
    elif type =='track':
        formatted_list = [f"{result.name}{' '*(n-len(result.name))} Artist(s): {[a.name for a in result.artists ]}" for result in results]
    
    return formatted_list
    

def search_results(results, type):
    results_title = f"Showwing {len(results)} Search Results from the MEUKINATOR3!"
    result_items = _result_formatter(results, type=type)
    result_items.append("<- Return")
    result_exit = False
    result_menu = TerminalMenu(
        menu_entries=result_items,
        title=results_title,
        cycle_cursor=True,
        clear_screen=True,
    )

    while not result_exit:
        result_sel = result_menu.show()
        if result_sel != (len(result_items)-1):
            if type == 'artist':
                show_artist_tracks(results[result_sel])
            elif type == 'track':
                player(results[result_sel], show_controls=True)
        else:
            result_exit = True

def player(song, skip_s=15, show_controls=False):
    if not show_controls:
        spotify.playback_start_tracks([song.id])
    # console.print(f"Playing: {song.name}")
    elif show_controls:
        player_options = ["Play Now", "Add To Queue", f'Fast Forward ({skip_s}sec)',f'Rewind ({skip_s}sec)', '<- Return']
        player_exit = False
        player_menu = TerminalMenu(
            menu_entries = player_options,
            title = f"{song.name}",
            cycle_cursor=True,
            clear_screen=True,
        )

        while not player_exit:
            player_sel = player_menu.show()
            if player_sel == 0:
                spotify.playback_start_tracks([song.id])
                player_exit = True
            elif player_sel == 1:
                spotify.playback_queue_add(song.uri)
                player_exit = True
            elif player_sel == 2:
                progress = spotify.playback_currently_playing(tracks_only=True).progress_ms
                forward_ms = progress+int(skip_s)*1000
                spotify.playback_start_tracks([song.id], position_ms = forward_ms)
            elif player_sel == 3:
                progress = spotify.playback_currently_playing(tracks_only=True).progress_ms
                rewind_ms = progress - int(skip_s)*1000
                if rewind_ms < 0:
                    rewind_ms = 0
                spotify.playback_start_tracks([song.id], position_ms = rewind_ms)
            # elif player_sel == 2:
            #     spotify.playlist_add(playlist_id=playlist_id, uris=[song.uri])  #can not directly add to playlist if it is not yours
            elif player_sel == (len(player_options)-1):
                player_exit = True


def main():
    main_menu_title = "M3UKINATOR MENU\n"
    main_menu_items = ["Search Artist","Search Songs", "Settings", "Quit"]
    main_menu_exit = False
    main_menu = TerminalMenu(
        menu_entries=main_menu_items,
        title=main_menu_title,
        cycle_cursor=True,
        clear_screen=True,
    )

    edit_menu_title = "  Edit MEUK search parameters\n"
    edit_menu_items = ["Followers","Genres", "Back to Main Menu"]
    edit_menu_back = False
    edit_menu = TerminalMenu(
        edit_menu_items,
        title=edit_menu_title,
        cycle_cursor=True,
        clear_screen=True,
    )

    while not main_menu_exit:
        main_sel = main_menu.show()
        if main_sel == 0: #Search based on artist name
            search_term = input("Search for artist name: ")
            artists =  search_artists(search_term)
            search_results(artists, type='artist')

        elif main_sel == 1: #Search based on song name
            search_term = input("Search for nieuwe pokkoe:")
            songs = search_songs(search_term)
            search_results(songs, type='track')

        elif main_sel == 2: #Settings menu
            while not edit_menu_back:
                edit_sel = edit_menu.show()
                if edit_sel == 0:
                    print("Followers")
                    time.sleep(5)
                elif edit_sel == 1:
                    print("Genres" )
                    time.sleep(5)
                elif edit_sel == 2:
                    edit_menu_back = True
                    print("Back Selected")
            edit_menu_back = False
        elif main_sel == 3: #Quit
            main_menu_exit = True
            console.print("Shutting Down M3UKINATOR3", style='bold red')
            sys.exit()
    return


if __name__ == "__main__":
    console = Console()
    token = fetch_token()
    spotify = tk.Spotify(token)

    if spotify:
        user = spotify.current_user().id
        found = False
        n,m = 0,50
        while not found:
            playlists = spotify.playlists(user, limit=m, offset=n)
            for playlist in playlists.items:
                if playlist.name == desired_playlist:
                    playlist_id = playlist.id
                    console.print(f"Found playlist {playlist.name} with ID {playlist.id}", style='bold green')
                    found = True
                    time.sleep(1)
            n += m
            if n > 500:
                console.print("Could not find {desired_playlist}! ERROR BLIEP BLEIP", style='bold red')
                time.sleep(3)
                playlist_id = None
                found = True
        main()