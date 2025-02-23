import os
from typing import Any, Optional

import discord
import numpy as np
from discord.ext import commands

from main import bot


async def get_gif(ctx, command: str, person: Optional[discord.Member] = None) -> None:
    self_commands: list[str] = ["deadinside", "shy"]

    if person is None and command not in self_commands:
        await ctx.send("To use this command, please mention a user.")
        return

    if person is None:
        actions: dict[str, str] = {
            "deadinside": f"{ctx.author.mention} is dead inside.",
            "shy": f"{ctx.author.mention} is {command}",
        }
    else:
        actions = {
            "fuck": f"{ctx.author.name} {command}s {person.mention}",
            "suck": f"{ctx.author.name} {command}s {person.mention}",
            "kick": f"{ctx.author.name} {command}s {person.mention}",
            "kiss": f"{ctx.author.name} {command}es {person.mention}",
            "pat": f"{ctx.author.name} {command}s {person.mention}",
            "slap": f"{ctx.author.name} {command}s {person.mention}",
            "spank": f"{ctx.author.name} {command}s {person.mention}",
        }

    media_folder: str = f"media/{command}/"
    try:
        files_all: list[str] = [
            name
            for name in os.listdir(media_folder)
            if os.path.isfile(os.path.join(media_folder, name))
        ]
        if not files_all:
            await ctx.send("No media files found for this command.")
            return

        mean = len(files_all) / 2
        stddev = len(files_all) / 6
        index = int(np.random.normal(mean, stddev))
        index = max(0, min(len(files_all) - 1, index))
        gif: str = f"{media_folder}/{files_all[index]}"

    except FileNotFoundError:
        await ctx.send("Media folder not found for this command.")
        return

    file = discord.File(gif, filename="image.gif")
    description: str = actions[command]
    if command != "kick" and str(person) == "Makima Ch.#7921":
        description += "\n😳"
    embed = discord.Embed(color=0xFF6961, description=description)
    embed.set_image(url="attachment://image.gif")
    await ctx.send(file=file, embed=embed)


@commands.hybrid_command(
    name="deadinside", with_app_command=True, description="Self dead inside GIF status"
)
async def deadinside(ctx) -> None:
    await get_gif(ctx, "deadinside")


@commands.hybrid_command(
    name="shy", with_app_command=True, description="Shy GIF status"
)
async def shy(ctx) -> None:
    await get_gif(ctx, "shy")


@commands.hybrid_command(
    name="fuck", with_app_command=True, description="Fuck GIF action"
)
async def fuck(ctx, person: discord.Member) -> None:
    await get_gif(ctx, "fuck", person)


@commands.hybrid_command(
    name="suck", with_app_command=True, description="Suck GIF action"
)
async def suck(ctx, person: discord.Member) -> None:
    await get_gif(ctx, "suck", person)


@commands.hybrid_command(
    name="kick", with_app_command=True, description="Kick GIF action"
)
async def kick(ctx, person: discord.Member) -> None:
    await get_gif(ctx, "kick", person)


@commands.hybrid_command(
    name="kiss", with_app_command=True, description="Kiss GIF action"
)
async def kiss(ctx, person: discord.Member) -> None:
    await get_gif(ctx, "kiss", person)


@commands.hybrid_command(
    name="pat", with_app_command=True, description="Pat GIF action"
)
async def pat(ctx, person: discord.Member) -> None:
    await get_gif(ctx, "pat", person)


@commands.hybrid_command(
    name="slap", with_app_command=True, description="Slap GIF action"
)
async def slap(ctx, person: discord.Member) -> None:
    await get_gif(ctx, "slap", person)


@commands.hybrid_command(
    name="spank", with_app_command=True, description="Spank GIF action"
)
async def spank(ctx, person: discord.Member) -> None:
    await get_gif(ctx, "spank", person)


async def setup(bot) -> None:
    commands_to_add: list[Any] = [
        deadinside,
        shy,
        fuck,
        suck,
        kick,
        kiss,
        pat,
        slap,
        spank,
    ]
    for command in commands_to_add:
        bot.add_command(command)
