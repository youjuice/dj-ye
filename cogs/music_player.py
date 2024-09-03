import discord
from discord.ext import commands
from discord import app_commands
from utils.ytdlsource import YTDLSource


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_voice(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                await interaction.user.voice.channel.connect()
            else:
                await interaction.followup.send("음성 채널에 먼저 참가해주세요!")
                raise commands.CommandError("Author not connected to a voice channel.")

    @app_commands.command(name="play", description="Enter Song Title & Artist")
    @app_commands.describe(title="Title", artist="Artist")
    async def play(self, interaction: discord.Interaction, title: str, artist: str):
        await interaction.response.defer()

        try:
            await self.ensure_voice(interaction)
            query = f"{title} {artist}"
            async with interaction.channel.typing():
                source = await YTDLSource.search_source(query, loop=self.bot.loop, download=False)

            if interaction.guild.voice_client.is_playing():
                await interaction.followup.send("노래가 이미 재생 중입니다. 플레이리스트에 추가하려면 /add_playlist 명령어를 사용해주세요.")
            else:
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

    @app_commands.command(name="pause", description="Pause the current music")
    async def pause(self, interaction: discord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("⏹️ The music has been paused.")
        else:
            await interaction.response.send_message("현재 재생 중인 음악이 없습니다.")

    @app_commands.command(name="resume", description="Resume the paused music")
    async def resume(self, interaction: discord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("The music has been resumed.")
        elif interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            await interaction.response.send_message("The music is already playing.")
        else:
            await interaction.response.send_message(
                "There is no music to resume. Use the play command to start playing music.")


async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))