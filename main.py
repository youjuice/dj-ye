import discord
from discord.ext import commands
import asyncio
from config import TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

initial_extensions = [
    'cogs.music_player'
]


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f'Loaded extension: {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}: {e}')


async def initialize_nltk():
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)


async def initialize_spotify():
    from spotipy.oauth2 import SpotifyClientCredentials
    import spotipy
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                          client_secret=SPOTIFY_CLIENT_SECRET)
    spotipy.Spotify(client_credentials_manager=client_credentials_manager)


async def main():
    await initialize_nltk()
    await initialize_spotify()
    await load_extensions()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())