import base64
import os
import asyncio
import logging
import random
import discord
import requests
import spotipy
import yt_dlp as youtube_dl

from dotenv import load_dotenv
from discord.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials

logger = logging.getLogger("discord")

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
assert SPOTIFY_CLIENT_ID
assert SPOTIFY_CLIENT_SECRET

discord.FFmpegPCMAudio("/usr/bin/ffmpeg")


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = list()
        self.spotify = Spotify()

    @commands.command(name="play", help="Plays a song")
    async def play(self, ctx, *, query: str):
        logger.info(f"User command: !play {query}")

        # Connect to voice channel
        if ctx.message.author.voice:
            author_voice_channel = ctx.message.author.voice.channel
            if not ctx.voice_client:
                await author_voice_channel.connect()
                logger.info(f"Bot connected to voice channel '{author_voice_channel}'")
            elif ctx.voice_client.channel != author_voice_channel:
                await ctx.send("The bot is already connected to a different voice channel.", silent=True)
                logger.error(f"Bot already connected to voice channel '{ctx.voice_client.channel}'")
                return
        else:
            await ctx.send(
                "You are not connected to a voice channel. Please connect to a voice channel first.", silent=True
            )
            return

        # Add track(s) to queue
        tracks = list()
        if "open.spotify.com" in query:
            tracks = self.spotify.get_tracks(query)
            if tracks:
                self.queue.extend(tracks)
                logger.info(f"Added {len(tracks)} tracks to queue")
        else:
            tracks.append(query)
            self.queue.append(query)
            logger.info(f"Added '{query}' to queue")

        # Play music
        if not ctx.voice_client.is_playing():
            await self.play_music(ctx)
        else:
            if len(tracks) == 1:
                await ctx.send(f"Added to queue: {tracks[0]}", silent=True)
            elif len(self.queue) > 1:
                await ctx.send(f"Added {len(tracks)} tracks to queue", silent=True)

    @commands.command(name="pause", help="Pauses the currently playing song")
    async def pause(self, ctx):
        logger.info("User command: !pause")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
        else:
            logger.error("Player is not playing anything")
            await ctx.send("The bot is not playing anything at the moment.", silent=True)

    @commands.command(name="resume", help="Resumes a currently paused song")
    async def resume(self, ctx):
        logger.info("User command: !resume")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        else:
            logger.error("Bot was not playing anything")
            await ctx.send("The bot was not playing anything. Use **!play <name_of_song>** to play a song.")

    @commands.command("stop", help="Stops playing song and disconnects the bot from voice channel")
    async def stop(self, ctx):
        logger.info("User command: !stop")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            logger.error("Player is not playing anything")
            await ctx.send("The bot is not playing anything at the moment.", silent=True)

    @commands.command(name="skip", help="Skips the currently playing song")
    async def skip(self, ctx):
        logger.info("User command: !skip")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            self.queue.pop(0)
            if len(self.queue) > 0:
                await self.play_music(ctx)
        else:
            logger.error("Queue is empty")
            await ctx.send("Queue is empty", silent=True)

    @commands.command("shuffle", help="Shuffles the queue")
    async def shuffle(self, ctx):
        if len(self.queue) > 2:
            queue_without_current_song = self.queue[1:]
            random.shuffle(queue_without_current_song)
            self.queue = [self.queue[0]] + queue_without_current_song
            random.shuffle(self.queue)
            await ctx.send("**Queue shuffled**", silent=True)
        else:
            await ctx.send("Queue is too short to shuffle", silent=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Clears the queue when the bot is no longer in a voice channel.

        TODO: disconnect bot after 5 minutes of inactivity
        """
        if member == self.bot.user:
            if not after.channel:
                self.queue.clear()

    async def play_music(self, ctx) -> None:
        logger.info("Attempting to play music...")
        while len(self.queue) > 0:
            # Play next song in queue
            async with ctx.typing():
                player = await YouTubeDownloader.from_query(self.queue[0], loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print("Player error: %s" % e) if e else None)
            logger.debug(f"Playing '{player.title}'")
            message = await ctx.send(f"**Now playing**: {player.title}", silent=True)

            # Wait for the song to finish playing
            while ctx.voice_client.is_playing():
                await asyncio.sleep(1)

            self.queue.pop(0)
            await message.delete()
            if len(self.queue) == 0:
                logger.info("Music queue ended")


class Spotify:
    def __init__(self):
        self.access_token = ""
        self.login()

    def login(self):
        logger.info("Logging in to Spotify...")
        auth_string = base64.b64encode((f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}").encode()).decode()
        headers = {"Authorization": f"Basic {auth_string}"}
        data = {"grant_type": "client_credentials"}
        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            logger.info("Spotify login successful")
        else:
            logger.error("Spotify login failed")
            logger.debug(response.json())

    def get_tracks(self, link: str) -> list[str]:
        track_list = list()
        if "track" in link:
            track_id = link.split("/")[-1]
            logger.info(f"Getting info on track with ID {track_id}...")
            url = f"https://api.spotify.com/v1/tracks/{track_id}"
            response = requests.get(url, headers={"Authorization": f"Bearer {self.access_token}"})
            if response.status_code == 200:
                track_info = response.json()
                name = track_info["name"]
                artist = track_info["artists"][0]["name"]
                track = f"{artist} - {name}"
                track_list.append(track)
            elif response.status_code == 401:
                logger.warning("Access token expired. Logging in again...")
                self.login()
                return self.get_tracks(link)
        elif "playlist" in link:
            playlist_id = link.split("/")[-1]
            logger.info(f"Getting info on playlist with ID {playlist_id}...")
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
            response = requests.get(url, headers={"Authorization": f"Bearer {self.access_token}"})
            if response.status_code == 200:
                for item in response.json()["tracks"]["items"]:
                    track = item["track"]
                    name = track["name"]
                    artist = track["artists"][0]["name"]
                    track_list.append(f"{artist} - {name}")
            elif response.status_code == 401:
                logger.warning("Access token expired. Logging in again...")
                self.login()
                return self.get_tracks(link)
        return track_list


class YouTubeDownloader(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_query(cls, query, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        format_options = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "default_search": "auto",
            "nocheckcertificate": True,
            "logtostderr": False,
            "nowarnings": True,
            "ignoreerrors": True,
            "source_address": "0.0.0.0",
        }
        ffmpeg_options = {
            "options": "-vn",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        }

        data = await loop.run_in_executor(
            None, lambda: youtube_dl.YoutubeDL(format_options).extract_info(query, download=False)
        )
        if "entries" in data:  # type: ignore
            data = data["entries"][0]  # type: ignore
        url = data["url"]  # type: ignore

        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data=data)  # type: ignore
