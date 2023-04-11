from app.helpers.openai import ask_model
from app.helpers.prompts import get_playlist_messages, extract_code_and_comments
from app.helpers.spotify import execute_playlist_code, get_playlist_by_id, get_user_playlists, get_playlist_by_name
from . import Blueprint, jsonify, render_template, request

bp = Blueprint('routes', __name__)

@bp.route("/", methods=("GET", "POST",))
def index():
    result = playlist_name = gpt_response = gpt_comments = playlist_id = None
    if request.method == "POST":
        data = request.get_json()
        form_type = data["form_type"]
        playlist_name = data["playlist_name"]
        if form_type == "playlist":
            gpt_response = ask_model(get_playlist_messages(playlist_name, data["question"]))
        elif form_type == "code":
            gpt_response = data["gpt_response"]
            gpt_code, gpt_comments = extract_code_and_comments(gpt_response)
            result = execute_playlist_code(playlist_name, gpt_code, gpt_comments)
        return jsonify(result=result, playlist_name=playlist_name, gpt_response=gpt_response, playlist_id=playlist_id)
    return render_template("index.html")


@bp.route("/playlists", methods=("GET",))
def return_playlists():
    return jsonify(get_user_playlists())


@bp.route("/search-playlist/<string:playlist_name>", methods=("GET",))
def search_playlist(playlist_name):
    return jsonify(get_playlist_by_name(playlist_name))


@bp.route("/playlist-info/<string:playlist_id>", methods=("GET",))
def get_playlist_info(playlist_id):
    return jsonify(get_playlist_by_id(playlist_id))