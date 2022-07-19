import discord
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle
import random
from datetime import *
import json
import requests
import os, platform


with open("config.json", "r") as f:
        TOKEN = json.load(f)["tokenKey"]


def get_prefix(client, message):
    with open("config.json", "r") as f:
        prefixes = json.load(f)["prefixes"]
    return prefixes[str(message.guild.id)], 'm!'


intents = discord.Intents.all()
startupDate = datetime.now()
bot = commands.Bot(command_prefix = get_prefix, help_command=None, intents=intents)


def beautifyDateDelta(date):
    timeDelta = (datetime.now() - date)
    timeDeltaDays = timeDelta.days
    timeDeltaSecs = int((timeDelta.total_seconds()-timeDelta.days*86400)//1)
    timeParams = [timeDeltaDays//360, timeDeltaDays%360//30, timeDeltaDays%360%30, timeDeltaSecs//3600, timeDeltaSecs%3600//60, timeDeltaSecs%3600%60]
    return timeParams


@bot.event
async def on_ready():
    startupDate = datetime.now()
    activity = discord.Game(name="m!help")
    DiscordComponents(bot)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("[{}] Makima is online now!".format(startupDate.isoformat(sep=' ')))
    

@bot.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = "m!"
    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)


@bot.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    del prefixes[str(guild.id)]
    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)


# ------------SERVICE COMMANDS-------------


@bot.group(invoke_without_command=True)
async def help(ctx):
    prefix = get_prefix(bot, ctx)[0]
    embed = discord.Embed(title = "Commands Dashboard", color=0xff6961)
    embed.add_field(
        name="Use `prefix` to change server prefix.",
        value=('Current server prefix is `{}`.'.format(prefix)), 
        inline=False)
    embed.add_field(
        name="Use `status` to check bot's statistics.",
        value=("This command doesn't have any arguments."), 
        inline=False)
    embed.add_field(
        name="Use `purge` to delete latest messages in chat.",
        value=("Sample: `purge 10` (Deletes latest 10 messages in chat.)\n Alternatives: `p`, `cls`, `clear`, `del`, `delete`"), 
        inline=False)
    embed.add_field(
        name="Use `avatar` to view user's avatar.",
        value=("Sample: `avatar @user` (Shows author's avatar if no user has been mentioned.)"), 
        inline=False)
    embed.add_field(
        name="Use `info` to view user's profile information.",
        value=("Sample: `info @user` (Shows author's info if no user has been mentioned.)"), 
        inline=False)
    embed.add_field(
        name='Use `roll` to roll a random number.',
        value=("Sample: `roll 1 1000` (By default it's rolling in 1-100 interval.)"), 
        inline=False)
    embed.add_field(
        name='Use `flip` to flip a coin.',
        value=("Sample: `flip head` (Guess side of the coin using `head/tail` after command)"), 
        inline=False)
    embed.add_field(
        name='Use `play` to play youtube audio and `leave` to leave voice channel.',
        value=("Sample: `play https://youtu.be/H3sdfKMKu8E`"), 
        inline=False)
    embed.add_field(
        name="Use `nhentai` to find hentai manga's info by ID.",
        value=("Sample: `nhentai 177013`"), 
        inline=False)
    embed.add_field(
        name='❗Hey! Check out some new GIF commands!',
        value=("`fuck`, `kiss`, `pat`, `kick`, `shy`, `slap`, `spank`, `deadinside`"), 
        inline=False)
    await ctx.send(embed = embed)


@bot.command(aliases=['p', 'cls', 'clear', 'del', 'delete'])
@commands.has_permissions(administrator = True)
async def purge(ctx, amount = None):
    if (amount is None):
        await ctx.channel.send("Please type amount of messages to delete.".format(amount))
    else:
        await ctx.channel.send("Deleting {} messages.".format(amount))
        await ctx.message.channel.purge(limit=int(amount) + 2)


@bot.command(pass_context=True)
async def status(ctx):
    botOnlineDuration = beautifyDateDelta(startupDate)
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    serverCount = len(prefixes)
    embed = discord.Embed(
        color=0xff6961, 
        title="Bot's uptime", 
        description="Uptime: {} days, {} hours, {} min, {} sec".format(botOnlineDuration[2], botOnlineDuration[3], botOnlineDuration[4], botOnlineDuration[5]))
    embed.add_field(
        name="Last started",
        value = (startupDate.strftime("`%H:%M:%S` `%d.%m.%Y`")), inline=False)
    embed.add_field(
        name="Servers",
        value=("Working on `{} servers`".format(serverCount)), inline=False)
    embed.add_field(
        name="Latency",
        value=("Current latency is `{} ms`".format(int(bot.latency*1000//1))), inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator = True)
async def prefix(ctx, prefixValue=""):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    if prefixValue == prefixes[str(ctx.guild.id)]:
        await ctx.channel.send("Current prefix is `{}`. Server prefix didn't change because you specified the same prefix as current.".format(
            prefixes[str(ctx.guild.id)]))
    elif prefixValue == "":
        await ctx.channel.send('Current prefix is `{}`.'.format(prefixes[str(ctx.guild.id)]))
    else:
        prefixes[str(ctx.guild.id)] = prefixValue
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f)
        await ctx.channel.send('Server prefix changed. Current prefix is `{}`.'.format(prefixes[str(ctx.guild.id)]))


# ------------ROLL GAMES, ETC-------------


@bot.command(pass_context=True)
async def roll(ctx, minRoll=None, maxRoll=None):
    if minRoll == None and maxRoll == None:
        minRoll, maxRoll = 0, 100
    elif maxRoll == None:
        maxRoll, minRoll = minRoll, 1
    await ctx.reply(getRandom(minRoll, maxRoll))


@bot.command(pass_context=True)
async def flip(ctx, flipGuess=""):
    flipResult = int(getRandom(1, 2))
    if flipResult == 1:
        flipResult = 'head'
    else:
        flipResult = 'tail'
    flipMessage = "Flipped " + flipResult
    if flipGuess == flipResult:
        flipMessage += " - you guessed right."
    elif flipGuess == 'head' or flipGuess == 'tail':
        flipMessage += " - you didn't guess right."
    else:
        flipMessage += "."
    await ctx.reply(flipMessage)


@bot.command()
async def avatar(ctx, targetPerson:  discord.Member=None):
    if not targetPerson:
        targetPerson = ctx.author
    targetAvatar = targetPerson.avatar_url
    embed = discord.Embed(color=0xff6961)
    embed.add_field(
        name = targetPerson, 
        value="Click [Here](%s) to download picture." % targetAvatar, 
        inline=False)
    embed.set_image(url=targetAvatar)
    await ctx.channel.send(embed=embed)


@bot.command()
async def info(ctx, targetPerson:  discord.Member=None):
    if not targetPerson:
        targetPerson = ctx.author
    rlist = []
    for role in targetPerson.roles:
        if role.name != "@everyone":
            rlist.append(role.mention)
    b = ", ".join(rlist)
    accCreate =  targetPerson.created_at.strftime("`%H:%M:%S` `%d.%m.%Y`")
    accJoin = targetPerson.joined_at.strftime("`%H:%M:%S` `%d.%m.%Y`")
    accCreateDelta = beautifyDateDelta(targetPerson.created_at)
    accJoinDelta = beautifyDateDelta(targetPerson.joined_at)
    embed = discord.Embed(title=targetPerson, color=0xff6961)
    embed.set_thumbnail(url=targetPerson.avatar_url),
    embed.add_field(name='Account created:',value="{} ({} years, {} months, {} days ago)".format(accCreate, accCreateDelta[0], accCreateDelta[1], accCreateDelta[2]), inline=False)
    embed.add_field(name='Joined server:',value="{} ({} years, {} months, {} days ago)".format(accJoin, accJoinDelta[0], accJoinDelta[1], accJoinDelta[2]), inline=False)
    embed.add_field(
        name = "User ID:", 
        value=" {}".format(targetPerson.id), 
        inline=True)
    embed.add_field(name=f'Roles:({len(rlist)})',value=''.join([b]),inline=False)
    embed.add_field(name='Top Role:',value=targetPerson.top_role.mention,inline=False)
    await ctx.channel.send(embed=embed)


def getRandom(min, max):
    return str(random.randint(int(min), int(max)))


# ------------JOIN AND lEAVE MESSAGES-------------


@bot.command()
async def onjoin(ctx):
    global joinChannel
    joinChannel = ctx.channel
    await ctx.channel.send("Now notification about new members will be shown in this channel")
    

@bot.event
async def on_member_join(Member):
    await joinChannel.send("{} just joined the server! Welcome!".format(Member.mention))


@bot.command()
async def onleave(ctx):
    global leaveChannel
    leaveChannel = ctx.channel
    await ctx.channel.send("Now notification about new members will be shown in this channel")
    

@bot.event
async def on_member_remove(Member):
    await leaveChannel.send("{} just leaved the server!".format(Member.mention))


bot.load_extension("gifs")
from music import check_queue, search_song, play_song
bot.load_extension("music")
bot.load_extension("nhentai")
bot.run(TOKEN)