import os
import random
import requests
import discord

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
# REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
# REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")


# auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)

# data = {
#     "grant_type": "password",
#     "username": "USERNAME",
#     "password": "PASSWORD",

# }


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith("pls "):
            query = message.content.split("pls ")[1]
            if query == "porn":
                media_url = self.get_random_post(subreddit="porn")
                print(media_url)
                embed = discord.Embed()
                embed.set_image(url=media_url)
                await message.channel.send(embed=embed)

    def get_random_post(self, subreddit: str, limit: int = 100, timeframe: str = "all", listing: str = "top"):
        try:
            base_url = f"https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}"
            result = requests.get(base_url, headers={"User-agent": "DiscordBot"})
            if result:
                # create random number to select a post
                random_number = random.randint(0, limit - 1)
                post = result.json()["data"]["children"][random_number]
                media_url = post["data"]["preview"]["reddit_video_preview"]["fallback_url"]
                return media_url
        except:
            print("An Error Occured")
