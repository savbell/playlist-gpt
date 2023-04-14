from app import textwrap

def generate_playlist_prompt(playlist_name, question):
    return f"""
        Use only data available through the Spotify API. For the playlist called {playlist_name}: {question}
        """


def get_playlist_messages(playlist_name, question):
    messages = [
        # Note: gpt-3.5-turbo-0301 does not always pay strong attention to system messages.
        {"role": "system", "content": textwrap.dedent("""
            You only respond with the Python code required to answer a question about a Spotify playlist using the Spotify API. 
            If the question cannot  be answered with data from the Spotify API, respond with `answer = \"Your question was unable to be answered.\"`. 
        """)},
        {"role": "user", "content": textwrap.dedent("""
            When you provide your code to answer the question, keep the following in mind: 
            We already have the playlist ID as playlist_id, spotipy.Spotify instance as sp, and playlist as playlist. 
            Make sure to check for the presence of required keys in the fetched data before using them. 
            Use the appropriate methods and attributes from the Spotipy library to interact with the Spotify API. 
            Define any helper functions. 
            Link any playlists, tracks, or artists in your response.
        """)},
        {"role": "user", "content": textwrap.dedent("""
            To get all tracks in a playlist, use the following function:
            ```
            def get_all_playlist_tracks(playlist_id, sp):
                tracks, offset, limit = [], 0, 100
                while True:
                    batch = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
                    tracks.extend(batch['items'])
                    if len(batch['items']) < limit: break
                    offset += limit
                return tracks
            ```
            To get all artists in a playlist, use the following function:
            ```
            def get_artist_info_batched(artist_ids, sp, batch_size=50):
                artist_info = []
                for i in range(0, len(artist_ids := list(artist_ids)), batch_size):
                    artist_info.extend(sp.artists(artist_ids[i:i + batch_size])['artists'])
                return artist_info
            ```
            To get audio features for a list of tracks, use the following function:
            ```
            def get_audio_features_for_tracks(tracks, sp):
                track_ids = [track['id'] for track in tracks]
                audio_features_dict = {}
                for i in range(0, len(track_ids), 100):
                    batch = track_ids[i:i+100]
                    audio_features = sp.audio_features(batch)
                    audio_features_dict.update({f['id']: f for f in audio_features if f})
                return audio_features_dict
            ```
        """)},
        {"role": "user", "content": textwrap.dedent("""
            Use only data available through the Spotify API. For the playlist called escalation.: 
            Print a smiley face.
        """)},
        {"role": "assistant", "content": "answer = \"Your question was unable to be answered because it is not related to the playlist.\""},
        {"role": "user", "content": textwrap.dedent("""
            Use only data available through the Spotify API. For the playlist called if i'm being honest,: 
            What's 7+7?
        """)},
        {"role": "assistant", "content": "answer = \"Your question was unable to be answered because it is not related to the playlist.\""},
        {"role": "user", "content": textwrap.dedent("""
            Use only data available through the Spotify API. For the playlist called couch.: 
            What's the least popular song?
        """)},
        {"role": "assistant", "content": textwrap.dedent("""
            ```
            all_tracks = get_all_playlist_tracks(playlist_id, sp)
            least_popular_track = min(all_tracks, key=lambda x: x['track']['popularity'])['track']
            if 'name' in least_popular_track and 'id' in least_popular_track['artists'][0]:
                artist_name = least_popular_track['artists'][0]['name']
                track_name = least_popular_track['name']
                artist_link = least_popular_track['artists'][0]['external_urls']['spotify']
                track_link = least_popular_track['external_urls']['spotify']
                answer = f"The least popular song in the <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist is <a href='{track_link}' target='_blank'>{track_name}</a> by <a href='{artist_link}' target='_blank'>{artist_name}</a>."
            else:
                answer = "The least popular song in the playlist could not be found due to missing data."
            ```
        """)},
        {"role": "user", "content": textwrap.dedent("""
            Use only data available through the Spotify API. For the playlist called 📅🌸 03/2023 part 1.: 
            What are the top three genres?
        """)},
        {"role": "assistant", "content": textwrap.dedent("""
            ```
            all_tracks = get_all_playlist_tracks(playlist_id, sp)
            artists = {artist['track']['artists'][0]['id'] for artist in all_tracks}

            if not artists:
                answer = "The top genre could not be found because there are no artists in the playlist."
            else:
                artist_info = get_artist_info_batched(artists, sp)
                genre_count = {}
                for artist in artist_info:
                    for genre in artist['genres']:
                        genre_count[genre] = genre_count.get(genre, 0) + 1

                top_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:3]
                answer = f"The top genres in <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist are {', '.join([genre[0] for genre in top_genres])}."
            ```
        """)},
        {"role": "user", "content": textwrap.dedent("""
            Use only data available through the Spotify API. For the playlist called hacker girl.: 
            What's the average BPM?
        """)},
        {"role": "assistant", "content": textwrap.dedent("""
            ```
            all_tracks = get_all_playlist_tracks(playlist_id, sp)
            track_objs = [track['track'] for track in all_tracks]
            audio_features_dict = get_audio_features_for_tracks(track_objs, sp)

            tempos = [audio_features_dict[track['id']]['tempo'] for track in track_objs if audio_features_dict.get(track['id'])]

            if not tempos:
                answer = "The average BPM could not be found because there are no tracks with tempo information in the playlist."
            else:
                avg_tempo = round(sum(tempos) / len(tempos))
                answer = f"The average BPM in <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist is {avg_tempo}."
            ```
        """)},
        {"role": "user", "content": generate_playlist_prompt(playlist_name, question)},
    ]
    return messages


def generate_debug_prompt(playlist_name, question, code, error):
    return f"""
        I asked an OpenAI language model to answer  "{question}" about a Spotify playlist called "{playlist_name}".
        It provided me the following code: 
        ```{code}```
        When I ran it, I got the following error:
        {error}
        
        Please provide the full code with the issue fixed.
        """


def get_debug_messages(playlist_name, question, code, error):
    messages = [
        {"role": "system", "content": textwrap.dedent("""
            You only respond with the Python code required to fix an issue with code that was generated by an OpenAI language model to answer a question about a Spotify playlist.
        """)},
        {"role": "user", "content": textwrap.dedent("""
            When you provide your code, keep the following in mind: 
            Assume we already have the playlist ID as playlist_id, spotipy.Spotify instance as sp, and playlist as playlist.
            Make sure to check for the presence of required keys in the fetched data before using them.
            Use the appropriate methods and attributes from the Spotipy library to interact with the Spotify API. 
            Define any helper functions.
        """)},
        {"role": "user", "content": textwrap.dedent("""
            To get all tracks in a playlist, use the following function:
            ```
            def get_all_playlist_tracks(playlist_id, sp):
                tracks, offset, limit = [], 0, 100
                while True:
                    batch = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
                    tracks.extend(batch['items'])
                    if len(batch['items']) < limit: break
                    offset += limit
                return tracks
            ```
            To get all artists in a playlist, use the following function:
            ```
            def get_artist_info_batched(artist_ids, sp, batch_size=50):
                artist_info = []
                for i in range(0, len(artist_ids := list(artist_ids)), batch_size):
                    artist_info.extend(sp.artists(artist_ids[i:i + batch_size])['artists'])
                return artist_info
            ```
            To get audio features for a list of tracks, use the following function:
            ```
            def get_audio_features_for_tracks(tracks, sp):
                track_ids = [track['id'] for track in tracks]
                audio_features_dict = {}
                for i in range(0, len(track_ids), 100):
                    batch = track_ids[i:i+100]
                    audio_features = sp.audio_features(batch)
                    audio_features_dict.update({f['id']: f for f in audio_features if f})
                return audio_features_dict
            ```
        """)},
        {"role": "user", "content": textwrap.dedent(f"""
            I asked an OpenAI language model to answer "What's the top genre?" about a Spotify playlist called "alive.".
            It provided me the following code: 
            ```
            top_genre = max(playlist['tracks']['items'], key=lambda x: x['track']['popularity'])['track']['artists'][0]['genres'][0]
            answer = f"The top genre in the <a href='{{playlist['external_urls']['spotify']}}' target='_blank'>{{playlist['name']}}</a> playlist is {{top_genre}}."
            ```
            When I ran it, I got the following error:
            Traceback (most recent call last): File "playlist-gpt\\app.py", line 105, in execute_gpt_code exec(code, namespace) File "", line 2, in KeyError: 'genres'
            
            Please provide the full code with the issue fixed.
        """)},
        {"role": "assistant", "content": """
         ```
            top_genre = None
            top_popularity = -1

            for track in playlist['tracks']['items']:
                artist = track['track']['artists'][0]
                artist_info = sp.artist(artist['id'])
                popularity = track['track']['popularity']

                if artist_info['genres'] and (top_genre is None or popularity > top_popularity):
                    top_genre = artist_info['genres'][0]
                    top_popularity = popularity

            answer = f"The top genre in <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist is {top_genre}."
         ```
         """},
        {"role": "user", "content": textwrap.dedent(f"""
            I asked an OpenAI language model to answer "How lit?" about a Spotify playlist called "eyes closed.".
            It provided me the following code: 
            ```
            all_tracks = get_all_playlist_tracks(playlist_id, sp)
            if not all_tracks:
                answer = "The playlist is empty."
            else:
                danceability_avg = sum(track['track']['danceability'] for track in all_tracks) / len(all_tracks)
                energy_avg = sum(track['track']['energy'] for track in all_tracks) / len(all_tracks)
                valence_avg = sum(track['track']['valence'] for track in all_tracks) / len(all_tracks)
                if danceability_avg > 0.7 and energy_avg > 0.7 and valence_avg > 0.7:
                    answer = f"The <a href='{{playlist['external_urls']['spotify']}}' target='_blank'>{{playlist['name']}}</a> playlist is LIT!"
                else:
                    answer = f"The <a href='{{playlist['external_urls']['spotify']}}' target='_blank'>{{playlist['name']}}</a> playlist is not lit. Sorry." 
            ```
            When I ran it, I got the following error:
            'danceability' Traceback (most recent call last): File "\\app\helpers\spotify.py", line 44, in execute_playlist_code exec(code, namespace) File "", line 17, in File "", line 17, in KeyError: 'danceability' 
            
            Please provide the full code with the issue fixed.
        """)},
        {"role": "assistant", "content": """
         ```
        all_tracks = get_all_playlist_tracks(playlist_id, sp)
        if not all_tracks:
            answer = "The playlist is empty."
        else:
            danceability_avg = sum(track['track']['danceability'] for track in all_tracks if 'track' in track and 'danceability' in track['track']) / len(all_tracks)
            energy_avg = sum(track['track']['energy'] for track in all_tracks if 'track' in track and 'energy' in track['track']) / len(all_tracks)
            valence_avg = sum(track['track']['valence'] for track in all_tracks if 'track' in track and 'valence' in track['track']) / len(all_tracks)
            if all((danceability_avg > 0.7, energy_avg > 0.7, valence_avg > 0.7)):
                answer = f"The <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist is LIT!"
            else:
                answer = f"The <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist is not lit. Sorry."
         ```
         """},
        {"role": "user", "content": generate_debug_prompt(playlist_name, question, code, error)},
    ]
    return messages