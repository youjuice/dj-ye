import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp as youtube_dl

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn -b:a 128k',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                # 재생 목록에서 첫 번째 항목 가져오기
                data = data['entries'][0]
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        except Exception as e:
            print(f"An error occurred while processing the URL: {e}")
            raise

    @classmethod
    async def search_source(cls, search: str, *, loop: asyncio.BaseEventLoop = None, download=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{search}", download=download))

        if 'entries' not in data:
            raise ValueError("Couldn't find any video matching the search query.")

        data = data['entries'][0]

        filename = data['url'] if not download else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_voice(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                await interaction.user.voice.channel.connect()
            else:
                await interaction.followup.send("음성 채널에 먼저 참가해주세요!")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()

    @app_commands.command(name="play", description="Enter Song Title & Artist")
    @app_commands.describe(title="Title", artist="Artist")
    async def play(self, interaction: discord.Interaction, title: str, artist: str):
        await interaction.response.defer()

        try:
            await self.ensure_voice(interaction)
            query = f"{title} {artist}"
            async with interaction.channel.typing():
                source = await YTDLSource.search_source(query, loop=self.bot.loop, download=False)

            interaction.guild.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

            await interaction.followup.send(f'🎧 Now playing: {title} - {artist}')
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            print(f"Detailed error: {e}")

    @app_commands.command(name="play_url", description="Enter YouTube URL")
    @app_commands.describe(url="YouTube URL")
    async def play_url(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()

        try:
            await self.ensure_voice(interaction)
            async with interaction.channel.typing():
                source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

            interaction.guild.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

            await interaction.followup.send(f'🎧 Now playing: {source.title}')
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

    @app_commands.command(name="stop", description="Stops and disconnects the bot from voice")
    async def stop(self, interaction: discord.Interaction):
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Disconnected from voice channel.")


async def setup(bot):
    await bot.add_cog(Music(bot))