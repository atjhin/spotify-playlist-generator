# ------------------------------------------- Archive -----------------------------------------
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
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, auth_token=None, scope = "playlist-read-private playlist-read-collaborative playlist-modify-public"):
        self.client_id=client_id
        self.client_secret=client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.auth_token=auth_token
        
        
    
    def connect(self, auth):
        # client_creds = SpotifyClientCredentials(client_id=self.client_id, 
        #                                         client_secret=self.client_secret)
        
        # client = spotipy.Spotify(client_credentials_manager=client_creds)
        # client_creds = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret, redirect_uri=SPOTIFY_REDIRECT_URI)
        # if self.auth_token is not None:
        #     client =  spotipy.Spotify(auth=self.auth_token)
        #     logging.warning('Auth successfull')
        #     print('Auth successfull\n\n')
        # else:
        # #     client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.client_id,
        # #                                         client_secret=self.client_secret,
        # #                                         redirect_uri=self.redirect_uri,
        # #                                         scope=self.scope))
        #     logging.warning('Auth token is missing')
        #     print('Auth token is missing\n\n')
        #     # raise Exception("Auth token is missing")
        client = spotipy.Spotify(auth_manager=auth)
        self.client_ = client


        
    def get_playlist(self) -> list:
        playlists = []
        offset = 0
        while True:
            response = self.client_.current_user_playlists(offset=offset, limit=50)
            playlists.extend(response['items'])
            if response['next']:
                offset += len(response['items'])
            else:
                break
        playlists = [playlist for playlist in playlists if playlist is not None]
        self.playlists_detail = playlists
        self.playlists_name_ = [playlist['name'] for playlist in playlists]
        return playlists
    
    def _get_tracks_from_playlists(self, playlists, unique):
        track_ls = []
        playlists_ls = self.playlists_name_ if playlists is None else playlists
        
        for playlist in self.playlists_detail:
            name = playlist['name']
            is_public = 1 if playlist['public'] else 0  # Check if the playlist is public
            
            if name not in playlists_ls:
                continue
            
            results = self.client_.playlist(playlist['id'], fields="tracks,next")
            tracks = results['tracks']

            for i, item in enumerate(tracks['items']):
                track_ls.append((name, item['track']['id'], item['track']['name'], is_public))  # Include `is_public`
        
        tracks_df = pd.DataFrame(track_ls, columns=['playlist', 'id', 'name', 'public']).drop_duplicates() \
                if unique else pd.DataFrame(track_ls, columns=['playlist', 'id', 'name', 'public'])
        return tracks_df
    
    
    def _get_audio_features_from_tracks(self, list_of_id, unique):
        tracks_detail = []
        for i in range(len(list_of_id) // 100 + 1):
            tracks_subset = list_of_id[i*100: (i+1)*100]
            audio_features_dict = [x for x in self.client_.audio_features(tracks_subset) if x is not None]
            if (len(tracks_subset) > 0):
                tracks_detail += audio_features_dict

        features_df = pd.DataFrame(tracks_detail).drop_duplicates() if unique \
                      else pd.DataFrame(tracks_detail)
        return features_df
    
    
    def get_tracks_from_playlists(self, limit=50, playlists=None, unique=True):
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
        # self.username = username
        
        # self.get_playlist(username, limit)
        
        self.playlists_df_ = self._get_tracks_from_playlists(playlists, unique)
        song_ids = self.playlists_df_.id.astype(str)
        features_df = self._get_audio_features_from_tracks(song_ids, unique)
        self.songs_df_ = pd.merge(self.playlists_df_, features_df, how='left', left_on='id', right_on='id')

    
    def get_df(self) -> pd.DataFrame:
        cols = ['name'] + FEATURES
        return self.songs_df_[cols].copy()
    
