import asyncio
import discord
import yt_dlp as youtube_dl


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
