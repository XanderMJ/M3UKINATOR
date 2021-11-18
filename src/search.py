import configparser
import os
import time
import cld3
import numpy as np

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
        language_confidance = int(self.settings.get('language_confidance'))/100.0
        if isinstance(follow_filter, int):
            reduced_artists = [artist for artist in results if artist.followers.total <= follow_filter]

            filter_language = str(self.settings.get('song_language'))
            if filter_language != ('all' or ''):
                filtered = self._filter_language(reduced_artists, filter_language, language_confidance)
                return filtered
            else:
                for artist in reduced_artists:
                    artist.language = 'all'
                return reduced_artists
        else:
            print("Follow filter is not `type(int)`")
            return results

    def _filter_language(self, results, target_language, language_conf=None):
        r = []

        for artist in results:
            lang_confs = []
            add = False

            top_songs = self.client.artist_top_tracks(artist_id=artist.id, market='from_token')
            
            for song in top_songs:
                detection = cld3.get_language(song.name)
                if detection.language == target_language:
                    if language_conf:
                        lang_confs.append(float(detection.probability))
                        add = True
                    else:
                        add = True
                        
                    artist.language = detection.language
                    
            if add:
                artist.language = target_language
                artist.language_prob = str(np.round(np.mean(lang_confs)*100,1))
                r.append(artist)
        return r

    def _result_formatter(self, results, offset=3):
        n = max([len(a.name) for a in results]) + offset
        m = max([len(str(a.followers.total)) for a in results]) +1
        return [f"{' '*(5-len(str(result.language_prob)))}{result.language_prob}% {result.language}: {result.name}{' '*(n-len(result.name))} Followers:{' '*(m-len(str(result.followers.total)))}{result.followers.total}" for result in results]
    

    def search_artist(self):
        result_limit = int(self.settings.get('result_limit'))
        result_offset = int(self.settings.get('result_offset'))
        max_search = int(self.settings.get('max_search_n'))
        entities = []

        if result_limit > 50: #dirty fix for querry overloading
            result_limit = 50

        search_term = input("Artist Name:")
        if search_term != '':
            while not (len(entities) > int(result_limit) or int(result_offset)>=int(max_search)):
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

                n_items = len(search_results.items)   
                if n_items < int(result_limit):
                    #No full querry result, end search
                    result_offset = max_search +1
                else:
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
        songs = [f"{song.album.release_date[:4]}: {song.name}" for song in top_songs]
        empty = [None]*len(songs)

        song_selection = CLI().create_menu(
            title=f" Top Songs for {artist.name}:",
            entries=dict(zip(songs, empty)),
            args=True
        )

        if song_selection != None:
            song = top_songs[song_selection]
            self.player(song)
            self.show_artist_top_songs(artist, entities, search_term)
        else:
            #go back to previous search result dit moet anders! nu quick fix  
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
        formatted = [f"{' '*(2-len(str(i)))}{i}) Y:{str(result.album.release_date)[:4]} Bpm:{' '*(3-len(str(result.tempo)))}{result.tempo} Title: {result.name}{' '*(n-len(result.name))},{[(a.name,a.followers) for a in result.artists]}" 
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

    def _filter_followers(self, results):
        follow_filter = int(self.settings.get('followers'))
        reduced_results = []
        for song in results:
            keep = True
            song_artists = song.artists
            for artist in song_artists:
                if artist.followers > follow_filter:
                    keep = False
            if keep == True:
                reduced_results.extend([song])
        print(f"Follower filter reduced {len(results)} results to {len(reduced_results)}")
        time.sleep(1)
        return reduced_results
            
    def search_song(self, search=None,data=None):
        if search is None:
            result_limit = int(self.settings.get('result_limit'))   ### amount of songs per request
            result_offset = int(self.settings.get('result_offset')) ### search offset, default 0
            max_search = int(self.settings.get('max_search_n'))     ### max data request 
            entities = []

            search_term = input("Song Name:")

            if search_term != '':

                while not (int(result_offset)>=int(max_search)):
                    search_results, *_ = self.client.search(
                        query=search_term,
                        types=('track',),
                        market='from_token',
                        limit=result_limit,
                        offset=result_offset
                        )
                    result_offset += result_limit

                    if search_results:
                        entities.extend([result for result in search_results.items])
                        if len(search_results.items) < result_limit:
                            print(f"Breaking max {len(search_results.items)} matches where found out max out of {max_search} attempts")
                            time.sleep(1)
                            break
                    else:
                        break

                if len(entities) > 0:

                    # Fetch all artists from the songs
                    chucked_artist_list = []
                    artist_list = []
                    for ent in entities:
                        for artist in ent.artists:
                            artist_list.append(artist.id)
                            if len(artist_list) == 50:
                                chucked_artist_list.append(artist_list)
                                artist_list=[]
                    if len(artist_list) > 0:  #add remaining artists
                        chucked_artist_list.append(artist_list)

                    ## add followers to each artist (bundle artist in large requests insstead of single)
                    # chunk the follower requests
                    artists_id, artists_followers = [],[]
                    for chunck in chucked_artist_list:
                        d = self.client.artists(chunck)
                        artists_id.extend([a.id for a in d])
                        artists_followers.extend([a.followers.total for a in d])

                    for ent in entities:
                        for artist in ent.artists:
                            f_id = artists_id.index(artist.id)
                            artist.followers = artists_followers[f_id]
                            # print(artist.id, artists_id[f_id], artists_followers[f_id])

                
                    songs =  self._filter_followers(entities)
                    print(f"numb songs:{len(songs)}, sleep(1sec)")
                    
                    if len(songs) > 50:
                        print(f"recuding resutls to 50, next update allows for loading next")
                        songs = songs[:50]

                    time.sleep(1)

                    # This can also be chuncked!
                    reduced_entities = []
                    if len(songs) > 0:
                        songs_metadata = self._add_song_metadata(songs)
                        reduced_entities.extend(songs_metadata)


                    # time.sleep(10)    
                else:
                    print("No results found, returing in 3sec")
                    time.sleep(3)

        else:
            reduced_entities = data
            search_term = search

        if len(reduced_entities) > 0:
            song_strs = self._format_song_title(reduced_entities)
            empty = [None]*len(reduced_entities)

            items = dict(zip(song_strs, empty))
            songs_view = CLI().create_menu(
                title=f"M3UL Songs for {search_term} found {len(song_strs)}:",
                entries=items,
                args=True,
            )
            if songs_view != None:
                self.player(reduced_entities[songs_view])
                self.search_song(search_term,reduced_entities)



        
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



