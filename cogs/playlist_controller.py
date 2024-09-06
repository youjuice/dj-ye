import discord
from discord import app_commands


class PlaylistController:
    def __init__(self):
        pass

    @app_commands.command(name="my_playlist", description="Show your playlist")
    async def my_playlist(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        playlist = self.get_playlist_manager(guild_id).get_playlist()
        if not playlist:
            await interaction.response.send_message("Your playlist is empty.")
        else:
            playlist_text = "\n".join([f"{i + 1}. {song['title']} - {song['artist']}" for i, song in enumerate(playlist)])
            await interaction.response.send_message(f"♡ Your playlist:\n{playlist_text}")

    @app_commands.command(name="remove", description="Remove a song from the playlist")
    @app_commands.describe(index="The index of the song to remove")
    async def remove_song(self, interaction: discord.Interaction, index: int):
        guild_id = interaction.guild_id
        playlist_manager = self.get_playlist_manager(guild_id)
        removed_song = playlist_manager.remove_song(index - 1)
        if removed_song:
            await interaction.response.send_message(f"Removed song: {removed_song['title']} - {removed_song['artist']}")
        else:
            await interaction.response.send_message("Invalid index. No song removed.")

    @app_commands.command(name="jump", description="Jump to a specific song in the playlist and play it")
    @app_commands.describe(index="The index of the song to jump to")
    async def jump_to_song(self, interaction: discord.Interaction, index: int):
        guild_id = interaction.guild.id
        playlist_manager = self.get_playlist_manager(guild_id)
        song = playlist_manager.jump_to_song(index - 1)
        if song:
            await interaction.response.send_message(f"Jumped to song: {song['title']} - {song['artist']}")
            voice_client = interaction.guild.voice_client
            if voice_client:
                if voice_client.is_playing():
                    voice_client.stop()

                self.force_play[guild_id] = True
                self.is_playing[guild_id] = False

                await self.play_song(voice_client, guild_id)
            else:
                await interaction.followup.send("Bot is not connected to a voice channel. Use the play command first.")
        else:
            await interaction.response.send_message("Invalid index. Couldn't jump to the song.")

    @app_commands.command(name="shuffle", description="Shuffle the playlist")
    async def shuffle_playlist(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        playlist_manager = self.get_playlist_manager(guild_id)
        playlist_manager.shuffle_playlist()
        await interaction.response.send_message("Playlist has been shuffled!")
