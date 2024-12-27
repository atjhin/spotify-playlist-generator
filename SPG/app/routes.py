from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import app
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import os
from temp_playground.utils import Spotify, GeminiPlaylistCurator
from instance.config import (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPE, GOOGLE_API_KEY,
                            SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, PERMANENT_SESSION_LIFETIME)

# Configuration
# app.config['SECRET_KEY'] = SECRET_KEY
# app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI  # Example DB URI
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
# app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME


print(f"""{SPOTIPY_CLIENT_ID}, {SPOTIPY_CLIENT_SECRET}, {SPOTIPY_REDIRECT_URI}, {SPOTIFY_SCOPE}
      """)
# Spotify OAuth Setup
# app.config['CLIENT_ID'] = SPOTIPY_CLIENT_ID
# app.config['CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
# app.config['REDIRECT_URI'] = SPOTIPY_REDIRECT_URI

SP_OUATH = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=SPOTIFY_SCOPE,
                        cache_path=False,
                        show_dialog=True)
SPOTIFY = Spotify()
GEMINI = GeminiPlaylistCurator(GOOGLE_API_KEY)
# Define a blueprint for routes
main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def index():
#     if 'token_info' not in session:
#         # return redirect(url_for('main.login'))
#     else:
#         token_info = session['token_info']
#         sp = Spotify(auth_token=token_info['access_token'])

#         # Fetch user playlists
#         playlists = sp.current_user_playlists()
#         return render_template('home.html', playlists=playlists)
    return render_template('home.html', playlists=[])

@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # if request.method == 'GET':
    #     if 'name' in session:
    #         flash('You are already logged in!', 'info')
    #         return redirect(url_for('main.home'))
    #     return render_template('login.html')
        
    #     # Redirect to Spotify login
    # else:
    #     auth_url = SP_OUATH.get_authorize_url()
    #     return redirect(auth_url)
    auth_url = SP_OUATH.get_authorize_url(state="xyz")
    auth_url += "&prompt=login"  # Add the prompt parameter
    return redirect(auth_url)

# Callback route to handle Spotify redirect
@main_blueprint.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = SP_OUATH.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('main.home'))


@main_blueprint.route('/logout')
def logout():
    # Clear the session to log out
    session.pop('token_info', None)  # Remove the token_info from the session
    cache_path = SP_OUATH.cache_handler.cache_path
    if os.path.exists(cache_path):
        os.remove(cache_path)
    session.clear()  # Clears session on logout
    flash('You have been logged out!', 'info')
    return redirect(url_for('main.home'))


@main_blueprint.route('/home', methods=['GET', 'POST'])
def home():
    # Render the home page and handle playlist selection form submission
    if request.method == 'GET':
        if 'token_info' not in session:
            playlists = None
        else:
            token_info = session['token_info']
            
            SPOTIFY.connect(auth_token=token_info['access_token'])
            playlists = SPOTIFY.get_playlists_from_user()
        session['playlists'] = playlists  # Store playlists in session
    
    if request.method == 'POST':
        # Handle form submission
        selected_playlists = request.form.getlist('selected_playlists')
        # print("Saving selected playlists \n\n")
        # print(selected_playlists)
        # print("\n\n")
        session['selected_playlists'] = selected_playlists  # Store selected playlists in session
        
        # Redirect to the next step
        return redirect(url_for('main.generate'))
    
    return render_template('home.html', playlists=playlists)


@main_blueprint.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        
        # Process special request data
        playlist_name = request.form.get('playlist_name')
        min_songs = int(request.form.get('min_songs'))
        max_songs = int(request.form.get('max_songs'))
        creativity = int(request.form.get('creativity'))
        special_requests = request.form.get('special_requests')
        
        # Store these in the session or use them as needed for playlist generation
        session['playlist_name'] = playlist_name
        session['min_songs'] = min_songs
        session['max_songs'] = max_songs
        session['creativity'] = creativity
        session['special_requests'] = special_requests
        print(session)
        list_of_playlist = session['selected_playlists']
        df = SPOTIFY.get_tracks_from_playlists(list_of_playlist)
        df = df[['track_name', 'artist_names']].drop_duplicates()
        print(f"Total number of tracks:{df.shape[0]}\nTracks:")
        print(df['track_name'])
        gemini_obj = GeminiPlaylistCurator(GOOGLE_API_KEY)
        gemini_obj.init_chat()
        songs, response = gemini_obj.ask_gemini(df, playlist_name, creativity, min_songs, max_songs, special_requests)
        print(f"Number of tracks: {len(songs)}")
        print(f"{response.text}")
        # SPOTIFY.create_playlist(playlist_name, songs)
        # print(session['playlist_name'] + "\n"+ session['range_songs'] +"\n"+ session['creativity'] +"\n"+ session['special_requests'])
        
        # You can now use these session variables to generate the playlist or whatever processing is needed
        # For example, you might generate a playlist based on the selected playlists and special requests
        
        return redirect(url_for('main.generate'))  # Redirect to reload the page or show the result
    
    return render_template('generate.html')

# @main_blueprint.route('/add', methods=['GET', 'POST'])
# def add():
#     if request.method == 'POST':
#         playlist_name = session['playlist_name']
#         min_songs = session['min_songs']
#         max_songs = session['max_songs']
#         creativity = session['creativity']
#         special_requests = session['special_requests']
        
#         GEMINI.init_chat()
#         songs, response = GEMINI.ask_gemini(df, playlist_name, creativity, min_songs, max_songs, special_requests)
#         print(f"Number of tracks: {len(songs)}")
#         print(f"{response.text}")
#         SPOTIFY.create_playlist(playlist_name, songs)
#         return redirect(url_for('main.feedback'))  # Redirect to reload the page or show the result
    
#     return render_template('add.html')