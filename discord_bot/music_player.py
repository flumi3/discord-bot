import base64
import os
import asyncio
import logging
import random
import discord
import requests
import yt_dlp as youtube_dl

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord.ext import commands

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
        self.loop_queue = False

    @commands.command(
        name="play",
        help="Plays a song",
    )
    async def play(self, ctx, *, query: str):
        """Plays a song from YouTube or Spotify

        Args:
            query (str): Song to play (link or name)
        """
        logger.info(f"User {ctx.author} invoked command: !play {query}")

        # Connect to voice channel
        if ctx.message.author.voice:
            author_voice_channel = ctx.message.author.voice.channel
            if not ctx.voice_client:
                await author_voice_channel.connect()
                self.ctx = ctx
                logger.info(f"Bot connected to voice channel '{author_voice_channel}'")
            elif ctx.voice_client.channel != author_voice_channel:
                await ctx.send("I am already connected to a different voice channel.", silent=True)
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

        # Get track name
        if "youtube.com" in query:
            track_name = self.get_youtube_title(query)
        else:
            track_name = tracks[0]
        track_name = track_name.lower()

        # Easter egg: Loop if the track is Walmart Yodeling Kid
        if "kid" in track_name and "walmart" in track_name and "edm" in track_name:
            await ctx.send(
                ":rotating_light: Walmart yodeling kid detected. Loop enabled :rotating_light:", silent=True
            )
            if not self.loop_queue:
                self.loop_queue = True

        # Easter egg: Send Money Boy image if track is with Money Boy
        if "money boy" in track_name:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            folder_path = root_dir + "/data/moneyboy-img"
            all_items = os.listdir(folder_path)
            files = [item for item in all_items if os.path.isfile(os.path.join(folder_path, item))]
            file = random.choice(files)
            file_path = os.path.join(folder_path, file)
            await ctx.send(file=discord.File(file_path), silent=True)

        # Play music
        if not ctx.voice_client.is_playing():
            await self.play_music(ctx)
        else:
            if len(tracks) == 1:
                await ctx.send(f"**Added to queue**: {track_name}", silent=True)
            elif len(self.queue) > 1:
                await ctx.send(f"Added {len(tracks)} tracks to queue", silent=True)

    @commands.command(name="pause", help="Pauses the currently playing song")
    async def pause(self, ctx):
        logger.info(f"User {ctx.author} invoked command: !pause")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
        else:
            logger.error("Player is not playing anything")
            await ctx.send("I am is not playing anything at the moment.", silent=True)

    @commands.command(name="resume", help="Resumes a currently paused song")
    async def resume(self, ctx):
        logger.info(f"User {ctx.author} invoked command: !resume")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        else:
            logger.error("Bot was not playing anything")
            await ctx.send("I was not playing anything. Use **!play <name_of_song>** to play a song.")

    @commands.command("stop", help="Stops playing song and disconnects the bot from voice channel")
    async def stop(self, ctx):
        logger.info(f"User {ctx.author} invoked command: !stop")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            if len(self.queue) > 0:
                self.queue.clear()
            voice_client.stop()
            logger.info("Stopped playing music")
        else:
            logger.error("Player is not playing anything")
            await ctx.send("I was not playing anything at the moment.", silent=True)

    @commands.command(name="skip", help="Skips the currently playing song")
    async def skip(self, ctx):
        logger.info(f"User {ctx.author} invoked command: !skip")
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            self.pop_queue()
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

    @commands.command("clear", help="Clears the music queue")
    async def clear_queue(self, ctx):
        logger.info(f"User {ctx.author} invoked command: !clear")
        if len(self.queue) > 0:
            self.queue.clear()
            await ctx.send("Queue cleared", silent=True)
        else:
            await ctx.send("Queue is empty", silent=True)

    @commands.command("queue", help="Shows the current queue")
    async def show_queue(self, ctx):
        logger.info(f"User {ctx.author} invoked command: !queue")
        if len(self.queue) > 0:
            queue = ""
            for i, track in enumerate(self.queue):
                if i != 0:
                    queue += f"{i}. {track}\n"
            await ctx.send(f"**Queue**:\n{queue}", silent=True)

    @commands.command("loop", help="Enable/Disable loop")
    async def loop(self, ctx):
        logger.info(f"User {ctx.author} invoked command: !loop")
        self.loop_queue = not self.loop_queue
        if self.loop_queue:
            await ctx.send("Looping queue", silent=True)
        else:
            await ctx.send("Un-looping queue", silent=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after) -> None:
        """Disconnect bot from voice channel after a certain amount of inactivity

        Args:
            member (discord.Member): Member that changed voice state
            before (discord.VoiceState): Voice state before change
            after (discord.VoiceState): Voice state after change
        """
        inactivity_limit = 30  # minutes of inactivity before bot disconnects
        inactivity_counter = 0  # in minutes

        # check if bot is connected to a voice channel
        if not member.id == self.bot.user.id:
            return
        elif before.channel is None:
            # wait until bot is inactive
            voice_client = after.channel.guild.voice_client
            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(1)
            else:
                while True:
                    # wait until bot is inactive for the specified time
                    await asyncio.sleep(60)
                    if voice_client.is_playing() and not voice_client.is_paused():
                        inactivity_counter = 0
                    else:
                        inactivity_counter += 1
                        logger.info(f"Bot inactive since {inactivity_counter} minutes")
                    if inactivity_counter == inactivity_limit:
                        logger.info(f"Disconnecting from voice channel '{voice_client.channel}'...")
                        await voice_client.disconnect()
                        await self.ctx.send(f"Disconnected from voice channel due to inactivity.", silent=True)
                        logger.info(f"Disconnected")
                        break

    async def play_music(self, ctx) -> None:
        logger.info("Attempting to play music...")
        while len(self.queue) > 0:
            # Play next song in queue
            async with ctx.typing():
                player = await YouTubeDownloader.from_query(self.queue[0], loop=self.bot.loop)  # type: ignore
                ctx.voice_client.play(player, after=lambda e: print("Player error: %s" % e) if e else None)
            logger.debug(f"Playing '{player.title}'")
            message = await ctx.send(f"**Now playing**: {player.title}", silent=True)

            # Wait for the song to finish playing
            while ctx.voice_client and ctx.voice_client.is_playing():
                await asyncio.sleep(1)

            if ctx.voice_client.is_paused():
                break
            else:
                self.pop_queue()
                await message.delete()
                if len(self.queue) == 0:
                    logger.info("Music queue ended")

    def pop_queue(self) -> None:
        if self.queue and len(self.queue) > 0:
            if self.loop_queue:
                self.queue.append(self.queue[0])
            self.queue.pop(0)

    def get_youtube_title(self, url: str) -> str:
        logger.info(f"Fetchig YouTube video title for URL {url}...")
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("title")
            if title:
                logger.debug(f"Found title: {title.text}")
                return title.text
        except Exception as e:
            logger.error(f"Failed to fetch YouTube video title for URL {url}. Error: {str(e)}")
        return ""


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
        logger.debug(f"Fetching YouTube video for query '{query}'...")
        loop = loop or asyncio.get_event_loop()
        ytl_options = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "default_search": "auto",
            "nocheckcertificate": True,
            "logtostderr": False,
            "nowarnings": True,
            "ignoreerrors": True,
            "source_address": "0.0.0.0",
            "cookiefile": "cookies.txt",
            "verbose": False,
            "quiet": True,
        }
        ffmpeg_options = {
            "options": "-vn",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        }

        data = await loop.run_in_executor(
            None, lambda: youtube_dl.YoutubeDL(ytl_options).extract_info(query, download=False)
        )
        if "entries" in data:  # type: ignore
            data = data["entries"][0]  # type: ignore
        url = data["url"]  # type: ignore

        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data=data)  # type: ignore
