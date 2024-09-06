import discord
from discord.ext import commands
from discord import app_commands
from utils.playlist_manager import PlaylistManager
from cogs.music_controller import MusicController
from cogs.play_controller import PlayController
from cogs.playlist_controller import PlaylistController


class MusicPlayer(commands.Cog, PlayController, PlaylistController):
    def __init__(self, bot):
        self.bot = bot
        self.playlist_managers = {}
        self.is_playing = {}
        self.controller_messages = {}
        PlayController.__init__(self)
        PlaylistController.__init__(self)

    def get_playlist_manager(self, guild_id):
        if guild_id not in self.playlist_managers:
            self.playlist_managers[guild_id] = PlaylistManager()
        return self.playlist_managers[guild_id]

    async def ensure_voice(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                voice_client = await interaction.user.voice.channel.connect()
                return voice_client
            else:
                await interaction.followup.send("음성 채널에 먼저 참가해주세요!")
                raise commands.CommandError("Author not connected to a voice channel.")
        return interaction.guild.voice_client

    @app_commands.command(name="stop", description="Stops and disconnects the bot from voice")
    async def stop(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            self.get_playlist_manager(guild_id).clear_playlist()
            self.is_playing[guild_id] = False
            await interaction.response.send_message("Disconnected from voice channel.")
            if guild_id in self.controller_messages:
                await self.controller_messages[guild_id].delete()
                del self.controller_messages[guild_id]
        else:
            await interaction.response.send_message("The bot is not connected to a voice channel.")

    async def update_controller(self, text_channel):
        guild_id = text_channel.guild.id
        view = MusicController(self)
        if guild_id in self.controller_messages:
            await self.controller_messages[guild_id].delete()
        self.controller_messages[guild_id] = await text_channel.send("ᖰ(ღ'ㅅ'ღ)ᖳ", view=view)

    async def show_music_controller(self, text_channel):
        view = MusicController(self)
        await text_channel.send(view=view)


async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
