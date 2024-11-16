import asyncio
import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path

import discord
from discord.ext import commands


def logger_init() -> None:
    """Create logger
    """
    logger = logging.getLogger('discord')
    logger.setLevel(logging.ERROR)
    logging.getLogger('discord.http').setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='debug.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,
        backupCount=5,
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def config_write():
    config_path = Path("config.json")
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, separators=(',', ': '))


def get_prefix(client, message):
    return config["servers"][str(message.guild.id)]["prefix"], 'm!'


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

startupDate = datetime.now(timezone.utc)
bot = commands.Bot(command_prefix = get_prefix, help_command=None, intents=intents)
config_path = Path("config.json")
with config_path.open("r", encoding="utf-8") as config_file:
    config = json.load(config_file)


@bot.event
async def on_ready():
    await bot.tree.sync()
    activity = discord.Game(name="m!help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"[{startupDate.isoformat(sep=' ')}] Makima is online now!")


@bot.event
async def on_guild_join(guild):
    config["servers"].update({
        str(guild.id):
        {
            "prefix": "m!",
            "joinMessageChannel": "",
            "leaveMessageChannel": "",
            "joinMessage": "{} joined the server!",
            "leaveMessage": "{} left the server!",
        }
    })
    config_write()


@bot.event
async def on_guild_remove(guild):
    del config["servers"][str(guild.id)]
    config_write()


async def main():
    extensions = ["basic", "gifs", "play_youtube"]
    for extension in extensions:
        await bot.load_extension("extensions." + extension)
    await bot.start(config["discord_token"])


if __name__ == "__main__":
    logger_init()
    asyncio.run(main())
