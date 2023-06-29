import logging
import discord
import json
import os

from dotenv import load_dotenv
from discord.ext import commands

logger = logging.getLogger("discord")
load_dotenv()


class CsgoLineups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lineups_data = self.load_lineups()

    def load_lineups(self):
        # get root dir path
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(root_dir + "/data/csgo-lineups.json", "r") as f:
            return json.load(f)

    @commands.command(name="jumpthrow", help="TODO")
    async def jumpthrow(self, ctx):
        logger.info(f"User command: !jumpthrow")
        await ctx.send('alias "+jumpthrow" "+jump;-attack"; alias "-jumpthrow" "-jump"; bind alt "+jumpthrow"')

    @commands.command(name="lineups", help="TODO")
    async def lineups(self, ctx, map: str):
        logger.info(f"User command: !lineups {map}")
        if map in self.lineups_data:
            ct_lineups = self.lineups_data[map]["ct"]
            t_lineups = self.lineups_data[map]["t"]
            embed = discord.Embed(title=f"Lineups for {map.capitalize()}", color=0x00FF00)

            def create_lineup_embeds(site_lineups):
                for i in range(len(site_lineups)):
                    site_name = list(site_lineups.keys())[i]
                    lineups = site_lineups[site_name]
                    links = list()
                    for lineup in lineups:
                        link = f"[{lineup['description']}]({lineup['url']})"
                        links.append(link)
                    embed.add_field(name=site_name.capitalize(), value="\n".join(links), inline=False)

            # create embeds for each site
            embed.add_field(name="__T Lineups__", value="\n", inline=False)
            create_lineup_embeds(t_lineups)
            embed.add_field(name="__CT Lineups__", value="\n", inline=False)
            create_lineup_embeds(ct_lineups)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Map not found.")
