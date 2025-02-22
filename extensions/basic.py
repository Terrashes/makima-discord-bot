from datetime import datetime, timezone
from random import choice, randint, choices
from typing import Any, Optional

import discord
import requests
from discord.ext import commands

from main import bot, config, config_write, get_prefix, startupDate


def beautifyDateDelta(date) -> list[Any]:
    timeDelta = datetime.now(timezone.utc) - date
    timeDeltaDays = timeDelta.days
    timeDeltaSecs = int((timeDelta.total_seconds() - timeDelta.days * 86400) // 1)
    timeParams = [
        timeDeltaDays // 365,
        timeDeltaDays % 365 // 30,
        timeDeltaDays % 365 % 30,
        timeDeltaSecs // 3600,
        timeDeltaSecs % 3600 // 60,
        timeDeltaSecs % 3600 % 60,
    ]
    return timeParams


@commands.group(invoke_without_command=True)
async def help(ctx) -> None:
    prefix = get_prefix(bot, ctx)[0]
    embed = discord.Embed(title="Commands Dashboard", color=0xFF6961)
    embed.add_field(
        name="`prefix` to change server prefix.",
        value=(f"Current server prefix is `{prefix}`."),
        inline=False,
    )
    embed.add_field(
        name="`status` to check bot's statistics.",
        value=("This command doesn't have any arguments."),
        inline=False,
    )
    embed.add_field(
        name="`onjoin` and `onleave` to add messages for users who just joined and left server.",
        value=('Sample: `onjoin "Welcome, {}!"` ({} - for mention user)'),
        inline=False,
    )
    embed.add_field(
        name="`purge` to delete latest messages in chat.",
        value=(
            "Sample: `purge 10` (Deletes latest 10 messages in chat.)\n Aliases: `p`, `cls`, `clear`, `del`, `delete`"
        ),
        inline=False,
    )
    embed.add_field(
        name="`avatar` to view user's avatar.",
        value=(
            "Sample: `avatar @user` (Shows author's avatar if no user has been mentioned.)"
        ),
        inline=False,
    )
    embed.add_field(
        name="`info` to view user's profile information.",
        value=(
            "Sample: `info @user` (Shows author's info if no user has been mentioned.)"
        ),
        inline=False,
    )
    embed.add_field(
        name="`roll` to roll a random number.",
        value=("Sample: `roll 1 1000` (By default it's rolling in 1-100 interval.)"),
        inline=False,
    )
    embed.add_field(
        name="`flip` to flip a coin.",
        value=(
            "Sample: `flip head` (Guess side of the coin using `head/tail` after command)"
        ),
        inline=False,
    )
    embed.add_field(
        name="`play` to play youtube audio and `leave` to leave voice channel.",
        value=("Sample: `play https://youtu.be/iWpCdUQLWwU`"),
        inline=False,
    )
    embed.add_field(
        name="`try` to randomly try any action.",
        value=("Sample: `try do something`"),
        inline=False,
    )
    # embed.add_field(
    #     name="`nhentai` to find hentai manga's info by ID.",
    #     value=("Sample: `nhentai 177013`"),
    #     inline=False)
    embed.add_field(
        name="New gif actions commands",
        value=(
            "`fuck`, `kiss`, `pat`, `kick`, `shy`, `slap`, `spank`, `deadinside`, `suck`"
        ),
        inline=False,
    )
    await ctx.send(embed=embed)


@commands.command(aliases=["p", "cls", "clear", "del", "delete"])
@commands.has_permissions(administrator=True)
async def purge(ctx, amount=None) -> None:
    if amount is None:
        await ctx.send("Please type amount of messages to delete.")
    else:
        await ctx.send(f"Deleting {amount} messages.")
        await ctx.message.channel.purge(limit=int(amount) + 2)


@commands.command()
async def status(ctx) -> None:
    botOnlineDuration: list[int] = beautifyDateDelta(startupDate)
    serverCount: int = len(config["servers"])
    embed = discord.Embed(
        color=0xFF6961,
        title="Bot's uptime",
        description=f"Uptime: {botOnlineDuration[2]} days, {botOnlineDuration[3]} hours, {botOnlineDuration[4]} min, {botOnlineDuration[5]} sec",
    )
    embed.add_field(
        name="Last started",
        value=(startupDate.strftime("`%H:%M:%S` `%d.%m.%Y`")),
        inline=False,
    )
    embed.add_field(
        name="Servers", value=(f"Working on `{serverCount}` servers"), inline=False
    )
    embed.add_field(
        name="Latency",
        value=(f"Current latency is `{bot.latency*1000//1}` ms"),
        inline=False,
    )
    await ctx.send(embed=embed)


@commands.command()
@commands.has_permissions(administrator=True)
async def prefix(ctx, new_prefix="") -> None:
    current_prefix = config["servers"][str(ctx.guild.id)]["prefix"]
    if new_prefix == current_prefix:
        await ctx.send(
            f"Current prefix is `{current_prefix}`. Server prefix didn't change because you specified the same prefix as current."
        )
    elif new_prefix is None:
        await ctx.send(f"Current prefix is `{current_prefix}`.")
    else:
        config["servers"][str(ctx.guild.id)]["prefix"] = new_prefix
        config_write()
        await ctx.send(
            f'Server prefix changed. Current prefix is `{config["servers"][str(ctx.guild.id)]["prefix"]}`.'
        )


# ------------ROLL GAMES, ETC-------------
@commands.hybrid_command(
    name="roll", with_app_command=True, description="Roll a number"
)
async def roll(ctx, min=1, max=100) -> None:
    await ctx.reply(randint(min, max))


@commands.hybrid_command(name="flip", with_app_command=True, description="Flip a coin")
async def flip(ctx, *, flip_guess: Optional[str] = None) -> None:
    flip_result: str = choice(["HEADS", "TAILS"])
    message: str = f"Got **{flip_result}**"
    if flip_guess:
        message += (
            lambda g, r: (
                " - you guessed right"
                if g.lower() == r
                else " - you didn't guess right" if g in ["heads", "tails"] else ""
            )
        )(flip_guess, flip_result)
    await ctx.reply(message)


@commands.hybrid_command(
    name="avatar", with_app_command=True, description="Get user's avatar image"
)
async def avatar(ctx, person: Optional[discord.Member] = None) -> None:
    if not person:
        person = ctx.author
    target_avatar = person.avatar
    embed = discord.Embed(color=0xFF6961)
    embed.add_field(
        name=person,
        value="Click [Here](%s) to download picture." % target_avatar,
        inline=False,
    )
    embed.set_image(url=target_avatar)
    await ctx.send(embed=embed)


@commands.command()
async def info(ctx, person=None) -> None:
    if not person:
        person = ctx.author
    rlist = []
    for role in person.roles:
        if role.name != "@everyone":
            rlist.append(role.mention)
    b = ", ".join(rlist)
    accCreate = person.created_at.strftime("`%H:%M:%S` `%d.%m.%Y`")
    accJoin = person.joined_at.strftime("`%H:%M:%S` `%d.%m.%Y`")
    accCreateDelta = beautifyDateDelta(person.created_at)
    accJoinDelta = beautifyDateDelta(person.joined_at)
    embed = discord.Embed(title=person, color=0xFF6961)
    embed.set_thumbnail(url=person.avatar)
    embed.add_field(
        name="Account created:",
        value="{} ({} years, {} months, {} days ago)".format(
            accCreate, accCreateDelta[0], accCreateDelta[1], accCreateDelta[2]
        ),
        inline=False,
    )
    embed.add_field(
        name="Joined server:",
        value="{} ({} years, {} months, {} days ago)".format(
            accJoin, accJoinDelta[0], accJoinDelta[1], accJoinDelta[2]
        ),
        inline=False,
    )
    embed.add_field(name="User ID:", value=f" {person.id}", inline=True)
    embed.add_field(name=f"Roles ({len(rlist)}) :", value="".join([b]), inline=False)
    embed.add_field(name="Top Role:", value=person.top_role.mention, inline=False)
    await ctx.send(embed=embed)


@commands.hybrid_command(
    name="checkip", with_app_command=True, description="Get info about IP/domain"
)
async def checkip(ctx, ip: str) -> None:
    if not ip:
        await ctx.send("Specify ip or domain for lookup")
    API_Token = config["ipapi_token"]
    response = requests.get(
        f"http://api.ipapi.com/{ip}?access_key={API_Token}&output=json", timeout=30
    ).json()
    embed = discord.Embed(title=f"Info about {ip}", color=0xFF6961)
    embed.add_field(name="Region:", value=response["region_name"], inline=False)
    embed.add_field(name="City", value=response["city"], inline=False)
    embed.add_field(name="Latitude:", value=response["latitude"], inline=False)
    embed.add_field(name="Longitude:", value=response["longitude"], inline=False)
    await ctx.send(embed=embed)


# ------------JOIN AND lEAVE MESSAGES-------------


@commands.command()
async def onjoin(ctx, message: str) -> None:
    config["servers"][str(ctx.guild.id)]["joinMessageChannel"] = str(ctx.channel.id)
    config["servers"][str(ctx.guild.id)]["joinMessage"] = message
    config_write()
    await ctx.send("Now notification about new members will be shown in this channel")


# @commands.event
# async def on_member_join(Member):
#     channel = bot.get_channel(int(config["servers"][str(Member.guild.id)]["joinMessageChannel"]))
#     await channel.send(config["servers"][str(Member.guild.id)]["joinMessage"].format(Member.mention))


@commands.command()
async def onleave(ctx, message: str) -> None:
    config["servers"][str(ctx.guild.id)]["leaveMessageChannel"] = str(ctx.channel.id)
    config["servers"][str(ctx.guild.id)]["leaveMessage"] = message
    config_write()
    await ctx.send("Now notification about left members will be shown in this channel")


# @commands.event
# async def on_member_remove(Member: discord.Member):
#     channel = bot.get_channel(int(config["servers"][str(Member.guild.id)]["leaveMessageChannel"]))
#     await channel.send(config["servers"][str(Member.guild.id)]["leaveMessage"].format(str(Member.name)+"#"+str(Member.discriminator)))


@commands.hybrid_command(
    name="try", with_app_command=True, description="Try some action"
)
async def try_command(ctx, *, action: Optional[str] = None) -> None:
    """
    Simulates an actor trying an action, randomly deciding success or failure.

    :param ctx: The context of the command.
    :param action: The action being attempted.
    """
    if not action:
        await ctx.send("Please specify action to try.")
    result = choice(["успешно", "безуспешно"])
    result_modifier = choices(
        [""] * 10
        + [
            ", но помер",
            ", но обосрался",
            ", закрутив себе яйцо",
        ],  # 10 empty + 3 rare outcomes
        weights=[1] * 10 + [0.1] * 3,  # Probability weights
    )[0]
    message = f"{ctx.author.mention} `{result}` {action}{result_modifier}"
    await ctx.send(message)


async def setup(bot) -> None:
    commands_to_add = [
        help,
        purge,
        status,
        prefix,
        roll,
        flip,
        avatar,
        info,
        checkip,
        onjoin,
        onleave,
        try_command,
    ]
    for command in commands_to_add:
        bot.add_command(command)
