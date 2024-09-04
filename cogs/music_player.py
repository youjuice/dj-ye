import discord
from discord.ext import commands
from discord import app_commands
from utils.playlist_manager import PlaylistManager
from cogs.music_controller import MusicController
from cogs.play_controller import PlayController
from cogs.playlist_controller import PlaylistController
from cogs.playlist_recommender import PlaylistRecommender
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

class MusicPlayer(commands.Cog, PlayController, PlaylistController):
    def __init__(self, bot):
        self.bot = bot
        self.playlist_manager = PlaylistManager()
        self.is_playing = False
        self.controller_message = None
        self.recommender = PlaylistRecommender(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        PlayController.__init__(self)
        PlaylistController.__init__(self)

    async def ensure_voice(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                return await interaction.user.voice.channel.connect()
            else:
                await interaction.followup.send("음성 채널에 먼저 참가해주세요!")
                raise commands.CommandError("Author not connected to a voice channel.")
        return interaction.guild.voice_client

    @app_commands.command(name="stop", description="Stops and disconnects the bot from voice")
    async def stop(self, interaction: discord.Interaction):
        await interaction.guild.voice_client.disconnect()
        self.playlist_manager.clear_playlist()
        await interaction.response.send_message("Disconnected from voice channel.")
        if self.controller_message:
            await self.controller_message.delete()
            self.controller_message = None

    async def update_controller(self, text_channel):
        view = MusicController(self)
        if self.controller_message:
            await self.controller_message.delete()
        self.controller_message = await text_channel.send("ᖰ(ღ'ㅅ'ღ)ᖳ", view=view)

    async def show_music_controller(self, text_channel):
        view = MusicController(self)
        await text_channel.send(view=view)

    @app_commands.command(name="recommend", description="Get a playlist recommendation based on your text")
    async def recommend(self, interaction: discord.Interaction, text: str):
        try:
            await self.recommender.process_recommendation(
                interaction,
                text,
                self.playlist_manager,
                self.ensure_voice,
                self.play_song
            )
        except Exception as e:
            await interaction.followup.send(
                "An error occurred while processing your recommendation. Please try again later.")

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))