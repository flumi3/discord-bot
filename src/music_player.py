import os
import asyncio
import logging
import random
import discord
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
        self.spotify_helper = SpotifyHelper()

    @commands.command(name="play", help="Plays a song")
    async def play(self, ctx, *, query: str):
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
        if "open.spotify.com" in query:
            tracks = self.spotify_helper.get_tracks(query)
            if tracks:
                self.queue.extend(tracks)
                logger.info(f"Added {len(tracks)} tracks to queue")
        else:
            self.queue.append(query)
            logger.info(f"Added '{query}' to queue")

        if not ctx.voice_client.is_playing():
            await self.play_music(ctx)
        else:
            await ctx.send(f"Song added to queue", silent=True)

    @commands.command(name="pause", help="Pauses the currently playing song")
    async def pause(self, ctx):
        logger.info("Attempting to pause player...")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
        else:
            logger.error("Player is not playing anything")
            await ctx.send("The bot is not playing anything at the moment.", silent=True)

    @commands.command(name="resume", help="Resumes a currently paused song")
    async def resume(self, ctx):
        logger.info("Attempting to resume player...")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        else:
            logger.error("Bot was not playing anything")
            await ctx.send("The bot was not playing anything. Use **!play <name_of_song>** to play a song.")

    @commands.command("stop", help="Stops playing song and disconnects the bot from voice channel")
    async def stop(self, ctx):
        logger.info("Attempting to stop player...")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            logger.error("Player is not playing anything")
            await ctx.send("The bot is not playing anything at the moment.", silent=True)

    @commands.command(name="skip", help="Skips the currently playing song")
    async def skip(self, ctx):
        logger.info("Attempting to skip song...")
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


class SpotifyHelper:
    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
        )
        self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def get_tracks(self, link: str) -> list[str]:
        if "track" in link:
            track_info = self.spotify.track(link)
            if track_info:
                name = track_info["name"]
                artist = track_info["artists"][0]["name"]
                track = f"{name} {artist}"
                return [track]
        elif "playlist" in link:
            results = self.spotify.playlist_items(link)
            if results:
                track_list = []
                for item in results["items"]:
                    track = item["track"]
                    name = track["name"]
                    artist = track["artists"][0]["name"]
                    track_list.append(f"{name} {artist}")
                return track_list
        return []


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

        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data=data)
