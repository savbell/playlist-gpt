from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

def testing(playlist_name):
    answer = ""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private"))
    results = sp.search(q=playlist_name, type="playlist")
    playlist_id = results["playlists"]["items"][0]["id"]
    playlist = sp.playlist(playlist_id)
    
    # Add generated code here to test
    
    
    return answer

print(testing("couch."))