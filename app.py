# Standard library imports
import os
import re
import textwrap
import traceback

# Third-party imports
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")


@app.route("/", methods=("GET", "POST"))
def index():
    result = playlist_name = gpt_response = gpt_comments = playlist_id = None
    if request.method == "POST":
        data = request.get_json()
        form_type = data["form_type"]
        playlist_name = data["playlist_name"]
        if form_type == "playlist":
            question = data["question"]
            response = openai.ChatCompletion.create(
                model=openai_model,
                messages=get_messages(playlist_name, question),
            )
            gpt_response = response.choices[0]["message"]["content"]
        elif form_type == "code":
            gpt_response = data["gpt_response"]
            gpt_code, gpt_comments = extract_code_and_comments(gpt_response)
            result = execute_gpt_code(playlist_name, gpt_code, gpt_comments)
        return jsonify(result=result, playlist_name=playlist_name, gpt_response=gpt_response, playlist_id=playlist_id)
    return render_template("index.html")


@app.route("/playlists", methods=("GET",))
def get_playlists():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private,playlist-read-collaborative"))
    playlists = []
    offset = 0
    while True:
        response = sp.current_user_playlists(limit=50, offset=offset)
        playlists += [{"name": playlist["name"], "id": playlist["id"]} for playlist in response["items"]]
        if response["next"] is None:
            break
        offset += 50
    return jsonify(playlists)

@app.route("/search-playlist/<string:playlist_name>", methods=("GET",))
def search_playlist(playlist_name):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private,playlist-read-collaborative"))
    results = sp.search(q=playlist_name, type="playlist")
    if not results["playlists"]["items"]:
        return jsonify({})
    playlist_id = results["playlists"]["items"][0]["id"]
    playlist = sp.playlist(playlist_id)
    return jsonify(playlist)


@app.route("/playlist-info/<string:playlist_id>", methods=("GET",))
def get_playlist_info(playlist_id):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private,playlist-read-collaborative"))
    playlist = sp.playlist(playlist_id)
    return jsonify(playlist)


def generate_prompt(playlist_name, question):
    return """Use only data available through the Spotify API. For the playlist called {}: {}
        """.format(
                playlist_name,
                question,
            )


def get_messages(playlist_name, question):
    messages = [
        # gpt-3.5-turbo-0301 does not always pay strong attention to system messages.
        # As a workaround for now, I've added a few user messages to help the model 
        # understand not to respond to non-Spotify requests.
        {"role": "system", "content": textwrap.dedent("""
            You only respond with the Python code required to answer a question about a Spotify playlist using the Spotify API. 
            Assume we already have the playlist ID as playlist_id, spotipy.Spotify instance as sp, and playlist as playlist. 
            Do not include anything but the code. Account for the possibility of some fields being empty. If the question cannot 
            be answered with data from the Spotify API, respond with `answer = \"Your question was unable to be answered.\"` 
            Make sure to check for the presence of required keys in the fetched data before using them. Use the appropriate 
            methods and attributes from the Spotipy library to interact with the Spotify API. Define any helper functions.
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
            What is the least popular track?
        """)},
        {"role": "assistant", "content": textwrap.dedent("""
            ```
            all_tracks = get_all_playlist_tracks(playlist_id, sp)
            least_popular_track = min(all_tracks, key=lambda x: x['track']['popularity'])['track']
            if 'name' in least_popular_track:
                track_name = least_popular_track['name']
                track_link = least_popular_track['external_urls']['spotify']
                answer = f"The least popular song in the <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist is <a href='{track_link}' target='_blank'>{track_name}</a>."
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
        {"role": "user", "content": generate_prompt(playlist_name, question)},
    ]
    return messages


def extract_code_and_comments(response):
    code = re.search(r"```(.*?)```", response, re.MULTILINE | re.DOTALL)
    if code:
        comments = response.replace(code.group(0), "").strip()
        code = code.group(1).replace("python", "")
    else:
        comments = ""
        code = response.replace("python", "")

    # The model keeps using these functions without defining them, so I'm manually adding them since they're quite useful.
    # TODO: Figure out how to get the model to listen to me when I ask it to define its helper functions!!
    if "get_all_playlist_tracks" in code:
        code = textwrap.dedent("""
            def get_all_playlist_tracks(playlist_id, sp):
                tracks, offset, limit = [], 0, 100
                while True:
                    batch = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
                    tracks.extend(batch['items'])
                    if len(batch['items']) < limit: break
                    offset += limit
                return tracks
            """) + "\n\n" + code
    if "get_artist_info_batched" in code:
        code = textwrap.dedent("""
            def get_artist_info_batched(artist_ids, sp, batch_size=50):
                artist_info = []
                for i in range(0, len(artist_ids := list(artist_ids)), batch_size):
                    artist_info.extend(sp.artists(artist_ids[i:i + batch_size])['artists'])
                return artist_info
            """) + "\n\n" + code
    if "get_audio_features_for_tracks" in code:
        code = textwrap.dedent("""
            def get_audio_features_for_tracks(tracks, sp):
                track_ids = [track['id'] for track in tracks]
                audio_features_dict = {}
                for i in range(0, len(track_ids), 100):
                    batch = track_ids[i:i+100]
                    audio_features = sp.audio_features(batch)
                    audio_features_dict.update({f['id']: f for f in audio_features if f})
                return audio_features_dict
            """) + "\n\n" + code
    return code, comments


def execute_gpt_code(playlist_name, code, comments=""):
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private,playlist-read-collaborative"))
    except Exception as e:
        return "There was an error connecting to your Spotify account: {}".format(e)
    
    results = sp.search(q=playlist_name, type="playlist")
    if not results["playlists"]["items"]:
        return "No playlists with that name could be found."
    # TODO: Add logic to handle multiple playlists with the same name. Currently we just take the first result.
    
    playlist_id = results["playlists"]["items"][0]["id"]
    playlist = sp.playlist(playlist_id)
    namespace = {"playlist_id": playlist_id, "playlist": playlist, "sp": sp, "answer": "Your question was unable to be answered."}
    
    try:
        exec(code, namespace)
    except Exception as e:
        traceback.print_exc()
        return "There was an error executing the code generated by GPT: {}\n\n{}".format(e, traceback.format_exc())
    
    if comments:
        answer = f"{namespace['answer']}<br><br><strong>Comments:</strong><br>{comments}"
    else:
        answer = namespace['answer']
    
    print("Answer: " + answer)
    return answer
