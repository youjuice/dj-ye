import discord
from discord.ext import commands
import logging
from config import TOKEN, PREFIX
import asyncio

# 로깅 설정
logging.basicConfig(filename='logs/bot.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


print(f"Loaded token: {TOKEN}")


class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=PREFIX, intents=intents)

    async def on_ready(self):
        logging.info(f'{self.user} has connected to Discord!')
        print(f'{self.user} is ready!')

    async def setup_hook(self):
        await self.load_extension('cogs.music')
        logging.info('Loaded music cog')

bot = MusicBot()


async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())