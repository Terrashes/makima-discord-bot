import discord
from discord.ext import commands, tasks
import random
from datetime import *
import json
import requests
import os
from twitchAPI import Twitch
from discord.utils import get

# -----------ONLY FOR TESTING----------

# from settings import tokenKey
# TOKEN = tokenKey

# --------UNCOMMENT FOR DEPLOY---------

from keep_alive import keep_alive
TOKEN = os.environ.get("TOKEN")
keep_alive()

# -------------------------------------

def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)], 'm!'


intents = discord.Intents.all()
startupDate = datetime.now()
bot = commands.Bot(command_prefix = get_prefix, help_command=None, intents=intents)


client_id = "r2k16dz59hslwf85ymgj6fenbomws2"
client_secret = "an3wsp2p0slk5f0v0czdq8dwe4ru7r"
twitch = Twitch(client_id, client_secret)
twitch.authenticate_app([])
TWITCH_STREAM_API_ENDPOINT_V5 = "https://api.twitch.tv/kraken/streams/{}"
API_HEADERS = {
    'Client-ID': client_id,
    'Accept': 'application/vnd.twitchtv.v5+json',
}


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
    embed.add_field(name="Use `uptime` to check bot's statistics.",
                    value=("This command doesn't have any arguments."), inline=False)
    embed.add_field(name="Use `purge` to delete latest messages in chat.",
                    value=("Sample: `purge 10` (Deletes latest 10 messages in chat.)"), inline=False)
    embed.add_field(name="Use `avatar` to view user's avatar.",
                    value=("Sample: `avatar @user` (if u don't mention any user it shows your avatar.)"), inline=False)
    embed.add_field(name="Use `mid` to decide who's going to mid.",
                    value=("This command doesn't have any arguments."), inline=False)
    embed.add_field(name='Use `roll` to roll a random number.',
                    value=("Sample: `roll 1 1000` (By default it's rolling in 1-100 interval.)"), inline=False)
    embed.add_field(name='Use `flip` to flip a coin.',
                    value=("Sample: `flip head` (U can guess side of the coin using `head/tail` after command)"), inline=False)
    embed.add_field(name='There are some new gif commands:',
                    value=("`fuck`, `kiss`, `pat`, `kick`, `shy`, `slap`, `spank`, `deadinside`"), inline=False)
    await ctx.send(embed = embed)


@bot.command(pass_context=True)
@commands.has_permissions(administrator = True)
async def purge(ctx, amount):
    await ctx.channel.send("Deleting {} messages.".format(amount))
    await ctx.message.channel.purge(limit=int(amount) + 2)


@bot.command(pass_context=True)
async def uptime(ctx):
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
        value = (startupDate), inline=False)
    embed.add_field(
        name="Servers",
        value=("Working on {} servers".format(serverCount)), inline=False)
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


@bot.command()
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))


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


# ------------GIF ACTIONS-------------


@bot.command()
async def fuck(ctx, targetPerson: discord.User=None):
    action = fuck
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return    
    file = discord.File(getGif(action), filename="image.gif")
    embed = discord.Embed(color=0xff6961,
        description = '{} {}s {}'.format(ctx.author.name, action, targetPerson.mention))
    embed.set_image(url="attachment://image.gif")
    await ctx.channel.send(file=file, embed=embed)


@bot.command()
async def kick(ctx, targetPerson: discord.User=None):
    action = kick
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return    
    file = discord.File(getGif(action), filename="image.gif")
    embed = discord.Embed(color=0xff6961,
        description = '{} {}s {}'.format(ctx.author.name, action, targetPerson.mention))
    embed.set_image(url="attachment://image.gif")
    await ctx.channel.send(file=file, embed=embed)


@bot.command()
async def kiss(ctx, targetPerson: discord.User=None):
    action = kiss
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return    
    file = discord.File(getGif(action), filename="image.gif")
    embed = discord.Embed(color=0xff6961,
        description = '{} {}es {}'.format(ctx.author.name, action, targetPerson.mention))
    embed.set_image(url="attachment://image.gif")
    await ctx.channel.send(file=file, embed=embed)


@bot.command()
async def pat(ctx, targetPerson: discord.User=None):
    action = pat
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return    
    file = discord.File(getGif(action), filename="image.gif")
    embed = discord.Embed(color=0xff6961,
        description = '{} {}s {}'.format(ctx.author.name, action, targetPerson.mention))
    embed.set_image(url="attachment://image.gif")
    await ctx.channel.send(file=file, embed=embed)


@bot.command()
async def slap(ctx, targetPerson: discord.Member=None):
    action = slap
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return    
    file = discord.File(getGif(action), filename="image.gif")
    embed = discord.Embed(color=0xff6961,
        description = '{} {}s {}'.format(ctx.author.name, action, targetPerson))
    embed.set_image(url="attachment://image.gif")
    await ctx.channel.send(file=file, embed=embed)


@bot.command()
async def spank(ctx, targetPerson: discord.Member=None):
    action = spank
    if not targetPerson:
        await ctx.channel.send('To use this command please mention any user.')
        return    
    file = discord.File(getGif(action), filename="image.gif")
    embed = discord.Embed(color=0xff6961,
        description = '{} {}s {}'.format(ctx.author.name, action, targetPerson))
    embed.set_image(url="attachment://image.gif")
    await ctx.channel.send(file=file, embed=embed)
        

@bot.command()
async def shy(ctx):
    action = shy 
    file = discord.File(getGif(action), filename="image.gif")
    embed = discord.Embed(color=0xff6961,
        description = '{} is {}'.format(ctx.author.name, action))
    embed.set_image(url="attachment://image.gif")
    await ctx.channel.send(file=file, embed=embed)


@bot.command()
async def deadinside(ctx):
    action = deadinside 
    file = discord.File(getGif(action), filename="image.gif")
    embed = discord.Embed(color=0xff6961,
        description = '{} is dead inside.'.format(ctx.author.name))
    embed.set_image(url="attachment://image.gif")
    await ctx.channel.send(file=file, embed=embed)


def getGif(command):
    DIR = "img/{}/".format(command)
    filesAll = [name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]
    return "img/{}/{}".format(command, random.choice(filesAll))

bot.run(TOKEN)