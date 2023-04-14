# Standard library imports
import os
import re
import requests
import textwrap
import traceback
from datetime import datetime

# Third-party imports
from dotenv import load_dotenv
from flask import Blueprint, Flask, jsonify, render_template, request
import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Local imports
from . import routes

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes.bp)
    return app
