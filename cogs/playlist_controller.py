import discord
from discord import app_commands

class PlaylistController:
    def __init__(self):
        pass

    @app_commands.command(name="add_playlist", description="Add a song to the playlist")
    @app_commands.describe(title="Song title", artist="Artist name")
    async def add_playlist(self, interaction: discord.Interaction, title: str, artist: str):
        song_info = {
            "title": title,
            "artist": artist,
            "query": f"{title} {artist}"
        }
        self.playlist_manager.add_song(song_info)
        await interaction.response.send_message(f"♫ Added to playlist: {title} - {artist}")

    @app_commands.command(name="my_playlist", description="Show your playlist")
    async def my_playlist(self, interaction: discord.Interaction):
        playlist = self.playlist_manager.get_playlist()
        if not playlist:
            await interaction.response.send_message("Your playlist is empty.")
        else:
            playlist_text = "\n".join([f"{i + 1}. {song['title']} - {song['artist']}" for i, song in enumerate(playlist)])
            await interaction.response.send_message(f"♡ Your playlist:\n{playlist_text}")
