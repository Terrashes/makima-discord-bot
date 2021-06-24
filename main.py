import discord
from discord.ext import commands
from random import randint
import json
import requests
import os

# -----------ONLY FOR TESTING----------

# from settings import tokenKey
# TOKEN = tokenKey

# -------------------------------------

# --------UNCOMMENT FOR DEPLOY---------

from keep_alive import keep_alive
TOKEN = os.environ.get("TOKEN")
keep_alive()

# -------------------------------------

serverPrefix = "."
bot = commands.Bot(command_prefix = serverPrefix, help_command=None)


@bot.event
async def on_ready():
    activity = discord.Game(name="twitch.tv/es6x3 - топ киса")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Bot has just started.")

@bot.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title = "Commands Dashboard")
    em.add_field(name="Use **`prefix`** to change server prefix.(doesn't work yet)",
                 value=('Current server prefix is "' + serverPrefix+'"'), inline=False)
    em.add_field(name='Use **`avatar`** to view users avatar.',
                 value=("Sample: `avatar @user` (if u don't mention any user it shows your avatar.)"), inline=False)
    em.add_field(name='Use **`mid`** to decide who is going to mid.',
                 value=("This command doesn't have any arguments."), inline=False)
    em.add_field(name='Use **`roll`** to roll a random number.',
                 value=("Sample: `roll 1 1000` (By default it's rolling in 1-100 interval.)"), inline=False)
    em.add_field(name='Use **`meme`** to get a random meme.',
                 value=("Boring, not funny memes, shitty API"), inline=False)
    em.add_field(name='Use **`flip`**- to flip a coin.',
                 value=("Sample: `flip head` (U can guess side of the coin using `head/tail` after command)"), inline=False)
    await ctx.send(embed = em)

# @bot.command(pass_context=True)
# async def prefix(ctx):
#     await ctx.reply()

@bot.command(pass_context=True)
async def avatar(ctx, targetPerson: discord.User=""):
    if (targetPerson == ""):
        targetPerson = ctx.author
        targetAvatar = ctx.author.avatar_url
    else:
        targetAvatar = targetPerson.avatar_url
    embed = discord.Embed()
    embed.add_field(name = targetPerson, value="Click [Here](%s) to download picture." % targetAvatar, inline=False)
    embed.set_image(url=targetAvatar)
    await ctx.channel.send(embed=embed)


@bot.command(pass_context=True)
async def sosi(ctx):
    await ctx.reply("Сам соси черт бля")


@bot.command(pass_context=True)
async def roll(ctx, minRoll=0, maxRoll=100):
    await ctx.reply(rollGame(minRoll, maxRoll))


@bot.command(pass_context=True)
async def mid(ctx):
    await ctx.reply(midGame())


@bot.command(pass_context=True)
async def flip(ctx, arg=""):
    await ctx.reply(flipGame(arg))

@bot.command()
async def meme(ctx):
    response = requests.get('https://some-random-api.ml/meme')
    json_data = json.loads(response.text)
    embed = discord.Embed(color = 0xffc7ff)
    embed.set_image(url = json_data['image'])
    await ctx.send(embed = embed)

@bot.command()
async def waifu(ctx):
    response = requests.get('https://some-random-api.ml/meme')
    json_data = json.loads(response.text)
    embed = discord.Embed(color = 0xffc7ff)
    embed.set_image(url = json_data['image'])
    await ctx.send(embed = embed)

# def changePrefix(min, max):
#     return randint(min, max)

def flipGame(resultFlip):
    resultFlipTrue = getRandom(1, 2)
    if resultFlip == 'head':
        if int(resultFlipTrue) == 1:
            return "Выпал орел - ты угадал"
        else:
            return "Выпала решка - ты не угадал"
    elif resultFlip == 'tail':
        if int(resultFlipTrue) == 2:
            return "Выпала решка - ты угадал"
        else:
            return "Выпал орел - ты не угадал"
    else:
        if int(resultFlipTrue) == 2:
            return "Выпала решка"
        else:
            return "Выпал орел"

def getRandom(min, max):
    return str(randint(int(min), int(max)))


def rollGame(minRoll, maxRoll):
    return getRandom(minRoll, maxRoll)


def midGame():
    userRoll = getRandom(1, 100)
    botRoll = getRandom(1, 100)
    if int(userRoll) > int(botRoll):
        return "Ты зароллил: " + userRoll + "\n" + "Я зароллил: " + botRoll + "\n" + userRoll + " > " + botRoll + "\n" + "Найс рандом чел"
    elif int(userRoll) < int(botRoll):
        return "Ты зароллил: " + userRoll + "\n" + "Я зароллил: " + botRoll + "\n" + userRoll + " < " + botRoll + "\n" + "Ez mid, ez life"
    else:
        return "Ты зароллил: " + userRoll + "\n" + "Я зароллил: " + botRoll + "\n" + "Ебаать, ты хоть знаешь какой шанс такое рольнуть? Реролл"

bot.run(TOKEN)
