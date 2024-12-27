import os
from datetime import timedelta
from dotenv import load_dotenv
from os.path import join, dirname
# dotenv_path = 'SPG/.env'
dotenv_path=join(dirname(dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# Flask Configuration
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Default to SQLite for local use
SQLALCHEMY_TRACK_MODIFICATIONS = False
PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)

# Spotify
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SPOTIFY_SCOPE = "user-library-read playlist-read-private playlist-read-collaborative"
GOOGLE_API_KEY= os.getenv("GOOGLE_API_KEY")