from spotipy.oauth2 import SpotifyClientCredentials
import spotipy 
import pandas as pd


class Spotify:
    """
    ---------------------------------------------------------------------------------------------
    Spotify class helps to extract tracks and its audio features from user playlists
    ---------------------------------------------------------------------------------------------
    Parameters:
        - client_id (str): User client id
        - client_secret (str): User secret id
    ---------------------------------------------------------------------------------------------
    Attributes:
        - client_ (spotipy.Spotify object): Initialized Spotify client object  
        - playlists_name_ (List[str]): List of all playlist names
        - df_ (pandas.DataFrame): Data with tracks and audio features
    ---------------------------------------------------------------------------------------------
    Methods
        - get_tracks_from_playlists: Extract tracks and audio features from user playlists
    ---------------------------------------------------------------------------------------------
    """
    def __init__(self, client_id, client_secret):
        self.client_id=client_id
        self.client_secret=client_secret
        
    
    def _connect(self):
        client_creds = SpotifyClientCredentials(client_id=self.client_id, 
                                                client_secret=self.client_secret)
        client = spotipy.Spotify(client_credentials_manager=client_creds)
        self.client_ = client
        
        
    def _get_playlist_from_username(self, username, limit, offset):
        playlists = self.client_.user_playlists(username, limit=limit, offset=offset)
        self.playlists_detail = playlists['items']
        self.playlists_name_ = [playlist['name'] for playlist in playlists['items']]
        
    
    def _get_tracks_from_playlists(self, playlists, unique):
        track_ls = []
        playlists_ls = self.playlists_name_ if playlists is None else playlists
        for playlist in self.playlists_detail:
            name = playlist['name']
            if name not in playlists_ls:
                continue
            results = self.client_.playlist(playlist['id'], fields="tracks,next")
            tracks = results['tracks']

            for i, item in enumerate(tracks['items']):
                track_ls.append((name, item['track']['id'], item['track']['name']))
        
        tracks_df = pd.DataFrame(track_ls, columns=['playlist', 'id', 'name']).drop_duplicates() \
                   if unique else pd.DataFrame(track_ls, columns=['playlist', 'id', 'name'])
        return tracks_df
    
    
    def _get_audio_features_from_tracks(self, list_of_id, unique):
        tracks_detail = []
        for i in range(len(list_of_id) // 100 + 1):
            tracks_subset = list_of_id[i*100: (i+1)*100]
            tracks_detail += self.client_.audio_features(tracks_subset) \
                             if len(tracks_subset) > 0 else []
        features_df = pd.DataFrame(tracks_detail).drop_duplicates() if unique \
                      else pd.DataFrame(tracks_detail)
        return features_df
    
    
    def get_tracks_from_playlists(self, username, limit=50, playlists=None, unique=True):
        """
        ------------------------------------------------------------------------------------------
        get_tracks_from_playlists connects to spotify api and extracts all tracks and 
                                  audio features from playlists
        ------------------------------------------------------------------------------------------
        Parameters:
            - username (str): Spotify username id
            - limit (int): Maximum number of playlists
            - playlists (List[str]): List of playlist names
            - unique (Bool): Returns unique tracks if true
        ------------------------------------------------------------------------------------------
        Effects:
            - Creates df_ attribute
        ------------------------------------------------------------------------------------------
        """
        self.username = username
        self._connect()
        self._get_playlist_from_username(username, limit, offset=0)
        tracks_df = self._get_tracks_from_playlists(playlists, unique)
        features_df = self._get_audio_features_from_tracks(tracks_df.id, unique)
        self.df_ = pd.merge(tracks_df, features_df, how='left', left_on='id', right_on='id')
    

