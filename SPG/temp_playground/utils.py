from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
# from spotipy.oauth2 import 
import spotipy 
import pandas as pd
import logging
import google.generativeai as genai
import time
import re

# -------------------------------------- GLOBAL VARIABLES -------------------------------------

FEATURES = [
    'danceability', 'energy', 'acousticness', 'instrumentalness', 'valence', 'loudness', 'tempo',
]

# ------------------------------------------- Spotify -----------------------------------------
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
# from spotipy.oauth2 import 
import spotipy 
import pandas as pd
FEATURES = [
    'danceability', 'energy', 'acousticness', 'instrumentalness', 'valence', 'loudness', 'tempo',
]
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
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None,
                 scope = "playlist-read-private playlist-read-collaborative playlist-modify-public user-library-read" ):
        self.client_id=client_id
        self.client_secret=client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        
    
    def connect(self, auth_token):
        self.auth_token=auth_token
        # client_creds = SpotifyClientCredentials(client_id=self.client_id, 
        #                                         client_secret=self.client_secret)
        
        # client = spotipy.Spotify(client_credentials_manager=client_creds)
        # client_creds = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret, redirect_uri=SPOTIFY_REDIRECT_URI)
        if self.auth_token is not None:
            client =  spotipy.Spotify(auth=self.auth_token)
            
        else:
            client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.client_id,
                                                client_secret=self.client_secret,
                                                redirect_uri=self.redirect_uri,
                                                scope=self.scope))
        self.client_ = client


        
    def get_playlists_from_user(self) -> pd.DataFrame:
        playlists = []
        offset = 0
        while True:
            response = self.client_.current_user_playlists(offset=offset, limit=50)
            if response is not None:
                playlists.extend(response['items'])
            if response['next']:
                offset += len(response['items'])
            else:
                break
        # print(playlists)
        playlists = [playlist for playlist in playlists if playlist is not None]
        self.playlists_detail = playlists
        self.playlists_name_ = [playlist['name'] for playlist in playlists]
        return playlists
    
    def get_tracks_from_playlists(self, playlist_id=None):
        """
        ------------------------------------------------------------------------------------------
        get_tracks_from_playlists connects to spotify api and extracts all tracks and 
                                  audio features from playlists
        ------------------------------------------------------------------------------------------
        Parameters:
            - playlists (List[str]): List of playlist names
            - unique (Bool): Returns unique tracks if true
        ------------------------------------------------------------------------------------------
        Returns:
            - Pandas DataFrame of with all tracks in 
        ------------------------------------------------------------------------------------------
        """
        track_ls = []
        playlists_ls = self.playlists_name_ if playlist_id is None else playlist_id
        
        for playlist in self.playlists_detail:
            name = playlist['name']
            id = playlist['id']
            is_public = 1 if playlist['public'] else 0  # Check if the playlist is public
            
            if id not in playlists_ls:
                continue
            
            results = self.client_.playlist(id, fields="tracks,next")
            tracks = results['tracks']

            for i, item in enumerate(tracks['items']):
                artists = ', '.join(artist['name'] for artist in item['track']['artists'])
                track_ls.append((name, item['track']['id'], item['track']['name'], artists, is_public))  # Include artists
        
        self.tracks_df_ = pd.DataFrame(track_ls, columns=['playlist_name', 'track_id', 'track_name', 'artist_names', 'is_public']).drop_duplicates()
        return self.tracks_df_

    def get_playlists_df(self) -> pd.DataFrame:
        playlist_df = pd.DataFrame(self.playlists_detail)
        return playlist_df
    
    def get_tracks_df(self) -> pd.DataFrame:
        # cols = ['name'] + FEATURES
        tracks_df = self.tracks_df_[['track_id', 'track_name', 'artist_names']].drop_duplicates()
        return tracks_df
    
    def create_playlist(self, playlist_name, song_list):
        # Step 1: Create a public playlist
        user_id = self.client_.current_user()["id"]
        playlist = self.client_.user_playlist_create(user=user_id, name=playlist_name, public=True)
        playlist_id = playlist['id']

        # Step 2: Search for each song and add to the playlist
        # track_ids = []
        # for song in song_list:
        #     results = self.client_.search(q=song, type='track', limit=1)
        #     if results['tracks']['items']:
        #         track_ids.append(results['tracks']['items'][0]['id'])
        tracks_df = self.get_tracks_df()
        tracks_df = tracks_df.groupby(['track_name','artist_names'],as_index=False).first()
        track_ids = tracks_df[tracks_df['track_name'].isin(song_list)].track_id.tolist()
        if track_ids:
            self.client_.playlist_add_items(playlist_id, track_ids)
            print(f"Playlist '{playlist_name}' created with {len(track_ids)} songs!")
        else:
            print("No valid tracks found to add to the playlist.")


# ------------------------------------------- GeminiAPI -----------------------------------------

class GeminiPlaylistCurator:
  def __init__(self, api_key, model_name='gemini-1.5-flash'):
    self.api_key = api_key
    self.model_name = model_name

  def init_chat(self):
    genai.configure(api_key=self.api_key)
    self.bot = genai.GenerativeModel(self.model_name)
    self.chat = self.bot.start_chat(history=[])

  def get_example_df(self):
    # example_df_path = '../temp_playground/Example_df_input.csv'
    # return pd.read_csv(example_df_path).to_csv(index=False, na_rep='NA')
    example_string = f"""
    track_name,artist_names
    Father Stretch My Hands Pt. 1,Kanye West
    HIGHEST IN THE ROOM,Travis Scott
    CAN'T SAY,Travis Scott
    HOLIDAY,Lil Nas X
    No Moon At All - Remastered,Julie London
    Maybe,The Ink Spots
    """
    return example_string

  def shuffle_df(self, df, max_rows=10, random_state=2024):
    n = min(df.shape[0], max_rows)
    return df.sample(n=n, random_state=random_state)

  def check_params(self, playlist_name, creativity, min_tracks, max_tracks, special_request):
    if not isinstance(playlist_name, str) or not playlist_name.strip():
      raise ValueError(f"playlist_name must be a non-empty string, value: {playlist_name}")
    if not isinstance(creativity, int) or (creativity < 1) or (creativity > 10):
      raise ValueError(f"creativity must be an integer between 1 and 10, value: {creativity}")
    if not isinstance(min_tracks, int) or (min_tracks < 1):
      raise ValueError(f"min_tracks must be an integer greater than 1, value: {min_tracks}")
    if not isinstance(max_tracks, int) or (max_tracks < 1):
      raise ValueError(f"max_tracks must be an integer greater than 1, value: {max_tracks}")
    if not isinstance(special_request, str):
      raise ValueError(f"special_request must be a string, value: {special_request}")


  def get_prompt(self, df, playlist_name, creativity, min_tracks, max_tracks, special_request):
    prompt = f"""
        You are a spotify music playlist curator who organizes tracks into thematic playlists based on the given list of tracks. 
        The inputs will be given in the following format:
          - playlist name: <str>
          - creativity: <int>
          - special requests: <text>
          - data: 
          ```
          <text>
          ```

        Input format:
        - Playlist name: Title of the playlist, guiding the theme.
        - creativity: Scale of creativity (1 to 10).
        - Special requests: Additional selection criteria.
        - Data: CSV format with track_name and artist_name. 

        Notes:
        - The playlist name will be the title of the playlist. Based on the playlist name, extract tracks in 'data' that you feel is most related to
          the theme and respond with the list of tracks belonging in the playlist. You should consider the songs audio features such as genre, danceability, 
          energy, acousticness, instrumentalness, valence, loudness, tempo and other where you find are helpful.
        - The creativity is how creative you can be when curating the playlist. It ranges from 1 to 10. At creativity 1, strictly match tracks by the most 
          relevant audio features and themes in the playlist name. At creativity 10, allow for more diverse but still loosely related tracks.
        - Special requests: this is some additional information that will help you choose which songs to pick in the playlist.
        - The data will contain track information and is the collection of tracks to be extracted from. It will be in csv format with the 
          following columns:
            - track_name: Name of track
            - artist_name: Name of artists separated by commas
        
        Refer to the input below:
        playlist name: {playlist_name}
        creativity: {creativity}
        special request: {special_request}
        data: 
        ```
        {df.to_csv(index=False, na_rep='NA')}
        ```

        Restrictions:
        - Only extract tracks from the input data.
        - Return between {min_tracks} and {max_tracks} tracks. If none match the playlist theme, return an empty string.
        - Format: songA, songB, songC,... (comma-separated list without additional text).
        
        Before sending back the response, re-check how many tracks are there and select maximum {max_tracks} tracks.
        """
    return prompt
  
  def get_chatgpt_generated_prompt(self, df, playlist_name, creativity, min_tracks, max_tracks, special_request):
    prompt = f"""
      You are a Spotify music playlist curator who creates thematic playlists based on the given list of tracks based on a playlist name. 
      ### Guidelines for Curation
      - Select tracks most relevant to the playlist name and theme.
      - Use audio features like genre, danceability, energy, acousticness, valence, loudness, tempo, and instrumentalness where appropriate.
        - Example: For "Relaxing Evening," choose tracks with low energy, high acousticness, and low tempo.
        - Example: For "Party," prioritize high danceability, energy, and tempo.
      - Incorporate special requests when provided.
      ### Input Format
      - **Playlist name:** Title of the playlist theme.
      - **creativity:** Scale of creativity (1 to 10).
        - At 1, strictly match tracks by audio features and theme.
        - At 10, allow for broader, creative selections still loosely related to the theme.
      - **Special requests:** Additional guidance for track selection (e.g., "focus on upbeat songs").
      - **Data:** A CSV table of eligible tracks enclosed with triple backticks with these columns:
        - `track_name`: Name of track.
        - `artist_name`: Names of artists (comma-separated).
      ### Output Format
      - Return a comma-separated list of tracks closed with double quotes, example: "songA","songB","songC".
      - Restrictions:
        - Only use tracks from the input data.
        - Extract `{min_tracks}-{max_tracks}` tracks.
        - If no tracks match, return an empty string.
      
      ### Example:
      #### Example input:
      - **Playlist name:** Only rap
      - **creativity:** 1
      - **Special request:** I only want rap songs
      - **Data:**
      ```
      {self.get_example_df()}
      ```

      #### Example ouput:
      "Father Stretch My Hands Pt. 1", "HIGHEST IN THE ROOM", "CAN'T SAY", "HOLIDAY"

      ### Inputs:
      - **Playlist name:** {playlist_name}
      - **creativity:** {creativity}
      - **Special request:** {special_request}
      - **Data:**
      ```
      {df.to_csv(index=False, na_rep='NA')}
      ```
      Strictly follow the output format above and before sending back the response, count how many tracks are generated and select maximum {max_tracks} tracks.
      """
    return prompt


  def ask_gemini(self, df, playlist_name, creativity, min_tracks, max_tracks, special_request=None, max_rows=10, random_state=2024):
    df = self.shuffle_df(df,max_rows,random_state)
    special_request = "None" if special_request is None else special_request
    self.check_params(playlist_name, creativity, min_tracks, max_tracks, special_request)
    prompt = self.get_chatgpt_generated_prompt(df, playlist_name, creativity, min_tracks, max_tracks, special_request)
    response = self.chat.send_message(prompt)
    songs = re.findall(r'"([^"]*)"', response.text)
    return songs, response
