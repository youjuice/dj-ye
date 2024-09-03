import discord
from discord.ui import View, Button


class MusicController(View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.secondary, custom_id="prev")
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await self.player.play_previous(interaction.guild.voice_client)
            await interaction.response.send_message("Switched to the previous song.", ephemeral=True)
        else:
            await interaction.response.send_message("No song is currently playing.", ephemeral=True)

    @discord.ui.button(label="Play/Pause", style=discord.ButtonStyle.primary, custom_id="play_pause")
    async def play_pause_button(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client is None:
            await interaction.response.send_message("I'm not connected to a voice channel.", ephemeral=True)
        elif not interaction.guild.voice_client.is_playing() and not interaction.guild.voice_client.is_paused():
            await interaction.response.send_message("No music is queued. Use the /play command to add music.", ephemeral=True)
        elif interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("▶️ Resumed the music.", ephemeral=True)
        else:
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("⏸️ Paused the music.", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, custom_id="next")
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await self.player.play_next(interaction.guild.voice_client)
            await interaction.response.send_message("Skipped to the next song.", ephemeral=True)
        else:
            await interaction.response.send_message("No song is currently playing.", ephemeral=True)
