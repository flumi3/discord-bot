import discord
import requests
import re

from bs4 import BeautifulSoup
from discord.ext import commands


class LolBuddy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="counter", help="Lists the top 5 counters to a champion")
    async def counter(self, ctx, *, champion_name: str):
        url = f"https://op.gg/champions/{champion_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")
        regex = re.compile(r"target_champion=(?P<champion_name>\D+)\">")
        weak_against_html = soup.find_all(class_="css-17rk1u8 eoarhn83")  # all counter elements have this classname
        weak_against = regex.findall(str(weak_against_html))
        strong_against_html = soup.find_all(class_="css-1syqaij eoarhn83")  # same as above
        strong_against = regex.findall(str(strong_against_html))
        weak_against = [champion_name.capitalize() for champion_name in weak_against]
        strong_against = [champion_name.capitalize() for champion_name in strong_against]

        embed = discord.Embed(title=f"Counters for {champion_name.capitalize()}", color=0x00FF00)
        embed.add_field(name="Weak Against", value="\n".join(weak_against), inline=True)
        embed.add_field(name="Strong Against", value="\n".join(strong_against), inline=True)

        await ctx.send(embed=embed)
