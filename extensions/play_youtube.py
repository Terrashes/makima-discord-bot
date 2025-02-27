import asyncio
from typing import Any

import discord
import yt_dlp
from discord.ext import commands

from main import bot

FFMPEG_OPTIONS: dict[str, str] = {'options': '-vn'}
YDL_OPTIONS = {
    'format': 'bestaudio',
    'noplaylist': True,
    'cookiefile': 'yt_cookies.txt'
    }
yt_queue = []


@commands.hybrid_command(name="play", with_app_command=True, description="Play youtube video")
async def play(ctx, *, search) -> None:
    voice_channel = ctx.author.voice.channel if ctx.author.voice else None
    if not voice_channel:
        return await ctx.send("You're not in voice channel")
    if not ctx.voice_client:
        await voice_channel.connect()

    async with ctx.typing():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url = info['url']
            title = info['title']
            yt_queue.append((url, title))
            await ctx.send(f"Added to queue: **{title}**")
    if not ctx.voice_client.is_playing():
        await play_next(ctx=ctx)


async def play_next(ctx):
    if yt_queue:
        url, title = yt_queue.pop(0)
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        ctx.voice_client.play(source,
                              after=lambda _: asyncio.run_coroutine_threadsafe(play_next(ctx),
                                                                               asyncio.get_running_loop())
                              )
    elif not ctx.voice_client.is_playing():
        await ctx.send('Queue is empty')


@commands.hybrid_command(name="skip", with_app_command=True, description="Skip youtube video")
async def skip(ctx) -> None:
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('Skipped')


async def setup(bot) -> None:
    commands_to_add = [play, skip]
    for command in commands_to_add:
        bot.add_command(command)
