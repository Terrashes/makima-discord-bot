from typing import Any
import asyncio
import json
import discord
import requests
from discord.ext import commands

class TwitchCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.load_config()
        self.notification_task = None
        self.twitch_access_token = self.get_twitch_access_token()

    @staticmethod
    def load_config():
        """Load the configuration."""
        with open("config.json", "r") as file:
            return json.load(file)

    def save_config(self):
        """Save the configuration."""
        with open("config.json", "w") as file:
            json.dump(self.config, file, indent=4)

    def get_twitch_access_token(self):
        """Authenticate with Twitch and retrieve the access token."""
        auth_url = "https://id.twitch.tv/oauth2/token"
        auth_params = {
            "client_id": self.config["twitch_client_id"],
            "client_secret": self.config["twitch_secret"],
            "grant_type": "client_credentials",
            "scope": "user:read:email",
        }
        response = requests.post(auth_url, params=auth_params).json()
        return response["access_token"]

    def is_stream_live(self, streamer_username):
        """Check if a Twitch stream is live."""
        try:
            headers = {
                "Client-ID": self.config["twitch_client_id"],
                "Authorization": f"Bearer {self.twitch_access_token}",
            }
            twitch_api_url = f"https://api.twitch.tv/helix/streams?user_login={streamer_username}"
            response = requests.get(twitch_api_url, headers=headers).json()
            status = bool(response.get("data", []))
            title = response["data"][0]["title"] if status else ""
            thumbnail = (
                response["data"][0]["thumbnail_url"].format(width=640, height=360)
                if status
                else ""
            )
            return status, title, thumbnail
        except Exception as e:
            print(f"Error checking Twitch status: {e}")
            return False, "", ""

    async def send_notification(self, streamer_username):
        """Send notifications about a streamer's status."""
        try:
            streamer_info = self.config["twitch"].get(streamer_username, {})
            current_status = streamer_info.get("status", False)
            status, title, thumbnail = self.is_stream_live(streamer_username)

            if status != current_status:
                for channel_id, messages in streamer_info.get("channels", {}).items():
                    channel = self.bot.get_channel(int(channel_id))
                    if channel:
                        if status:
                            embed = discord.Embed(
                                color=0x6441A4,
                                title=messages["messageLive"],
                                description="",
                            )
                            embed.add_field(
                                name=title,
                                value=f"https://www.twitch.tv/{streamer_username}",
                                inline=False,
                            )
                            embed.set_image(url=thumbnail)
                            await channel.send(embed=embed)
                        else:
                            await channel.send(messages["messageOff"])
                streamer_info["status"] = status
                self.save_config()
        except Exception as e:
            print(f"Error sending notification: {e}")

    async def send_notifications(self):
        """Periodic task to check Twitch streams and send notifications."""
        while not self.bot.is_closed():
            try:
                if self.config["twitch"]:
                    for streamer_username in self.config["twitch"]:
                        await self.send_notification(streamer_username)
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error in notification loop: {e}")
    
    @commands.hybrid_command(name="twadd", description="Add Twitch streamer for notifications")
    async def twadd(self, ctx, streamer_username: str = None):
        """Add a Twitch streamer for notifications."""
        if not streamer_username:
            await ctx.send("Please specify the streamer's username.")
            return

        message_live = f"Hey everyone! {streamer_username} is now live!"
        message_off = f"{streamer_username} is offline now."

        await ctx.send("Please enter a message for when the streamer goes live:")
        try:
            message = await self.bot.wait_for(
                "message",
                timeout=60,
                check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel,
            )
            message_live = message.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Using the default live message.")

        await ctx.send("Please enter a message for when the streamer goes offline:")
        try:
            message = await self.bot.wait_for(
                "message",
                timeout=60,
                check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel,
            )
            message_off = message.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Using the default offline message.")

        twitch_config = self.config["twitch"].setdefault(streamer_username, {"status": False, "channels": {}})
        twitch_config["channels"][str(ctx.channel.id)] = {"messageLive": message_live, "messageOff": message_off}
        self.save_config()
        await ctx.send(f"Streamer `{streamer_username}` has been added to notifications.")

    @commands.hybrid_command(name="twdel", description="Remove Twitch streamer notifications")
    async def twdel(self, ctx, streamer_username: str = None):
        """Remove a Twitch streamer from notifications."""
        if not streamer_username:
            await ctx.send("Please specify the streamer's username.")
            return

        try:
            del self.config["twitch"][streamer_username]["channels"][str(ctx.channel.id)]
            if not self.config["twitch"][streamer_username]["channels"]:
                del self.config["twitch"][streamer_username]
            self.save_config()
            await ctx.send(f"Streamer `{streamer_username}` has been removed from notifications.")
        except KeyError:
            await ctx.send(f"Streamer `{streamer_username}` is not tracked in this channel.")

    @commands.hybrid_command(name="twlist", description="List Twitch streamers tracked in this channel")
    async def twlist(self, ctx):
        """List Twitch streamers being tracked in the current channel."""
        message = "**Tracked Streamers:**"
        for streamer_username, streamer_info in self.config["twitch"].items():
            if str(ctx.channel.id) in streamer_info["channels"]:
                status = ":green_circle: Live" if streamer_info["status"] else ":red_circle: Offline"
                message += f"\n{streamer_username} {status}"
        if message == "**Tracked Streamers:**":
            await ctx.send("No streamers are being tracked in this channel.")
        else:
            await ctx.send(message)

    @commands.Cog.listener()
    async def on_ready(self):
        """Start the notification task when the bot is ready."""
        if not self.notification_task:
            self.notification_task = asyncio.create_task(self.send_notifications())

async def setup(bot: commands.Bot):
    """Add the TwitchCog to the bot."""
    await bot.add_cog(TwitchCog(bot))
