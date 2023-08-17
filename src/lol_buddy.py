import discord
import requests
import logging
import re

from html2image import Html2Image
from bs4 import BeautifulSoup
from discord.ext import commands

logger = logging.getLogger("discord")


class LolBuddy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="counter", help="Lists the top 5 counters to a champion")
    async def counter(self, ctx, *, champion_name: str):
        """Lists the top 5 counters to a champion

        Args:
            champion_name (str): Name of the champion to get counters for
        """
        url = f"https://op.gg/champions/{champion_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        logger.info(f"Fetching counters for {champion_name} from op.gg...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error fetching counters for {champion_name} from op.gg")
            await ctx.send(f"Error fetching counters for {champion_name} from op.gg")
            return
        soup = BeautifulSoup(response.text, "html.parser")
        # with open("opgg.html", "w", encoding="utf-8") as f:
        #     f.write(soup.prettify())

        regex = re.compile(r"target_champion=(?P<champion_name>\D+)\">")
        weak_against_html = soup.find_all(class_="css-17rk1u8 eesz9tm3")  # all counter elements have this classname
        weak_against = regex.findall(str(weak_against_html))
        strong_against_html = soup.find_all(class_="css-1syqaij eesz9tm3")  # same as above
        strong_against = regex.findall(str(strong_against_html))
        weak_against = [champion_name.capitalize() for champion_name in weak_against]
        strong_against = [champion_name.capitalize() for champion_name in strong_against]

        embed = discord.Embed(title=f"Counters for {champion_name.capitalize()}", color=0x00FF00)
        embed.add_field(name="Weak Against", value="\n".join(weak_against), inline=True)
        embed.add_field(name="Strong Against", value="\n".join(strong_against), inline=True)

        hti = Html2Image()
        counter_html = soup.find_all(class_="css-1o74if1 eesz9tm0")
        hti.screenshot(html_str=str(counter_html), save_as="counter.png")

        await ctx.send(embed=embed)
