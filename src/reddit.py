import os
import random
import requests
import discord

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
logger = logging.getLogger("discord")


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

    def get_random_post(self, subreddit: str, timeframe: str = "all", sort: str = "top"):
        """Queries a random post from a subreddit.

        Args:
            subreddit (str): The subreddit to query.
            timeframe (str, optional): The timeframe to query. Defaults to "all".
            sort (str, optional): The sort to query. Defaults to "top".

        """
        random_number = random.randint(0, 300)
        try:
            base_url = (
                f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={1}&count={random_number}&t={timeframe}"
            )
            result = requests.get(base_url, headers={"User-agent": "DiscordBot"})
            if result:
                # create random number to select a post

                post = result.json()["data"]["children"][random_number]
                media_url = post["data"]["preview"]["reddit_video_preview"]["fallback_url"]
                return media_url
        except:
            print("An Error Occured")
