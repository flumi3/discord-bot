import os
import logging
import random
import json

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
logger = logging.getLogger("discord")


class MessageListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # get root dir path
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(root_dir + "/data/p_urls.json", "r") as f:
            self.porn_gif_urls = json.load(f)

        with open(root_dir + "/data/names.json", "r") as f:
            self.names = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        message.content = message.content.lower()

        if message.content.startswith("pls "):
            query = message.content.split("pls ")[1]
            if query == "porn":
                logger.info("User command: pls porn")
                random_number = random.randint(0, len(self.porn_gif_urls) - 1)
                url = self.porn_gif_urls[random_number]
                await message.channel.send(url)

        # Easter egg: if someone says a name from the names.json file, the bot will respond with "Stinkt"
        elif message.content in self.names:
            await message.channel.send("Stinkt")
