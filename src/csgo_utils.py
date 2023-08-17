import logging
import discord
import json
import os

from dotenv import load_dotenv
from discord.ext import commands

logger = logging.getLogger("discord")
load_dotenv()


class CsgoUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.lineups_data = self.load_lineups()
        self.callout_maps = self.load_callout_maps()

    def load_lineups(self):
        # get root dir path
        with open(self.root_dir + "/data/csgo-lineups.json", "r") as f:
            return json.load(f)

    def load_callout_maps(self) -> dict:
        callouts_dir = self.root_dir + "/data/csgo-callouts"
        callouts = dict()
        for file in os.listdir(callouts_dir):
            name = file.split(".")[0]
            path = callouts_dir + "/" + file
            callouts[name] = path
        return callouts

    @commands.command(name="jumpthrow", help="Sends jumpthrow bind command")
    async def send_jumpthrow_bind(self, ctx):
        logger.info(f"User command: !jumpthrow")
        await ctx.send('alias "+jumpthrow" "+jump;-attack"; alias "-jumpthrow" "-jump"; bind alt "+jumpthrow"')

    @commands.command(name="practice", help="Sends a practice config that can be pasted into the console")
    async def send_practice_cfg(self, ctx):
        logger.info(f"User command: !practice")
        cfg = (
            "**Server config:**\n"
            "sv_cheats 1;bot_kick;mp_limitteams 0;mp_autoteambalance 0;mp_roundtime 60;mp_roundtime_defuse 60;"
            "mp_freezetime 0;mp_warmup_end;ammo_grenade_limit_total 5;sv_infinite_ammo 1;mp_maxmoney 60000;"
            "mp_startmoney 60000;mp_buytime 9999;mp_buy_anywhere 1\n\n"
            "**Practice config:**\n"
            "sv_grenade_trajectory 1;sv_grenade_trajectory_time 10;sv_showimpacts 1;sv_showimpacts_time 10;"
            "give weapon_incgrenade;give weapon_flashbang;give weapon_smokegrenade;give weapon_molotov;"
            "give weapon_decoy;give weapon_hegrenade"
        )
        await ctx.send(cfg)

    @commands.command(name="callouts", help="Sends the callouts for a given CS:GO map")
    async def send_callouts(self, ctx, map: str):
        logger.info(f"User command: !callouts")
        map = map.lower()
        if map == "vertigo":
            callouts_dir = self.root_dir + "/data/csgo-callouts"
            await ctx.send(file=discord.File(callouts_dir + "/vertigo-upper.png"))
            await ctx.send(file=discord.File(callouts_dir + "/vertigo-lower.png"))
        if map in self.callout_maps:
            await ctx.send(file=discord.File(self.callout_maps[map]))

    @commands.command(name="lineups", help="Sends lineups embed for given map")
    async def send_lineups(self, ctx, map: str):
        """Sends CS:GO lineups for the given map

        Args:
            map (str): Map to get lineups for
        """
        logger.info(f"User command: !lineups {map}")
        map = map.lower()
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
