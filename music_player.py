import os
import asyncio
import discord
import spotipy
import yt_dlp as youtube_dl

from dotenv import load_dotenv
from discord.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials

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
            elif ctx.voice_client.channel != author_voice_channel:
                await ctx.send("The bot is already connected to a different voice channel.")
                return
        else:
            await ctx.send("You are not connected to a voice channel. Please connect to a voice channel first.")
            return

        # Add track(s) to queue
        if "open.spotify.com" in query:
            tracks = self.spotify_helper.get_tracks(query)
            if tracks:
                self.queue.extend(tracks)
        else:
            self.queue.append(query)

        if not ctx.voice_client.is_playing():
            await self.play_music(ctx)
        else:
            await ctx.send(f"**Song added to queue**")

    @commands.command(name="pause", help="Pauses the currently playing song")
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name="resume", help="Resumes a currently paused song")
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything. Use the **play** command to play a song.")

    @commands.command("stop", help="Stops playing song and disconnects the bot from voice channel")
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name="skip", help="Skips the currently playing song")
    async def skip(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            self.queue.pop(0)
            if len(self.queue) > 0:
                await self.play_music(ctx)
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    async def play_music(self, ctx) -> None:
        while len(self.queue) > 0:
            # Play next song in queue
            async with ctx.typing():
                player = await YouTubeDownloader.from_query(self.queue[0], loop=self.bot.loop)
                ctx.voice_client.play(player, after=lambda e: print("Player error: %s" % e) if e else None)
            await ctx.send(f"**Now playing**: {player.title}")

            # Wait for the song to finish playing
            while ctx.voice_client.is_playing():
                await asyncio.sleep(1)

            self.queue.pop(0)


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
            print(results)
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
        ffmpeg_options = {"options": "-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"}

        data = await loop.run_in_executor(
            None, lambda: youtube_dl.YoutubeDL(format_options).extract_info(query, download=False)
        )
        if "entries" in data:  # type: ignore
            data = data["entries"][0]  # type: ignore
        url = data["url"]  # type: ignore

        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data=data)
