# Standard library imports
import os
import re
import textwrap
import traceback

# Third-party imports
from dotenv import load_dotenv
from flask import Flask, render_template, request
import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")


@app.route("/", methods=("GET", "POST"))
def index():
    result = playlist_name = gpt_code = None
    if request.method == "POST":
        playlist_name = request.form["playlist_name"]
        question = request.form["question"]
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=get_messages(playlist_name, question),
        )
        gpt_code = response.choices[0]["message"]["content"]
        result = execute_gpt_code(playlist_name, extract_code(gpt_code))
    return render_template("index.html", result=result, playlist_name=playlist_name, gpt_code=gpt_code)


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
            Assume we already have the playlist ID as playlist_id. Do not include anything but the code. Account for the 
            possibility of some fields being empty. If the question cannot be answered with data from the Spotify API, respond 
            with `answer = \"Your question was unable to be answered.\"`
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
            What is the name of the most popular track?
        """)},
        {"role": "assistant", "content": textwrap.dedent("""
            ```
            playlist = sp.playlist(playlist_id)
            most_popular_track = max(playlist['tracks']['items'], key=lambda x: x['track']['popularity'])['track']['name']
            answer = f"The most popular track in the <a href='{playlist['external_urls']['spotify']}' target='_blank'>{playlist['name']}</a> playlist is {most_popular_track}."
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


def extract_code(response):
    code = re.search(r"^```(.*?)```$", response, re.MULTILINE | re.DOTALL)
    return code.group(1).replace("python", "") if code else response.replace("python", "")


def execute_gpt_code(playlist_name, code):
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
    
    print("Answer: " + namespace["answer"])
    return namespace["answer"]


# Uncomment to test generated code
"""
def testing(playlist_name):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id,client_secret,redirect_uri,scope="playlist-read-private"))
    results = sp.search(q=playlist_name, type="playlist")
    playlist_id = results["playlists"]["items"][0]["id"]
    playlist = sp.playlist(playlist_id)
    
    # Add generated code here to test
    
    print(answer)

testing("couch.")
"""
