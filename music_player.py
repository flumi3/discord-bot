import asyncio
import discord
import yt_dlp as youtube_dl
from discord import VoiceState
from discord.ext import commands
from discord.ext.commands import Context

discord.FFmpegPCMAudio("/usr/bin/ffmpeg")


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = list()

    @commands.command(name="play", help="Plays a song")
    async def play(self, ctx, *, query: str):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel. Please connect to a voice channel first.")
            return
        else:
            voice_channel = ctx.message.author.voice.channel
            if not ctx.voice_client:
                await voice_channel.connect()

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

    async def play_music(self, ctx):
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
        ffmpeg_options = {"options": "-vn"}

        data = await loop.run_in_executor(
            None, lambda: youtube_dl.YoutubeDL(format_options).extract_info(query, download=False)
        )
        if "entries" in data:
            data = data["entries"][0]
        url = data["url"]

        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data=data)
