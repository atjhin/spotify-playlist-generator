from datetime import datetime
from app import db

# Database to store user's session information
class SessionModel(db.Model):
    __tablename__ = 'session_cache'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    data = db.Column(db.Text, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, session_id, data, expiration):
        self.session_id = session_id
        self.data = data
        self.expiration = expiration


class SpotifyCache(db.Model):
    __tablename__ = 'spotify_cache'  # Unique table name
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# # Database for storing user's prompt
# class UserPrompt(db.Model):
#     __tablename__ = 'user_prompt'
#     instance_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, unique=True, nullable=False)
#     prompt_id = db.Column(db.Integer, unique=True, nullable=False)
#     prompt = db.Column(db.String(500), nullable=False)
#     time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     status = db.Column(db.String(50), nullable=False)

#     def __repr__(self):
#         return f"UserPrompt('{self.user_id}', '{self.prompt}', '{self.time}', '{self.status}')"


# # Database for storing prompt parameters
# class PromptParameters(db.Model):
#     __tablename__ = 'prompt_parameters'
#     prompt_id = db.Column(db.Integer, primary_key=True)
#     prompt = db.Column(db.String(500), nullable=False)
#     playlist_name = db.Column(db.String(100), nullable=False)
#     temperature = db.Column(db.Integer)
#     top_p = db.Column(db.Integer)
#     top_k = db.Column(db.Integer)

#     def __repr__(self):
#         return f"PromptParameters('{self.prompt_id}', '{self.playlist_name}')"


# # Database for storing prompt results
# class PromptResults(db.Model):
#     __tablename__ = 'prompt_results'
#     results_id = db.Column(db.Integer, primary_key=True)
#     prompt_id = db.Column(db.Integer, db.ForeignKey('prompt_parameters.prompt_id'), unique=True, nullable=False)
#     result = db.Column(db.String(500), nullable=False)

#     def __repr__(self):
#         return f"PromptResults('{self.results_id}', '{self.result}')"


# # Database for storing song features
# class SongFeatures(db.Model):
#     __tablename__ = 'song_features'
#     song_id = db.Column(db.Integer, primary_key=True)
#     danceability = db.Column(db.Integer, nullable=False)
#     acousticness = db.Column(db.Integer, nullable=False)
#     loudness = db.Column(db.Integer, nullable=False)

#     def __repr__(self):
#         return f"SongFeatures('{self.song_id}', '{self.danceability}', '{self.acousticness}', '{self.loudness}')"


# # Database for storing user's playlist
# class UserPlaylist(db.Model):
#     __tablename__ = 'user_playlist'
#     user_id = db.Column(db.Integer, primary_key=True)
#     playlist_id = db.Column(db.Integer, nullable=False)
#     song_id = db.Column(db.Integer, nullable=False)

#     def __repr__(self):
#         return f"UserPlaylist('{self.user_id}', '{self.playlist_id}', '{self.song_id}')"
