import discord
from discord.ext import commands
from random import randint
import json
import requests
from keep_alive import keep_alive
import os

TOKEN = os.environ.get("TOKEN")
bot = commands.Bot(command_prefix = ".")


@bot.event
async def on_ready():
    activity = discord.Game(type=discord.ActivityType.watching, name="twitch.tv/es6x3 - топ киса")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print("Bot is ready!")


@bot.command(pass_context=True)
async def prefix(ctx):
    await ctx.reply(midGame())


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

keep_alive()
bot.run(TOKEN)
