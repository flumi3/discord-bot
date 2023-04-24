import asyncio
import os
import discord

from dotenv import load_dotenv
from discord.ext import commands
from music_player import MusicPlayer

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
assert TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)
client.status = discord.Status.online
bot = commands.Bot(command_prefix=("!", "/"), intents=intents)


async def init():
    await bot.add_cog(MusicPlayer(bot))


if __name__ == "__main__":
    asyncio.run(init())
    bot.run(TOKEN)
