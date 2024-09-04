import nltk
import os
import spotipy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from spotipy.oauth2 import SpotifyClientCredentials


class PlaylistRecommender:
    def __init__(self, spotify_client_id, spotify_client_secret):
        self.nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
        self.initialize_nltk()
        self.initialize_spotify(spotify_client_id, spotify_client_secret)
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def initialize_nltk(self):
        os.makedirs(self.nltk_data_path, exist_ok=True)
        nltk.data.path.append(self.nltk_data_path)
        resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                nltk.download(resource, download_dir=self.nltk_data_path, quiet=True)

    def initialize_spotify(self, client_id, client_secret):
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def preprocess_text(self, text):
        tokens = word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token.isalnum()]
        tokens = [token for token in tokens if token not in self.stop_words]
        return ' '.join(tokens)

    async def get_spotify_playlist(self, query, limit=10):
        results = self.sp.search(q=f"playlist {query}", type='playlist', limit=5)
        if not results['playlists']['items']:
            return None

        playlist_id = results['playlists']['items'][0]['id']
        tracks = self.sp.playlist_tracks(playlist_id, limit=limit)

        playlist = []
        for track in tracks['items']:
            if track['track']:
                track_info = track['track']
                playlist.append({
                    'title': track_info['name'],
                    'artist': track_info['artists'][0]['name'] if track_info['artists'] else 'Unknown Artist',
                    'spotify_uri': track_info['uri']
                })

        return playlist

    async def recommend_playlist(self, text):
        preprocessed_text = self.preprocess_text(text)
        return await self.get_spotify_playlist(preprocessed_text)

    async def process_recommendation(self, interaction, text, playlist_manager, ensure_voice, play_song):
        await interaction.response.defer()
        playlist = await self.recommend_playlist(text)

        if playlist:
            response = "Here's a recommended playlist based on your text:\n"
            for i, track in enumerate(playlist, 1):
                response += f"{i}. {track['title']} by {track['artist']}\n"
            await interaction.followup.send(response)

            for track in playlist:
                playlist_manager.add_song(track)

            voice_client = await ensure_voice(interaction)
            await play_song(voice_client)
        else:
            await interaction.followup.send("Sorry, I couldn't find a suitable playlist based on your text.")