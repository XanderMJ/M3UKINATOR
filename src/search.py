import configparser
import os
import time
import cld3

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
            if filter_language != ('all' or ''):
                filtered = self._filter_language(reduced_artists, filter_language)
                return filtered
            else:
                for artist in reduced_artists:
                    artist.language = 'all'
                return reduced_artists
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
                    artist.language = detection.language
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
        if search_term != '':
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
                self.show_artist_top_songs(artist, entities, search_term)

        
 

    def show_artist_top_songs(self,artist,entities,search_term):
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
            self.player(song)
            self.show_artist_top_songs(artist, entities, search_term)
        else:
            #go back to previous search result dit moet anders! nu quick fix
            # pass    
            formatted_response = self._result_formatter(entities)
            empty = [None]*len(formatted_response)
            artist_selection = CLI().create_menu( 
                title = f" M3UKINATOR Result {len(entities) }for {search_term}:",
                entries=dict(zip(formatted_response,empty)),
                args=True
            )

            if artist_selection != None:
                artist = entities[artist_selection]
                self.show_artist_top_songs(artist, entities, search_term)
        


    ## All definitions related to Song search
    def _format_song_title(self, results, offset=3,m=60):
        n = max([len(a.name) for a in results]) + offset
        if n>m: n=m
        formatted = [f"{i}) Bpm:{' '*(4-len(str(result.tempo)))}{result.tempo}, Title:{result.name}{' '*(n-len(result.name))},{[a.name for a in result.artists]}" 
                    for (i,result) in enumerate(results)]
        return formatted

    def _add_song_metadata(self, song_list):
        song_id = [song.id for song in song_list]
        metadata = self.client.tracks_audio_features(song_id)
        for song,meta in zip(song_list, metadata):
            if meta is None:
                song.tempo, song.danceability, song.energy, song.instrumentalness, song.speechiness = None,None,None,None,None
            else:
                song.tempo = int(meta.tempo)                    #bmp
                song.danceability = meta.danceability           #dancing 0=bad 1=good
                song.energy = meta.energy                       #loudness, noise
                song.instrumentalness = meta.instrumentalness   # 0=no vocals
                song.speechiness = meta.speechiness             # <0.33 no speech 0.33<0.66 speech and music >0.66 only spoken
        return song_list

    def search_song(self, search=None,data=None):
        if search is None:
            result_limit = self.settings.get('result_limit')
            result_offset = self.settings.get('result_offset')
            max_search = self.settings.get('max_search_n')
            entities = []
            search_term = input("Song Name:")
            if search_term != '':
                while not (len(entities) >= int(result_limit) or int(result_offset)>=int(max_search)):
                    search_results, *_ = self.client.search(
                        query=search_term,
                        types=('track',),
                        market='from_token',
                        limit=result_limit,
                        offset=result_offset
                        )
                    result_offset += result_limit

                    if search_results:
                        songs = [result for result in search_results.items]  #reduce data
                        songs_metadata = self._add_song_metadata(songs)
                        entities.extend(songs_metadata)

                    else:
                        break
        else:
            entities = data
            search_term = search

        song_strs = self._format_song_title(entities)
        empty = [None]*len(entities)

        items = dict(zip(song_strs, empty))
        songs_view = CLI().create_menu(
            title=f"M3UL Songs for {search_term}:",
            entries=items,
            args=True,
        )

        if songs_view != None:
            self.player(entities[songs_view])
            self.search_song(search_term,entities)                



    # Player model, should not be in this class...

    def player(self, track):
        adv_player = str(self.settings.get('advanced_player'))

        if adv_player.lower() == 'yes':
            player_menu = CLI().create_menu(
                title = "Player Menu",
                entries={
                    "Play":None,
                    "Queue":None
                    },
                    args=True   
            )
            if player_menu == 0:
                self.client.playback_start_tracks([track.id])
            elif player_menu == 1:
                self.client.playback_queue_add(track.uri)
        else:
            self.client.playback_start_tracks([track.id])



