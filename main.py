import asyncio
import json
import os
import platform
import random
from datetime import *
from urllib import response
from urllib.error import URLError

import discord
import requests
from discord import app_commands
from discord.ext import commands, tasks

with open("config.json", "r") as f:
    config = json.load(f)

import logging
import logging.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='debug.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)


def writeConfig():
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4,
                        separators=(',',': '))

def get_prefix(client, message):
    return config["servers"][str(message.guild.id)]["prefix"], 'm!'


intents = discord.Intents.all()
startupDate = datetime.now(timezone.utc)
bot = commands.Bot(command_prefix = get_prefix, help_command=None, intents=intents)


def beautifyDateDelta(date):
    timeDelta = (datetime.now(timezone.utc) - date)
    timeDeltaDays = timeDelta.days
    timeDeltaSecs = int((timeDelta.total_seconds()-timeDelta.days*86400)//1)
    timeParams = [timeDeltaDays//365, timeDeltaDays%365//30, timeDeltaDays%365%30, timeDeltaSecs//3600, timeDeltaSecs%3600//60, timeDeltaSecs%3600%60]
    return timeParams


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
    writeConfig()


@bot.event
async def on_guild_remove(guild):
    del config["servers"][str(guild.id)]
    writeConfig()


# ------------SERVICE COMMANDS-------------


@bot.group(invoke_without_command=True)
async def help(ctx):
    prefix = get_prefix(bot, ctx)[0]
    embed = discord.Embed(title = "Commands Dashboard", color=0xff6961)
    embed.add_field(
        name="`prefix` to change server prefix.",
        value=('Current server prefix is `{}`.'.format(prefix)),
        inline=False)
    embed.add_field(
        name="`status` to check bot's statistics.",
        value=("This command doesn't have any arguments."),
        inline=False)
    embed.add_field(
        name="`onjoin` and `onleave` to add messages for users who just joined and left server.",
        value=('Sample: `onjoin "Welcome, {}!"` ({} - for mention user)'),
        inline=False)
    embed.add_field(
        name="`purge` to delete latest messages in chat.",
        value=("Sample: `purge 10` (Deletes latest 10 messages in chat.)\n Aliases: `p`, `cls`, `clear`, `del`, `delete`"),
        inline=False)
    embed.add_field(
        name="`avatar` to view user's avatar.",
        value=("Sample: `avatar @user` (Shows author's avatar if no user has been mentioned.)"),
        inline=False)
    embed.add_field(
        name="`info` to view user's profile information.",
        value=("Sample: `info @user` (Shows author's info if no user has been mentioned.)"),
        inline=False)
    embed.add_field(
        name='`roll` to roll a random number.',
        value=("Sample: `roll 1 1000` (By default it's rolling in 1-100 interval.)"),
        inline=False)
    embed.add_field(
        name='`flip` to flip a coin.',
        value=("Sample: `flip head` (Guess side of the coin using `head/tail` after command)"),
        inline=False)
    embed.add_field(
        name='`play` to play youtube audio and `leave` to leave voice channel.',
        value=("Sample: `play https://youtu.be/iWpCdUQLWwU`"),
        inline=False)
    # embed.add_field(
    #     name="`nhentai` to find hentai manga's info by ID.",
    #     value=("Sample: `nhentai 177013`"),
    #     inline=False)
    embed.add_field(
        name='GIF message commands!',
        value=("`fuck`, `kiss`, `pat`, `kick`, `shy`, `slap`, `spank`, `deadinside`"),
        inline=False)
    await ctx.send(embed = embed)


@bot.hybrid_command(name="ping", with_app_command=True, description="Generic slash command")
async def ping(ctx):
    await ctx.send('Pong')


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
    serverCount = len(config["servers"])
    embed = discord.Embed(
        color=0xff6961,
        title="Bot's uptime",
        description="Uptime: {} days, {} hours, {} min, {} sec".format(botOnlineDuration[2], botOnlineDuration[3], botOnlineDuration[4], botOnlineDuration[5]))
    embed.add_field(
        name="Last started",
        value = (startupDate.strftime("`%H:%M:%S` `%d.%m.%Y`")), inline=False)
    embed.add_field(
        name="Servers",
        value=("Working on `{}` servers".format(serverCount)), inline=False)
    embed.add_field(
        name="Latency",
        value=("Current latency is `{}` ms".format(int(bot.latency*1000//1))), inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator = True)
async def prefix(ctx, prefixValue=""):
    if prefixValue == config["servers"][str(ctx.guild.id)]["prefix"]:
        await ctx.channel.send("Current prefix is `{}`. Server prefix didn't change because you specified the same prefix as current.".format(
            config["servers"][str(ctx.guild.id)]["prefix"]))
    elif prefixValue == "":
        await ctx.channel.send('Current prefix is `{}`.'.format(config["servers"][str(ctx.guild.id)]["prefix"]))
    else:
        config["servers"][str(ctx.guild.id)]["prefix"] = prefixValue
        writeConfig()
        await ctx.channel.send('Server prefix changed. Current prefix is `{}`.'.format(config["servers"][str(ctx.guild.id)]["prefix"]))


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
    targetAvatar = targetPerson.avatar
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
    embed.set_thumbnail(url=targetPerson.avatar),
    embed.add_field(name='Account created:',value="{} ({} years, {} months, {} days ago)".format(accCreate, accCreateDelta[0], accCreateDelta[1], accCreateDelta[2]), inline=False)
    embed.add_field(name='Joined server:',value="{} ({} years, {} months, {} days ago)".format(accJoin, accJoinDelta[0], accJoinDelta[1], accJoinDelta[2]), inline=False)
    embed.add_field(
        name = "User ID:",
        value=" {}".format(targetPerson.id),
        inline=True)
    embed.add_field(name=f'Roles ({len(rlist)}) :',value=''.join([b]),inline=False)
    embed.add_field(name='Top Role:',value=targetPerson.top_role.mention,inline=False)
    await ctx.channel.send(embed=embed)


@bot.command()
async def checkip(ctx, ip=None):
    API_Token = '3617fbb4249944f61316ede0496c9bc5'
    response = requests.get('http://api.ipapi.com/{}?access_key={}&output=json'.format(ip, API_Token)).json()
    embed = discord.Embed(title='Info about {}'.format(ip), color=0xff6961)
    embed.add_field(name='Region:',value=response['region_name'], inline=False)
    embed.add_field(name='City',value=response['city'], inline=False)
    embed.add_field(name='Latitude:',value=response['latitude'], inline=False)
    embed.add_field(name='Longitude:',value=response['longitude'], inline=False)
    await ctx.channel.send(embed=embed)


def getRandom(min, max):
    return str(random.randint(int(min), int(max)))


# ------------JOIN AND lEAVE MESSAGES-------------


@bot.command()
async def onjoin(ctx, message):
    config["servers"][str(ctx.guild.id)]["joinMessageChannel"] = str(ctx.channel.id)
    config["servers"][str(ctx.guild.id)]["joinMessage"] = message
    writeConfig()
    await ctx.channel.send("Now notification about new members will be shown in this channel")


@bot.event
async def on_member_join(Member):
    channel = bot.get_channel(int(config["servers"][str(Member.guild.id)]["joinMessageChannel"]))
    await channel.send(config["servers"][str(Member.guild.id)]["joinMessage"].format(Member.mention))


@bot.command()
async def onleave(ctx, message):
    config["servers"][str(ctx.guild.id)]["leaveMessageChannel"] = str(ctx.channel.id)
    config["servers"][str(ctx.guild.id)]["leaveMessage"] = message
    writeConfig()
    await ctx.channel.send("Now notification about left members will be shown in this channel")


@bot.event
async def on_member_remove(Member):
    channel = bot.get_channel(int(config["servers"][str(Member.guild.id)]["leaveMessageChannel"]))
    await channel.send(config["servers"][str(Member.guild.id)]["leaveMessage"].format(str(Member.name)+"#"+str(Member.discriminator)))


async def load_extensions():
    # for filename in os.listdir("./"):
    #     if filename.endswith(".py") and filename == "gifs.py":
    #         await bot.load_extension(f"{filename[:-3]}")
    await bot.load_extension("gifs")
    # await bot.load_extension(f"youtube")


async def main():
    await load_extensions()
    await bot.start(config["token"])


if __name__ == "__main__":
    asyncio.run(main())
