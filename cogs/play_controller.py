import discord
from discord import app_commands
from utils.ytdl_source import YTDLSource


class PlayController:
    def __init__(self):
        pass

    @app_commands.command(name="play", description="Play a song")
    @app_commands.describe(title="Title", artist="Artist")
    async def play(self, interaction: discord.Interaction, title: str, artist: str):
        await interaction.response.defer()

        try:
            guild_id = interaction.guild.id
            voice_client = await self.ensure_voice(interaction)
            song_info = {"title": title, "artist": artist}
            self.get_playlist_manager(guild_id).add_song(song_info)

            if guild_id not in self.is_playing or not self.is_playing[guild_id]:
                await self.play_song(voice_client, guild_id)
                await interaction.followup.send("Music Start!! ミ★")
            else:
                await interaction.followup.send(f'♫ Added to playlist: {title} - {artist}')
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            print(f"Detailed error: {e}")

    @app_commands.command(name="volume", description="Changes the player's volume")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, interaction: discord.Interaction, volume: int):
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("Not connected to a voice channel.")

        if volume < 0 or volume > 100:
            return await interaction.response.send_message("볼륨은 0에서 100 사이의 값이어야 합니다.")

        interaction.guild.voice_client.source.volume = volume / 100
        await interaction.response.send_message(f"Changed volume to {volume}%")

    async def play_song(self, voice_client, guild_id):
        if guild_id in self.is_playing and self.is_playing[guild_id] and not self.force_play.get(guild_id, False):
            return

        playlist_manager = self.get_playlist_manager(guild_id)
        current_song = playlist_manager.get_current_song()
        if current_song:
            query = f"{current_song['title']} {current_song['artist']}"
            try:
                source = await YTDLSource.search_source(query, loop=self.bot.loop, download=False)

                def after_playing(error):
                    self.is_playing[guild_id] = False
                    if not self.force_play.get(guild_id, False):
                        self.bot.loop.create_task(self.play_next(voice_client, guild_id))

                if voice_client.is_playing():
                    voice_client.stop()

                self.is_playing[guild_id] = True
                self.force_play[guild_id] = False  # force_play 재설정
                voice_client.play(source, after=after_playing)

                if voice_client.channel:
                    await voice_client.channel.send(
                        f'♫ Now playing: {current_song["title"]} - {current_song["artist"]}')
                    await self.update_controller(voice_client.channel)
            except Exception as e:
                print(f"An error occurred: {e}")
                self.is_playing[guild_id] = False
                self.force_play[guild_id] = False  # force_play 재설정
                if not self.force_play.get(guild_id, False):
                    await self.play_next(voice_client, guild_id)
        else:
            if voice_client.is_connected():
                await voice_client.disconnect()
                if voice_client.channel:
                    await voice_client.channel.send("Playlist ended. Disconnected from voice channel.")
                    await self.update_controller(voice_client.channel)

    async def play_next(self, voice_client, guild_id):
        playlist_manager = self.get_playlist_manager(guild_id)
        playlist_manager.move_to_next_song()
        await self.play_song(voice_client, guild_id)

    async def play_previous(self, voice_client, guild_id):
        playlist_manager = self.get_playlist_manager(guild_id)
        playlist_manager.get_previous_song()
        await self.play_song(voice_client, guild_id)