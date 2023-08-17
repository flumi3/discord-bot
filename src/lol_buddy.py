import discord
import requests
import logging
import re

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
        logger.info(f"User {ctx.author} invoked command: !counter")
        url = f"https://op.gg/champions/{champion_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        logger.info(f"Fetching counters for {champion_name} from op.gg...")

        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.Timeout:
            logger.error("Timeout fetching counters from op.gg. Retrying...")
            for i in range(3):
                try:
                    response = requests.get(url, headers=headers)
                except requests.exceptions.Timeout:
                    logger.error("Timeout fetching counters from op.gg. Retrying...")
                    if i == 2:
                        logger.error("Timeout fetching counters from op.gg. Aborting...")
                        await ctx.send("Timeout fetching counters from op.gg. Aborting...")
                        return
                    continue
                else:
                    break
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching counters for {champion_name} from op.gg: {e}")
            return
        else:
            if response.status_code != 200:
                logger.error(f"Error fetching counters for {champion_name} from op.gg ({response.status_code})")
                await ctx.send(f"Error fetching counters for {champion_name} from op.gg")
                return

        logger.debug("Successfully fetched counters from op.gg")
        soup = BeautifulSoup(response.text, "html.parser")  # type: ignore
        # with open("opgg.html", "w", encoding="utf-8") as f:
        #     f.write(soup.prettify())

        regex = re.compile(r"target_champion=(?P<champion_name>\D+)\">")
        weak_against_html = soup.find_all(class_="css-17rk1u8 eesz9tm3")  # all counter elements have this classname
        weak_against = regex.findall(str(weak_against_html))
        weak_against = [champion_name.capitalize() for champion_name in weak_against]
        logger.debug(f"Found {len(weak_against)} 'weak against' counters for {champion_name}")

        strong_against_html = soup.find_all(class_="css-1syqaij eesz9tm3")  # same as above
        strong_against = regex.findall(str(strong_against_html))
        strong_against = [champion_name.capitalize() for champion_name in strong_against]
        logger.debug(f"Found {len(strong_against)} 'strong against' counters for {champion_name}")

        embed = discord.Embed(title=f"Counters for {champion_name.capitalize()}", color=0x00FF00)
        embed.add_field(name="Weak Against", value="\n".join(weak_against), inline=True)
        embed.add_field(name="Strong Against", value="\n".join(strong_against), inline=True)

        await ctx.send(embed=embed)
