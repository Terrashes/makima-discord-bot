import os
import random

import discord
from discord.ext import commands

from main import bot


@commands.command()
async def deadinside(ctx):
    file, embed = getGif(deadinside, ctx.author)
    await ctx.channel.send(file=file, embed=embed)


@commands.command()
async def fuck(ctx, targetPerson: discord.Member=None):
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return
    file, embed = getGif(fuck, ctx.author, targetPerson)
    await ctx.channel.send(file=file, embed=embed)


@commands.command()
async def kick(ctx, targetPerson: discord.Member=None):
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return
    file, embed = getGif(kick, ctx.author, targetPerson)
    await ctx.channel.send(file=file, embed=embed)


@commands.command()
async def kiss(ctx, targetPerson: discord.Member=None):
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return
    file, embed = getGif(kiss, ctx.author, targetPerson)
    await ctx.channel.send(file=file, embed=embed)


@commands.command()
async def pat(ctx, targetPerson: discord.Member=None):
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return
    file, embed = getGif(pat, ctx.author, targetPerson)
    await ctx.channel.send(file=file, embed=embed)


@commands.command()
async def shy(ctx):
    file, embed = getGif(shy, ctx.author)
    await ctx.channel.send(file=file, embed=embed)


@commands.command()
async def slap(ctx, targetPerson: discord.Member=None):
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return
    file, embed = getGif(slap, ctx.author, targetPerson)
    await ctx.channel.send(file=file, embed=embed)


@commands.command()
async def spank(ctx, targetPerson: discord.Member=None):
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return
    file, embed = getGif(spank, ctx.author, targetPerson)
    await ctx.channel.send(file=file, embed=embed)


def getGif(command, author, targetPerson: discord.Member=None):
    DIR = f"media/{command}/"
    filesAll = [name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]
    gif = f"media/{command}/{random.choice(filesAll)}"
    file = discord.File(gif, filename="image.gif")

    if not targetPerson:
        actions = {
            'deadinside': f'{author.mention} is dead inside.',
            'shy': f'{author.mention} is {command}'
        }
    else:
        actions = {
            'fuck': f'{author.name} {command}s {targetPerson.mention}',
            'kick': f'{author.name} {command}s {targetPerson.mention}',
            'kiss': f'{author.name} {command}es {targetPerson.mention}',
            'pat': f'{author.name} {command}s {targetPerson.mention}',
            'slap': f'{author.name} {command}s {targetPerson.mention}',
            'spank': f'{author.name} {command}s {targetPerson.mention}',
        }
    description = actions[str(command)]
    if str(command) != 'kick' and str(targetPerson) == "Makima Ch.#7921":
        description += '\n😳'
    embed = discord.Embed(color=0xff6961, description=description)
    embed.set_image(url="attachment://image.gif")
    return file, embed


async def setup(bot):
    commands_to_add = [deadinside, shy, fuck, kick, kiss, pat, slap, spank]
    for command in commands_to_add:
        bot.add_command(command)
