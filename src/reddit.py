import os
import logging
import requests
import random
import json

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
logger = logging.getLogger("discord")


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # get root dir path
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(root_dir + "/data/p_urls.json", "r") as f:
            self.porn_gif_urls = json.load(f)

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


def get_posts(subreddit: str, sort: str = "top", timeframe: str = "all", amount: int = 100) -> list:
    """Queries a list of posts from a subreddit.

    Args:
        subreddit (str): The subreddit to query.
        sort (str, optional): The sorting method to use. Defaults to "top".
        timeframe (str, optional): The timeframe to query. Defaults to "all".
        limit (int, optional): The number of posts to query. Defaults to 10.

    Returns:
        list: A list of posts.
    """
    logger.info(f"Querying Reddit API for {amount} {sort} posts from r/{subreddit}...")
    posts = []
    after = ""
    initial_amount = amount
    while len(posts) < initial_amount and amount > 0:
        if amount > 100:
            limit = 100
        else:
            limit = amount

        if not after:
            url = f"https://reddit.com/r/{subreddit}/{sort}.json?limit={limit}&t={timeframe}&raw_json=1"
        else:
            url = f"https://reddit.com/r/{subreddit}/{sort}.json?limit={limit}&t={timeframe}&raw_json=1&after={after}"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}  # pretend to be a browser
        response = requests.get(url, headers=headers)
        r_content = response.json()
        posts.extend(r_content["data"]["children"])
        after = r_content["data"]["after"]  # used to get the next page of posts
        amount = amount - limit
    # with open("./data/posts.json", "w") as f:
    #     f.write(str(posts))
    logger.info(f"Retrieved {len(posts)} posts.")
    return posts
