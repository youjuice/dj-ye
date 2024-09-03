import discord
from discord.ext import commands
from discord import app_commands
from utils.ytdlsource import YTDLSource
from cogs.music_controller import MusicController
from utils.playlist_manager import PlaylistManager


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlist_manager = PlaylistManager()

    async def ensure_voice(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                voice_client = await interaction.user.voice.channel.connect()
                await self.show_music_controller(interaction.channel)
                return voice_client
            else:
                await interaction.followup.send("음성 채널에 먼저 참가해주세요!")
                raise commands.CommandError("Author not connected to a voice channel.")
        return interaction.guild.voice_client

    async def show_music_controller(self, text_channel):
        view = MusicController(self)
        await text_channel.send("ᖰ(ღ'ㅅ'ღ)ᖳ", view=view)

    @app_commands.command(name="play", description="Enter Song Title & Artist")
    @app_commands.describe(title="Title", artist="Artist")
    async def play(self, interaction: discord.Interaction, title: str, artist: str):
        await interaction.response.defer()

        try:
            voice_client = await self.ensure_voice(interaction)
            song_info = {"title": title, "artist": artist}

            if not voice_client.is_playing():
                self.playlist_manager.add_song(song_info)
                await self.play_song(voice_client)
                current_song = self.playlist_manager.get_current_song()
                await interaction.followup.send(f'🎧 Now playing: {current_song["title"]} - {current_song["artist"]}')
            else:
                self.playlist_manager.add_song(song_info)
                await interaction.followup.send(f'🎵 Added to playlist: {title} - {artist}')
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            print(f"Detailed error: {e}")

    @app_commands.command(name="play_url", description="Enter YouTube URL")
    @app_commands.describe(url="YouTube URL")
    async def play_url(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        try:
            voice_client = await self.ensure_voice(interaction)
            async with interaction.channel.typing():
                source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

            self.playlist_manager.add_song(source)
            if not voice_client.is_playing():
                await self.play_song(voice_client)
                await interaction.followup.send(f'🎧 Now playing: {source.title}')
            else:
                await interaction.followup.send(f'🎵 Added to playlist: {source.title}')
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            print(f"Detailed error: {e}")

    @app_commands.command(name="volume", description="Changes the player's volume")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, interaction: discord.Interaction, volume: int):
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("Not connected to a voice channel.")

        interaction.guild.voice_client.source.volume = volume / 100
        await interaction.response.send_message(f"🔊 Changed volume to {volume}%")

    async def play_next(self, voice_client):
        next_song = self.playlist_manager.get_next_song()
        if next_song:
            await self.play_song(voice_client)
            # 다음 노래 재생 알림
            text_channel = voice_client.guild.text_channels[0]  # 첫 번째 텍스트 채널을 사용
            await text_channel.send(f'🎧 Now playing: {next_song["title"]} - {next_song["artist"]}')
        else:
            await voice_client.disconnect()
            text_channel = voice_client.guild.text_channels[0]
            await text_channel.send("Playlist ended. Disconnected from voice channel.")

    async def play_previous(self, voice_client):
        prev_song = self.playlist_manager.get_previous_song()
        if prev_song:
            await self.play_song(voice_client)
            # 이전 노래 재생 알림
            text_channel = voice_client.guild.text_channels[0]  # 첫 번째 텍스트 채널을 사용
            await text_channel.send(f'🎧 Now playing: {prev_song["title"]} - {prev_song["artist"]}')
        else:
            text_channel = voice_client.guild.text_channels[0]
            await text_channel.send("No previous songs in the playlist.")

    async def play_song(self, voice_client):
        current_song = self.playlist_manager.get_current_song()
        if current_song:
            query = f"{current_song['title']} {current_song['artist']}"
            source = await YTDLSource.search_source(query, loop=self.bot.loop, download=False)
            voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(voice_client)))

    @app_commands.command(name="add_playlist", description="Add a song to the playlist")
    @app_commands.describe(title="Song title", artist="Artist name")
    async def add_playlist(self, interaction: discord.Interaction, title: str, artist: str):
        song_info = {
            "title": title,
            "artist": artist,
            "query": f"{title} {artist}"
        }
        self.playlist_manager.add_song(song_info)
        await interaction.response.send_message(f"🎵 Added to playlist: {title} - {artist}")

    @app_commands.command(name="my_playlist", description="Show your playlist")
    async def my_playlist(self, interaction: discord.Interaction):
        playlist = self.playlist_manager.get_playlist()
        if not playlist:
            await interaction.response.send_message("Your playlist is empty.")
        else:
            playlist_text = "\n".join([f"{i + 1}. {song['title']} - {song['artist']}" for i, song in enumerate(playlist)])
            await interaction.response.send_message(f"Your playlist:\n{playlist_text}")

    @app_commands.command(name="stop", description="Stops and disconnects the bot from voice")
    async def stop(self, interaction: discord.Interaction):
        await interaction.guild.voice_client.disconnect()
        self.playlist_manager.clear_playlist()
        await interaction.response.send_message("⏹️ Disconnected from voice channel.")


async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))