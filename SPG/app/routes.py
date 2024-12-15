from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import app
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import os
from temp_playground.utils import Spotify
from instance.config import (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPE,
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

sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=SPOTIFY_SCOPE,
                        cache_path=False,
                        show_dialog=True)

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
    #     auth_url = sp_oauth.get_authorize_url()
    #     return redirect(auth_url)
    auth_url = sp_oauth.get_authorize_url(state="xyz")
    auth_url += "&prompt=login"  # Add the prompt parameter
    return redirect(auth_url)

# Callback route to handle Spotify redirect
@main_blueprint.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('main.home'))


@main_blueprint.route('/logout')
def logout():
    # Clear the session to log out
    session.pop('token_info', None)  # Remove the token_info from the session
    cache_path = sp_oauth.cache_handler.cache_path
    if os.path.exists(cache_path):
        os.remove(cache_path)
    session.clear()  # Clears session on logout
    flash('You have been logged out!', 'info')
    return redirect(url_for('main.home'))


@main_blueprint.route('/home')
def home():
    # Render the home page (which will now show playlists)
    if 'token_info' not in session:
        playlists = None
    else:
        token_info = session['token_info']
        sp = Spotify(auth_token=token_info['access_token'])
        sp.connect(sp_oauth)
        playlists = sp.get_playlist()
    session['playlists'] = playlists
    return render_template('home.html')


@main_blueprint.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        # Handle the form submission
        selected_playlists = request.form.getlist('selected_playlists')
        session['selected_playlists'] = selected_playlists
        
        # Process special request data
        playlist_name = request.form.get('playlist_name')
        range_songs = request.form.get('range_songs')
        creativity = request.form.get('creativity')
        special_requests = request.form.get('special_requests')
        
        # Store these in the session or use them as needed for playlist generation
        session['playlist_name'] = playlist_name
        session['range_songs'] = range_songs
        session['creativity'] = creativity
        session['special_requests'] = special_requests

        # print(session['playlist_name'] + "\n"+ session['range_songs'] +"\n"+ session['creativity'] +"\n"+ session['special_requests'])
        
        # You can now use these session variables to generate the playlist or whatever processing is needed
        # For example, you might generate a playlist based on the selected playlists and special requests
        
        return redirect(url_for('main.generate'))  # Redirect to reload the page or show the result
    
    return render_template('generate.html')