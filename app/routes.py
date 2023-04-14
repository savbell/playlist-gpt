from app.helpers.openai import ask_model
from app.helpers.prompts import get_playlist_messages, extract_code_and_comments
from app.helpers.spotify import execute_playlist_code, get_playlist_by_id, get_user_playlists, get_playlist_by_name
from . import Blueprint, jsonify, render_template, request

bp = Blueprint('routes', __name__)

@bp.route("/", methods=("GET", "POST",))
def index():
    if request.method == "POST":
        request_data = request.get_json()
        form_type = request_data["formType"]
        data = request_data["data"]

        if form_type == "playlist":
            gpt_response = ask_model(get_playlist_messages(data["playlistName"], data["question"]))
            data["gptResponse"] = gpt_response
            data["result"] = None
        elif form_type == "code":
            gpt_code, gpt_comments = extract_code_and_comments(data["gptResponse"])
            result = execute_playlist_code(data["playlistId"], gpt_code, gpt_comments)
            data["result"] = result

        return jsonify(data)
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