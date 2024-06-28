import discord
import requests
import logging
import json
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
            response.raise_for_status()
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
        except requests.HTTPError as e:
            logger.error(f"Error fetching counters for {champion_name} from op.gg: {e}")
            await ctx.send(f"Error fetching counters for {champion_name} from op.gg. Use !logs to see whats going on.")
            return
        else:
            logger.info("Success.")

        logger.info("Successfully fetched counters from op.gg")
        soup = BeautifulSoup(response.text, "html.parser")  # type: ignore

        # Uncomment to print html to file for debugging
        # with open("opgg.html", "w", encoding="utf-8") as f:
        #     f.write(soup.prettify())

        # Get script tag that holds all the relevant JSON data
        script_tag = soup.find("script", id="__NEXT_DATA__", type="application/json")
        json_data = script_tag.string  # Extract the JSON string from the tag
        data_dict = json.loads(json_data)  # Parse the JSON string into a Python dictionary
        counters_data = data_dict["props"]["pageProps"]["data"]["summary"]["opponents"]

        # Extract champion names from the opponents dict
        weak_against_champion_names = [counter["meta"]["name"] for counter in counters_data[0]]
        strong_against_champion_names = [counter["meta"]["name"] for counter in counters_data[1]]
        logger.info(f"Found {len(weak_against_champion_names)} 'weak against' counters for {champion_name}")
        logger.info(f"Found {len(strong_against_champion_names)} 'strong against' counters for {champion_name}")

        embed = discord.Embed(title=f"Counters for {champion_name.capitalize()}", color=0x00FF00)
        embed.add_field(name="Weak Against", value="\n".join(weak_against_champion_names), inline=True)
        embed.add_field(name="Strong Against", value="\n".join(strong_against_champion_names), inline=True)

        await ctx.send(embed=embed)
