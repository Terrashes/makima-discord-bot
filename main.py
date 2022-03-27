import discord
from discord.ext import commands, tasks
import random
from datetime import *
import json
import requests
import os, platform



# -----------ONLY FOR TESTING----------

from settings import tokenKey
TOKEN = tokenKey

# --------UNCOMMENT FOR DEPLOY---------

# from keep_alive import keep_alive
# TOKEN = os.environ.get("TOKEN")
# keep_alive()

# -------------------------------------


def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)], 'm!'


intents = discord.Intents.all()
startupDate = datetime.now()
bot = commands.Bot(command_prefix = get_prefix, help_command=None, intents=intents)


@bot.event
async def on_ready():
    startupDate = datetime.now()
    activity = discord.Game(name="m!help")
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
    embed.add_field(name="Use `prefix` to change server prefix.",
                    value=('Current server prefix is `{}`.'.format(prefix)), inline=False)
    embed.add_field(name="Use `status` to check bot's statistics.",
                    value=("This command doesn't have any arguments."), inline=False)
    embed.add_field(name="Use `purge` to delete latest messages in chat.",
                    value=("Sample: `purge 10` (Deletes latest 10 messages in chat.)\n Alternatives: `p`, `cls`, `clear`, `del`, `delete`"), inline=False)
    embed.add_field(name="Use `avatar` to view user's avatar.",
                    value=("Sample: `avatar @user` (Shows author's avatar if no user has been mentioned.)"), inline=False)
    embed.add_field(name="Use `mid` to decide who's going to mid.",
                    value=("This command doesn't have any arguments."), inline=False)
    embed.add_field(name='Use `roll` to roll a random number.',
                    value=("Sample: `roll 1 1000` (By default it's rolling in 1-100 interval.)"), inline=False)
    embed.add_field(name='Use `flip` to flip a coin.',
                    value=("Sample: `flip head` (Guess side of the coin using `head/tail` after command)"), inline=False)
    embed.add_field(name='❗Hey! Check out some new GIF commands!',
                    value=("`fuck`, `kiss`, `pat`, `kick`, `shy`, `slap`, `spank`, `deadinside`"), inline=False)
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
    startupDelta = (datetime.now() - startupDate)
    startupDelta_s = startupDelta.total_seconds()
    startupDelta_days = startupDelta.days
    startupDelta_days = divmod(startupDelta_s, 86400)
    startupDelta_hour = divmod(startupDelta_days[1], 3600)
    startupDelta_min = divmod(startupDelta_hour[1], 60)
    startupDelta_sec = divmod(startupDelta_min[1], 1)
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    serverCount = len(prefixes)
    embed = discord.Embed(color=0xff6961, title="Bot's uptime", description="Uptime: {} days, {} hours, {} min, {} sec".format(int(startupDelta_days[0]), int(startupDelta_hour[0]), int(startupDelta_min[0]), int(startupDelta_sec[0])))
    embed.add_field(
        name="Last started",
        value = (startupDate.strftime("`%H:%M:%S` `%d.%m.%Y`")), inline=False)
    embed.add_field(
        name="Servers",
        value=("Working on `{} servers`".format(serverCount)), inline=False)
    embed.add_field(
        name="Latency",
        value=("Bot's ping is `{} ms`".format(int(bot.latency*1000//1))), inline=False)
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
        await ctx.channel.send('Current prefix is `{}` Server prefix changed.'.format(prefixes[str(ctx.guild.id)]))


# ------------ROLL GAMES, ETC-------------


@bot.command(pass_context=True)
async def roll(ctx, minRoll=0, maxRoll=100):
    await ctx.reply(getRandom(minRoll, maxRoll))


@bot.command(pass_context=True)
async def mid(ctx):
    userRoll = getRandom(1, 100)
    botRoll = getRandom(1, 100)
    if int(userRoll) > int(botRoll):
        midResult = "You rolled " + userRoll + "\n" + "Me rolled " + botRoll + "\n" + userRoll + " > " + botRoll + "\n" + "Mid is yours, going to ruin"
    elif int(userRoll) < int(botRoll):
        midResult = "You rolled " + userRoll + "\n" + "Me rolled " + botRoll + "\n" + userRoll + " < " + botRoll + "\n" + "Ez mid, ez life"
    else:
        midResult = "You rolled " + userRoll + "\n" + "Me rolled " + botRoll + "\n" + "Ебаать, ты хоть знаешь какой шанс такое рольнуть? Реролл"
    await ctx.reply(midResult)


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
    embed.add_field(name = targetPerson, value="Click [Here](%s) to download picture." % targetAvatar, inline=False)
    embed.set_image(url=targetAvatar)
    await ctx.channel.send(embed=embed)


def getRandom(min, max):
    return str(random.randint(int(min), int(max)))


# ------------JOIN lEAVE MESSAGES-------------


@bot.command()
async def onjoin(ctx):
    global joinChannel
    joinChannel = ctx.channel
    await ctx.channel.send("Now notification about new members will be shown in this channel")
    

@bot.event
async def on_member_join(Member):
    await joinChannel.send("{} just joined the server!".format(Member.mention))


@bot.command()
async def onleave(ctx):
    global leaveChannel
    leaveChannel = ctx.channel
    await ctx.channel.send("Now notification about new members will be shown in this channel")
    

@bot.event
async def on_member_remove(Member):
    await leaveChannel.send("{} just leaved the server!".format(Member.mention))


bot.load_extension("gifs")
from music import check_queue,search_song,play_song
bot.load_extension("music")
bot.run(TOKEN)