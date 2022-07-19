from msilib.schema import Component
from bs4 import BeautifulSoup
from discord_components import DiscordComponents, Button, ButtonStyle
import requests
import discord
from discord.ext import commands
from main import bot


cookies = {
    'cf_clearance': 'eINMW9hcX962t6WxjcoewVn64QLiRye76G.T_wzLSkY-1656492615-0-150',
    'csrftoken': 'M0bNXNa38HXDoLtf6w3tVr9AoN2jsHZx6jHU7uGPO8urM2BPUcfNApqczNG7CE55',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    # Requests sorts cookies= alphabetically
    # 'Cookie': 'cf_clearance=eINMW9hcX962t6WxjcoewVn64QLiRye76G.T_wzLSkY-1656492615-0-150; csrftoken=M0bNXNa38HXDoLtf6w3tVr9AoN2jsHZx6jHU7uGPO8urM2BPUcfNApqczNG7CE55',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
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
async def nhentai(ctx, id):
    URL = 'https://nhentai.net/g/' + id
    response = requests.get(URL, cookies=cookies, headers=headers)
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


def setup(bot):
    commands = [nhentai]
    for i in range(0, len(commands)):
        bot.add_command(commands[i])