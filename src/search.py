import configparser
import os
import time
import cld3
from main import search_artists, search_songs


from src.interface import CLI

class SearchEngine:

    def __init__(self, client, file="settings.ini"):
        self.client = client
        self.file = file
        self.settings = self._get_settings()

    ### All methods related to setting menu

    def _get_settings(self):
        """get search settings from the 'setting.ini' file"""

        if not os.path.isfile(self.file):
            print("Please make sure the 'settings.cfg' file is located in the main directory")
            return None
        else:
            config = configparser.ConfigParser()
            config.read(self.file)
            return config._sections['search settings'] 

    def _set_settings(self,item,val):
        """set a new config value from the settings menu"""

        new_value = input(f"Change value for {item}, current={val}:")
        if new_value != '':                                                # quick and dirty 
            config = configparser.ConfigParser()
            config.read(self.file)
            config.set('search settings', item, new_value)
            with open(self.file, 'w') as cfgfile:                           # write new value to file
                config.write(cfgfile)
            self.settings = self._get_settings()                            # update the values, get from file
        self.view_settings()                                                # set viewport back to setting screen

    def view_settings(self):
        items, values = zip(*self.settings.items())
        menu_selection = CLI().create_menu(
                            title="Settings Menu",
                            entries=dict(zip(items,values)),
                            args=True
        )
        if menu_selection != None:
            item,val = items[menu_selection],values[menu_selection]
            self._set_settings(item,val)      
        return


    ## All definitions related to Artist Search

    def _filter_artist(self, results):
        follow_filter = int(self.settings.get('followers'))
        if isinstance(follow_filter, int):
            reduced_artists = [artist for artist in results if artist.followers.total <= follow_filter]

            filter_language = str(self.settings.get('song_language'))
            if filter_language != (None or ''):
                filtered = self._filter_language(reduced_artists, filter_language)
                return filtered
        else:
            print("Follow filter is not `type(int)`")
            return results

    def _filter_language(self, results, target_language):
        r = []
        for artist in results:

            top_songs = self.client.artist_top_tracks(artist_id=artist.id, market='from_token')
            add = False
            for song in top_songs:
                detection = cld3.get_language(song.name)
                if detection.language == target_language:
                    # print('Detected:', detection.language)
                    add = True
                    artist.language = 'nl'
            if add:
                r.append(artist)
        return r

    def _result_formatter(self, results, offset=3):
        n = max([len(a.name) for a in results]) + offset
        m = max([len(str(a.followers.total)) for a in results]) +1
        return [f"{result.language}:{result.name}{' '*(n-len(result.name))} Followers:{' '*(m-len(str(result.followers.total)))}{result.followers.total}" for result in results]
    

    def search_artist(self):
        result_limit = self.settings.get('result_limit')
        result_offset = self.settings.get('result_offset')
        max_search = self.settings.get('max_search_n')
        entities = []

        search_term = input("Artist Name:")

        while not (len(entities) > int(result_limit) or int(result_offset)>int(max_search)):
            search_results, *_ = self.client.search(
                query=search_term, 
                types=('artist',),
                market='from_token',
                limit=result_limit,
                offset=result_offset
                )

            # Should add a check on 404 response
            filtered_search_results = self._filter_artist(results=search_results.items)
            entities.extend(item for item in filtered_search_results)
            result_offset += result_limit

        formatted_response = self._result_formatter(entities)
        empty = [None]*len(formatted_response)

        artist_selection = CLI().create_menu( 
            title = f" M3UKINATOR Result {len(entities) }for {search_term}:",
            entries=dict(zip(formatted_response,empty)),
            args=True
        )

        if artist_selection != None:
            artist = entities[artist_selection]
            self.show_artist_top_songs(artist)
 

    def show_artist_top_songs(self,artist):
        top_songs = self.client.artist_top_tracks(artist_id=artist.id, market='from_token')
        songs = [song.name for song in top_songs]
        empty = [None]*len(songs)

        song_selection = CLI().create_menu(
            title=f" Top Songs for {artist.name}:",
            entries=dict(zip(songs, empty)),
            args=True
        )

        if song_selection != None:
            song = top_songs[song_selection]
            # print(song.id)
            self.player(song.id)
            self.show_artist_top_songs(artist)    
        

    def player(self, track_id):
        self.client.playback_start_tracks([track_id])

    ## All definitions related to Song search

    def search_song(self):
        search_term = input("Song Name:")
        print(f"Improved Song Searching comming SOON, returning in 3seconds")
        time.sleep(3)
        return


