from msilib.schema import Component
from bs4 import BeautifulSoup
from discord_components import DiscordComponents, Button, ButtonStyle
import requests
import discord
from discord.ext import commands
from main import bot


cookies = {
    "cf_clearance": "hy7szdLIpMHpUzzXUHI31CusN.S0ltuvL4DStjffII8-1658665867-0-150",
    "csrftoken": "M0bNXNa38HXDoLtf6w3tVr9AoN2jsHZx6jHU7uGPO8urM2BPUcfNApqczNG7CE55"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
}


def get_info(response):
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find(class_="pretty").contents[0]
    cover = soup.find('img', class_='lazyload')['data-src']
    tags = soup.find_all(class_="tag")
    tagsArray = []
    strTags = ""
    for i in range(0, len(tags)):
        stringtag = str(tags[i])
        if stringtag.find('href="/tag/') != -1:
            tagsArray.append(next(tags[i].children).contents[0])
    for i in range(0,len(tagsArray)):
        strTags += "`{}` ".format(tagsArray[i])
    return title, cover, strTags


@commands.command()
async def nhentai(ctx, id = 'random'):
    if id != 'random':
        id == 'g/' + id
    URL = 'https://nhentai.net/' + id
    response = requests.get(URL, cookies=cookies, headers=headers)
    print(URL, response)
    if response.status_code == 200:
        info = get_info(response)
        embed = discord.Embed(color=0xff6961)
        embed.add_field(name = info[0], value = info[2], inline=False)
        page = embed.set_image(url=info[1])
        message = await ctx.channel.send(embed=embed,
            components = [
            Button(style=ButtonStyle.grey, label="Previous", emoji="⏮️"),
            Button(style=ButtonStyle.grey, label="Next", emoji="⏭️")
            ]   
        )
        buttonPress = await bot.wait_for("button_click")
        if buttonPress.channel == ctx.channel:
            if buttonPress.component.label == "Previous":
                page = embed.set_image(url="https://i.imgur.com/yrwAhWo.jpeg")
                await message.edit(embed=embed)
            if buttonPress.component.label == "Next":
                page = embed.set_image(url="=info[1]")
                await message.edit(embed=embed)
    else:
        await ctx.channel.send("ID wasn't found. (Error {}.)".format(response.status_code))


async def setup(bot):
    commands = [nhentai]
    for command in commands:
        bot.add_command(command)