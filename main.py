import discord
from discord.ext import commands
from random import randint
from datetime import *
import json
import requests
import os
from discord.ext.commands import Bot


# -----------ONLY FOR TESTING----------

# from settings import tokenKey
# TOKEN = tokenKey

# -------------------------------------


# --------UNCOMMENT FOR DEPLOY---------

from keep_alive import keep_alive
TOKEN = os.environ.get("TOKEN")
keep_alive()

# -------------------------------------


def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


startupDate = datetime.now()
bot = Bot(command_prefix = get_prefix, help_command=None)


@bot.event
async def on_ready():
    activity = discord.Game(name="?help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("[{}] Makima is online now!".format(startupDate.isoformat(sep='T')))


@bot.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = "?"
    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)

# ------------SERVICE COMMANDS-------------

@bot.group(invoke_without_command=True)
async def help(ctx):
    prefix = get_prefix(bot, ctx)
    embed = discord.Embed(title = "Commands Dashboard")
    embed.add_field(name="Use `prefix` to change server prefix.",
                    value=('Current server prefix is `"' + str(prefix) +'"`'), inline=False)
    embed.add_field(name="Use `uptime` to check bot's statistics.",
                    value=("This command doesn't have any arguments."), inline=False)
    embed.add_field(name="Use `purge` to delete latest messages in chat.",
                    value=("Sample: `purge 10` (Deletes latest 10 messages in current chat.)"), inline=False)
    embed.add_field(name="Use `avatar` to view user's avatar.",
                    value=("Sample: `avatar @user` (if u don't mention any user it shows your avatar.)"), inline=False)
    embed.add_field(name="Use `mid` to decide who's going to mid.",
                    value=("This command doesn't have any arguments."), inline=False)
    embed.add_field(name='Use `roll` to roll a random number.',
                    value=("Sample: `roll 1 1000` (By default it's rolling in 1-100 interval.)"), inline=False)
    embed.add_field(name='Use `meme` to get a random meme.',
                    value=("Boring, not funny memes, shitty API"), inline=False)
    embed.add_field(name='Use `flip`- to flip a coin.',
                    value=("Sample: `flip head` (U can guess side of the coin using `head/tail` after command)"), inline=False)
    await ctx.send(embed = embed)


@bot.command(pass_context=True)
@commands.has_permissions(administrator = True)
async def purge(ctx, amount):
    messages = []
    await ctx.channel.send("Deleting " + amount + " messages.")
    async for message in ctx.message.channel.history(limit=int(amount) + 2):
        messages.append(message)
    await ctx.message.channel.delete_messages(messages)


@bot.command(pass_context=True)
async def uptime(ctx):
    startupDelta = (datetime.now() - startupDate)
    startupDelta_s = startupDelta.total_seconds()
    startupDelta_days = startupDelta.days
    startupDelta_days = divmod(startupDelta_s, 86400)
    startupDelta_hour = divmod(startupDelta_days[1], 3600)
    startupDelta_min = divmod(startupDelta_hour[1], 60)
    startupDelta_sec = divmod(startupDelta_min[1], 1)
    embed = discord.Embed(title="Bot's uptime", description="Uptime: {} days, {} hours, {} min, {} sec".format(int(startupDelta_days[0]), int(startupDelta_hour[0]), int(startupDelta_min[0]), int(startupDelta_sec[0])))
    embed.add_field(
        name="Last started",
        value = (startupDate), inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator = True)
async def prefix(ctx, prefixValue):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    if prefixes[str(ctx.guild.id)] != prefixValue:
        prefixes[str(ctx.guild.id)] = prefixValue
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f)
        await ctx.channel.send("Server prefix changed. Current prefix is " + '`"' + prefixValue + '"`' + " .")
    else:
        await ctx.channel.send("Server prefix didn't change because you specified the same prefix as current. Current prefix is " + '`"' + prefixes[str(ctx.guild.id)] + '"`' + " .")


# ------------ROLL GAMES, ETC-------------


@bot.command(pass_context=True)
async def roll(ctx, minRoll=0, maxRoll=100):
    await ctx.reply(getRandom(minRoll, maxRoll))


@bot.command(pass_context=True)
async def mid(ctx):
    userRoll = getRandom(1, 100)
    botRoll = getRandom(1, 100)
    if int(userRoll) > int(botRoll):
        midResult = "Ты зароллил: " + userRoll + "\n" + "Я зароллил: " + botRoll + "\n" + userRoll + " > " + botRoll + "\n" + "Найс рандом чел"
    elif int(userRoll) < int(botRoll):
        midResult = "Ты зароллил: " + userRoll + "\n" + "Я зароллил: " + botRoll + "\n" + userRoll + " < " + botRoll + "\n" + "Ez mid, ez life"
    else:
        midResult = "Ты зароллил: " + userRoll + "\n" + "Я зароллил: " + botRoll + "\n" + "Ебаать, ты хоть знаешь какой шанс такое рольнуть? Реролл"
    await ctx.reply(midResult)


@bot.command(pass_context=True)
async def flip(ctx, resultFlip=""):
    resultFlipTrue = getRandom(1, 2)
    if resultFlip == 'head':
        if int(resultFlipTrue) == 1:
            resultFlipFinal = "Выпал орел - ты угадал"
        else:
            resultFlipFinal = "Выпала решка - ты не угадал"
    elif resultFlip == 'tail':
        if int(resultFlipTrue) == 2:
            resultFlipFinal = "Выпала решка - ты угадал"
        else:
            resultFlipFinal = "Выпал орел - ты не угадал"
    else:
        if int(resultFlipTrue) == 2:
            resultFlipFinal = "Выпала решка"
        else:
            resultFlipFinal = "Выпал орел"
    await ctx.reply(resultFlipFinal)


@bot.command()
async def meme(ctx):
    response = requests.get('https://some-random-api.ml/meme')
    json_data = json.loads(response.text)
    embed = discord.Embed(color=0xffc7ff)
    embed.set_image(url=json_data['image'])
    await ctx.send(embed=embed)


def getRandom(min, max):
    return str(randint(int(min), int(max)))


bot.run(TOKEN)