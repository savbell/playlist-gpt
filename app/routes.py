from app.helpers.openai import ask_model
from app.helpers.prompts import get_playlist_messages, extract_code_and_comments
from app.helpers.spotify import execute_playlist_code, get_playlist_by_id, get_user_playlists, get_playlist_by_name
from app.helpers.utils import extract_playlist_id_from_link
from . import datetime, Blueprint, jsonify, render_template, request, requests

bp = Blueprint('routes', __name__)

@bp.route("/", methods=("GET", "POST",))
def index():
    if request.method == "POST":
        request_data = request.get_json()
        form_type = request_data["formType"]
        data = request_data["data"]

        if form_type == "playlist":
            gpt_response = ask_model(get_playlist_messages(data["playlistName"], data["question"]))
            gpt_code, gpt_comments = extract_code_and_comments(gpt_response)
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            gpt_response_object = {
                "timestamp": timestamp,
                "playlistInfo": data["playlistInfo"],
                "question": data["question"],
                "response": gpt_response,
                "code": gpt_code,
                "comments": gpt_comments,
                "result": None,
                "error": None,
            }
            if data["gptResponses"] is None:
                data["gptResponses"] = [gpt_response_object]
            data["result"] = None
            
        elif form_type == "code":
            if data["gptResponses"] and len(data["gptResponses"]) > 0:
                last_gpt_response = data["gptResponses"][-1]
                result, error = execute_playlist_code(data["playlistId"], last_gpt_response["code"], last_gpt_response["comments"])
                last_gpt_response["result"] = result
                last_gpt_response["error"] = error
                
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


@bp.route("/resolve-short-url/<path:short_url>", methods=("GET",))
def resolve_short_url(short_url):
    try:
        response = requests.get(short_url)
        playlist_id = extract_playlist_id_from_link(response.url)
        if playlist_id:
            return jsonify({"id": playlist_id})
        else:
            return jsonify({"error": "Failed to extract playlist ID from the expanded URL."}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred while resolving the short URL: {str(e)}"}), 500
