from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from spotipy.oauth2 import SpotifyOAuth
from temp_playground.utils import Spotify, GeminiPlaylistCurator
from instance.config import (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPE, GOOGLE_API_KEY)
from app.database import SpotifyCache, SessionModel, db
from app import SESSION_ID
import json
from datetime import datetime
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseCacheHandler:
    def get(self, key):
        """Retrieve cache from the database."""
        cache_entry = SpotifyCache.query.filter_by(key=key).first()
        return json.loads(cache_entry.value) if cache_entry else None

    def put(self, key, value):
        """Store cache in the database."""
        value = json.dumps(value)
        cache_entry = SpotifyCache.query.filter_by(key=key).first()
        if cache_entry:
            cache_entry.value = value
            cache_entry.timestamp = datetime.utcnow()
        else:
            cache_entry = SpotifyCache(key=key, value=value)
        db.session.add(cache_entry)
        db.session.commit()

    def delete(self, key):
        """Delete cache from the database."""
        cache_entry = SpotifyCache.query.filter_by(key=key).first()
        if cache_entry:
            db.session.delete(cache_entry)
            db.session.commit()

cache_handler = DatabaseCacheHandler()

SP_OUATH = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SPOTIFY_SCOPE,
    cache_path=False,
    show_dialog=True
)

SPOTIFY = Spotify()
GEMINI = GeminiPlaylistCurator(GOOGLE_API_KEY)

main_blueprint = Blueprint('main', __name__)

# Helper functions for session handling
def save_session_data(session_id, key, value):
    session_entry = SessionModel.query.filter_by(session_id=session_id).first()
    if not session_entry:
        session_entry = SessionModel(session_id=session_id, data=json.dumps({}), expiration=datetime.utcnow())
    session_data = json.loads(session_entry.data)
    session_data[key] = value
    session_entry.data = json.dumps(session_data)
    session_entry.expiration = datetime.utcnow()
    db.session.add(session_entry)
    db.session.commit()

def get_session_data(session_id, key):
    session_entry = SessionModel.query.filter_by(session_id=session_id).first()
    if session_entry:
        session_data = json.loads(session_entry.data)
        return session_data.get(key)
    return None

def clear_session_data(session_id):
    session_entry = SessionModel.query.filter_by(session_id=session_id).first()
    if session_entry:
        db.session.delete(session_entry)
        db.session.commit()

@main_blueprint.route('/')
def index():
    return render_template('home.html', playlists=[])

@main_blueprint.route('/login', methods=['GET'])
def login():
    auth_url = SP_OUATH.get_authorize_url(state="xyz")
    auth_url += "&prompt=login"
    return redirect(auth_url)

@main_blueprint.route('/callback')
def callback():
    code = request.args.get('code')
    try:
        token_info = SP_OUATH.get_access_token(code)
        save_session_data(SESSION_ID, "token_info", token_info)  # Save token in the database
        logger.info("Token successfully retrieved and saved.")
    except Exception as e:
        logger.error(f"Error retrieving token: {e}")
        flash("Failed to authenticate with Spotify. Please try again.", "error")
        return redirect(url_for('main.index'))
    return redirect(url_for('main.home'))

@main_blueprint.route('/logout')
def logout():
    clear_session_data(SESSION_ID)  # Clear session data from the database
    flash('You have been logged out!', 'info')
    return redirect(url_for('main.home'))

@main_blueprint.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        token_info = get_session_data(SESSION_ID, "token_info")
        playlists = []
        if token_info:
            try:
                SPOTIFY.connect(auth_token=token_info['access_token'])
                playlists = SPOTIFY.get_playlists_from_user()
                print(f"current playlists: {playlists[:5]}")
                save_session_data(SESSION_ID, "playlists", playlists)
                logger.info("Playlists successfully retrieved.")
            except Exception as e:
                logger.error(f"Error retrieving playlists: {e}")
                flash("Failed to retrieve playlists. Please log in again.", "error")
        else:
            logger.warning("No token found in session.")

    if request.method == 'POST':
        selected_playlists = request.form.getlist('selected_playlists')
        save_session_data(SESSION_ID, "selected_playlists", selected_playlists)
        return redirect(url_for('main.generate'))

    playlists = get_session_data(SESSION_ID, "playlists")
    print(f"playlist from session: {playlists[:5]}")
    return render_template('home.html', playlists=playlists)

@main_blueprint.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        playlist_name = request.form.get('playlist_name', '').strip()
        if not playlist_name:
            flash('Playlist name cannot be empty.', 'error')
            return redirect(url_for('main.index'))
        min_songs = int(request.form.get('min_songs'))
        max_songs = int(request.form.get('max_songs'))
        creativity = int(request.form.get('creativity'))
        special_requests = request.form.get('special_requests')

        save_session_data(SESSION_ID, "playlist_name", playlist_name)
        save_session_data(SESSION_ID, "min_songs", min_songs)
        save_session_data(SESSION_ID, "max_songs", max_songs)
        save_session_data(SESSION_ID, "creativity", creativity)
        save_session_data(SESSION_ID, "special_requests", special_requests)

        list_of_playlist = get_session_data(SESSION_ID, "selected_playlists")
        df = SPOTIFY.get_tracks_from_playlists(list_of_playlist)
        df = df[['track_name', 'artist_names']].drop_duplicates()

        gemini_obj = GEMINI
        gemini_obj.init_chat()
        songs_list, response = gemini_obj.ask_gemini(
            df, playlist_name, creativity, min_songs, max_songs, special_requests, max_rows=1000
        )
        print("List of songs generated:")
        print(songs_list)
        save_session_data(SESSION_ID, "songs_list", songs_list)
        return redirect(url_for('main.add'))

    return render_template('generate.html')

@main_blueprint.route('/add', methods=['GET', 'POST'])
def add():
    songs_list = get_session_data(SESSION_ID, "songs_list")
    playlist_name = get_session_data(SESSION_ID, "playlist_name")
    print("Songs_list from session:")
    print(songs_list)
    if request.method == 'POST':
        SPOTIFY.create_playlist(playlist_name, songs_list)
        return redirect(url_for('main.feedback'))
    return render_template('add.html', songs_list=songs_list, playlist_name=playlist_name)

@main_blueprint.route('/feedback', methods=['GET'])
def feedback():
    return render_template('feedback.html')