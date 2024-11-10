import os
import sys
import logging
import logging.handlers

from discord.ext import commands


class LogUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = self.init_logging()

    @commands.command(name="logs", help="Shows the last x lines of the log file")
    async def logs(self, ctx, num_of_lines: int = 10):
        with open("logs/discord.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            lines = lines[-num_of_lines:]
            await ctx.send("```" + "".join(lines) + "```")

    def init_logging(self):
        """Initializes logging for the bot"""
        logger = logging.getLogger("discord")
        logger.setLevel(logging.DEBUG)
        logging.getLogger("discord.http").setLevel(logging.INFO)

        # create log folder if not exists
        if not os.path.exists("logs"):
            os.makedirs("logs")

        handler = logging.handlers.RotatingFileHandler(
            filename="logs/discord.log",
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,  # 32 MB
            backupCount=5,  # Rotate through 5 files
        )

        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter("[{asctime}] [{levelname:}] {name}: {message}", date_format, style="{")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
