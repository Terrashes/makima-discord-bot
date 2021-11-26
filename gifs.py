import discord
from discord.ext import commands
import os
import random
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
    DIR = "img/{}/".format(command)
    filesAll = [name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]
    gif = "img/{}/{}".format(command, random.choice(filesAll))
    file = discord.File(gif, filename="image.gif")
    
    if not targetPerson:
        actions = {
            'deadinside' : '{} is dead inside.'.format(author.mention),
            'shy' : '{} is {}'.format(author.mention, command),
        }
    else: 
        actions = {  
            'fuck' : '{} {}s {}'.format(author.name, command, targetPerson.mention),               
            'kick' : '{} {}s {}'.format(author.name, command, targetPerson.mention),
            'kiss' : '{} {}es {}'.format(author.name, command, targetPerson.mention),
            'pat' : '{} {}s {}'.format(author.name, command, targetPerson.mention),
            'slap' : '{} {}s {}'.format(author.name, command, targetPerson.mention),
            'spank' : '{} {}s {}'.format(author.name, command, targetPerson.mention), 
        }
    description = actions[str(command)]
    if targetPerson == bot.user:
        description += '\n😳'
    embed = discord.Embed(color=0xff6961, description = description)
    embed.set_image(url="attachment://image.gif")
    return file, embed


def setup(bot):
    commands = [deadinside, shy, fuck, kick, kiss, pat, slap, spank]
    for i in range(0, len(commands)):
        bot.add_command(commands[i])