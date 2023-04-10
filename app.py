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
    result = playlist_name = gpt_response = gpt_comments = None
    if request.method == "POST":
        form_type = request.form["form_type"]
        playlist_name = request.form["playlist_name"]
        if form_type == "playlist":
            question = request.form["question"]
            response = openai.ChatCompletion.create(
                model=openai_model,
                messages=get_messages(playlist_name, question),
            )
            gpt_response = response.choices[0]["message"]["content"]
        elif form_type == "code":
            gpt_response = request.form["gpt_response"]
            gpt_code, gpt_comments = extract_code_and_comments(gpt_response)
            result = execute_gpt_code(playlist_name, gpt_code, gpt_comments)
        return render_template("index.html", result=result, playlist_name=playlist_name, gpt_response=gpt_response)

    return render_template("index.html")


@app.route("/playlists", methods=("GET",))
def get_playlists():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private"))
    playlists = sp.current_user_playlists(limit=50)
    response = [{"name": playlist["name"], "id": playlist["id"]} for playlist in playlists["items"]]
    return jsonify(response)


def generate_prompt(playlist_name, question):
    return """Use only data available through the Spotify API. For the playlist called {}, answer: {}
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
            Assume we already have the playlist ID as playlist_id, and the spotipy.Spotify instance as sp. Do not include anything 
            but the code. Account for the possibility of some fields being empty. If the question cannot be answered with data from 
            the Spotify API, respond with `answer = \"Your question was unable to be answered.\"` Make sure to check for the presence 
            of required keys in the fetched data before using them. Use the appropriate methods and attributes from the Spotipy library 
            to interact with the Spotify API.
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
            What is the name and link of the most popular track?
        """)},
        {"role": "assistant", "content": textwrap.dedent("""
            ```
            playlist = sp.playlist(playlist_id)
            most_popular_track = max(playlist['tracks']['items'], key=lambda x: x['track']['popularity'])['track']
            track_name = most_popular_track['name']
            track_link = most_popular_track['external_urls']['spotify']
            answer = f"The most popular track in the <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist is <a href='{track_link}' target='_blank'>{track_name}</a>."
            ```
        """)},
        {"role": "user", "content": textwrap.dedent("""
            Use only data available through the Spotify API. For the playlist called 📅🌸 03/2023 part 1.: 
            What are the top three genres?
        """)},
        {"role": "assistant", "content": textwrap.dedent("""
            ```
            tracks = sp.playlist_tracks(playlist_id, fields='items(track(name, artists(id)))')['items']
            artists = set([artist['track']['artists'][0]['id'] for artist in tracks])
            artist_info = sp.artists(artists)['artists']
            genre_count = {}
            for artist in artist_info:
                for genre in artist['genres']:
                    if genre in genre_count:
                        genre_count[genre] += 1
                    else:
                        genre_count[genre] = 1
            top_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:3]
            top_genres = [genre[0] for genre in top_genres]
            answer = f"The top three genres in the <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist are: {', '.join(top_genres)}"
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
    return code, comments


def execute_gpt_code(playlist_name, code, comments=""):
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private"))
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
