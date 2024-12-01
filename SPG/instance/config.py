import os
from datetime import timedelta

# Flask Configuration
SECRET_KEY = os.getenv('SECRET_KEY', '8a0f946f1471e113e528d927220ad977ed8b2cce63303beff10c8cb4a15e1a99')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///spotify_playlist_generator.db')  # Default to SQLite for local use
SQLALCHEMY_TRACK_MODIFICATIONS = False
PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)
