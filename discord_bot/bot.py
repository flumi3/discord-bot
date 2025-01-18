import os
import asyncio
import discord

from dotenv import load_dotenv
from discord.ext import commands
from discord_bot.music_player import MusicPlayer
from discord_bot.message_listener import MessageListener
from discord_bot.lol_buddy import LolBuddy
from discord_bot.csgo_utils import CsgoUtils
from discord_bot.logging_utils import LogUtils

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
    await bot.add_cog(LolBuddy(bot))
    await bot.add_cog(MessageListener(bot))
    await bot.add_cog(CsgoUtils(bot))
    await bot.add_cog(LogUtils(bot))


if __name__ == "__main__":
    asyncio.run(init())
    bot.run(TOKEN)
