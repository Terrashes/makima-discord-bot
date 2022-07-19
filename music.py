import discord
from discord.ext import commands
import youtube_dl
from main import bot
import pafy

async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

async def search_song(self, amount, song, get_url=False):
    info = await bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
    if len(info["entries"]) == 0: return None

    return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

async def play_song(self, ctx, song):
    url = pafy.new(song).getbestaudio().url
    ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
    ctx.voice_client.source.volume = 1

@commands.command()
async def play(ctx, *, song=None):
    if ctx.author.voice is None:
        return await ctx.send("You are not connected to a voice channel, please connect to the channel you want the bot to join.")

    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

    await ctx.author.voice.channel.connect()
    if song is None:
        return await ctx.send("You must include a song to play.")

    if ctx.voice_client is None:
        return await ctx.send("I must be in a voice channel to play a song.")

    # handle song where song isn't url
    if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
        await ctx.send("Searching for song, this may take a few seconds.")
        result = await bot.search_song(1, song, get_url=True)

        if result is None:
            return await ctx.send("Sorry, I could not find the given song, try using my search command.")

        song = result[0]

    if ctx.voice_client.source is not None:
        queue_len = len(bot.song_queue[ctx.guild.id])

        if queue_len < 10:
            bot.song_queue[ctx.guild.id].append(song)
            return await ctx.send(f"I am currently playing a song, this song has been added to the queue at position: {queue_len+1}.")

        else:
            return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")
    url = pafy.new(song).getbestaudio().url
    ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: bot.bot.loop.create_task(check_queue(ctx)))
    ctx.voice_client.source.volume = 0.5
    await ctx.send(f"Now playing: {song}")

@commands.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        return await ctx.voice_client.disconnect()
    await ctx.send("I am not connected to a voice channel.")

def setup(bot):
    commands = [play, leave]
    for i in range(0, len(commands)):
        bot.add_command(commands[i])