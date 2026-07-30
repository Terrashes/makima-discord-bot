from __future__ import annotations

import asyncio
import logging
import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands


LOGGER = logging.getLogger(__name__)

COOKIE_FILE = Path("yt_cookies.txt")
MAX_QUEUE_DISPLAY = 10
YOUTUBE_URL_RE = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/",
    re.IGNORECASE,
)
HTTP_URL_RE = re.compile(r"^https?://", re.IGNORECASE)

FFMPEG_OPTIONS: dict[str, str] = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}
YDL_OPTIONS: dict[str, Any] = {
    "format": "bestaudio[acodec=opus]/bestaudio[ext=m4a]/bestaudio/best[acodec!=none]/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "source_address": "0.0.0.0",
}
YDL_FALLBACK_FORMAT = "best[acodec!=none]/best"


class MusicError(Exception):
    """Raised for user-facing music command failures."""


@dataclass
class Track:
    title: str
    stream_url: str
    webpage_url: str
    duration: int | None
    requested_by: str


@dataclass
class GuildMusicState:
    queue: deque[Track] = field(default_factory=deque)
    current: Track | None = None
    text_channel: discord.abc.Messageable | None = None
    play_next_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    stopping: bool = False


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.states: dict[int, GuildMusicState] = {}

    def _state_for(self, guild_id: int) -> GuildMusicState:
        state = self.states.get(guild_id)
        if state is None:
            state = GuildMusicState()
            self.states[guild_id] = state
        return state

    @staticmethod
    def _normalise_query(query: str) -> str:
        query = query.strip()
        if YOUTUBE_URL_RE.match(query) and not HTTP_URL_RE.match(query):
            return f"https://{query}"
        if HTTP_URL_RE.match(query):
            return query
        return f"ytsearch1:{query}"

    @staticmethod
    def _format_duration(seconds: int | None) -> str:
        if not seconds:
            return "live"

        minutes, secs = divmod(seconds, 60)
        hours, mins = divmod(minutes, 60)
        if hours:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"

    @staticmethod
    def _shorten(value: str, limit: int = 80) -> str:
        if len(value) <= limit:
            return value
        return f"{value[: limit - 3]}..."

    @staticmethod
    def _is_voice_active(voice_client: discord.VoiceClient) -> bool:
        return voice_client.is_playing() or voice_client.is_paused()

    def _get_voice_client(self, guild_id: int) -> discord.VoiceClient | None:
        guild = self.bot.get_guild(guild_id)
        if guild is None or not isinstance(guild.voice_client, discord.VoiceClient):
            return None
        return guild.voice_client

    def _extract_info(self, query: str) -> dict[str, Any]:
        options = YDL_OPTIONS.copy()
        if COOKIE_FILE.exists():
            options["cookiefile"] = str(COOKIE_FILE)

        normalised_query = self._normalise_query(query)
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(normalised_query, download=False)
        except yt_dlp.DownloadError as exc:
            if "Requested format is not available" not in str(exc):
                raise

            fallback_options = options.copy()
            fallback_options["format"] = YDL_FALLBACK_FORMAT
            with yt_dlp.YoutubeDL(fallback_options) as ydl:
                info = ydl.extract_info(normalised_query, download=False)

        if not isinstance(info, dict):
            raise MusicError("Could not read the YouTube response.")

        entries = info.get("entries")
        if entries is not None:
            info = next((entry for entry in entries if entry), None)
            if info is None:
                raise MusicError("No videos were found.")

        if not info.get("url"):
            raise MusicError("Could not get an audio stream for that video.")

        return info

    async def _extract_track(self, query: str, requester: discord.abc.User) -> Track:
        loop = asyncio.get_running_loop()

        try:
            info = await loop.run_in_executor(None, self._extract_info, query)
        except yt_dlp.DownloadError as exc:
            raise MusicError("I couldn't load that YouTube video.") from exc

        duration = info.get("duration")
        if duration is not None:
            duration = int(duration)

        return Track(
            title=str(info.get("title") or "Untitled"),
            stream_url=str(info["url"]),
            webpage_url=str(info.get("webpage_url") or info.get("original_url") or query),
            duration=duration,
            requested_by=getattr(requester, "display_name", str(requester)),
        )

    async def _ensure_voice_client(
        self, ctx: commands.Context[Any]
    ) -> discord.VoiceClient | None:
        if ctx.guild is None:
            await ctx.send("This command can be used only in a server.")
            return None

        voice_state = getattr(ctx.author, "voice", None)
        voice_channel = voice_state.channel if voice_state else None
        if voice_channel is None:
            await ctx.send("Join a voice channel first.")
            return None

        voice_client = ctx.guild.voice_client
        if voice_client is None:
            try:
                return await voice_channel.connect()
            except (asyncio.TimeoutError, discord.ClientException):
                LOGGER.exception("Could not connect to voice channel")
                await ctx.send("I couldn't connect to your voice channel.")
                return None

        if not isinstance(voice_client, discord.VoiceClient):
            await ctx.send("I am already connected with an unsupported voice client.")
            return None

        if voice_client.channel != voice_channel:
            if self._is_voice_active(voice_client):
                await ctx.send(f"I'm already playing in {voice_client.channel.mention}.")
                return None
            await voice_client.move_to(voice_channel)

        return voice_client

    async def _send_to_state_channel(
        self, state: GuildMusicState, message: str
    ) -> None:
        if state.text_channel is None:
            return

        try:
            await state.text_channel.send(message)
        except discord.HTTPException:
            LOGGER.exception("Could not send music status message")

    def _after_callback(self, guild_id: int):
        def callback(error: Exception | None) -> None:
            future = asyncio.run_coroutine_threadsafe(
                self._handle_track_finished(guild_id, error), self.bot.loop
            )
            future.add_done_callback(self._log_callback_error)

        return callback

    @staticmethod
    def _log_callback_error(future: asyncio.Future[Any]) -> None:
        try:
            future.result()
        except Exception:
            LOGGER.exception("Music playback callback failed")

    async def _handle_track_finished(
        self, guild_id: int, error: Exception | None
    ) -> None:
        state = self.states.get(guild_id)
        if state is None:
            return

        if error is not None:
            LOGGER.error("Voice playback error in guild %s: %s", guild_id, error)
            await self._send_to_state_channel(state, f"Playback error: `{error}`")

        state.current = None
        if state.stopping:
            state.stopping = False
            return

        await self._play_next(guild_id)

    async def _play_next(self, guild_id: int) -> None:
        state = self._state_for(guild_id)
        while True:
            async with state.play_next_lock:
                voice_client = self._get_voice_client(guild_id)
                if voice_client is None or not voice_client.is_connected():
                    state.current = None
                    return

                if self._is_voice_active(voice_client) or state.current is not None:
                    return

                if not state.queue:
                    state.current = None
                    return

                track = state.queue.popleft()
                state.current = track

            try:
                source = await discord.FFmpegOpusAudio.from_probe(
                    track.stream_url, **FFMPEG_OPTIONS
                )
            except Exception:
                LOGGER.exception("Could not create FFmpeg source")
                if state.current is track:
                    state.current = None
                await self._send_to_state_channel(
                    state,
                    f"Couldn't start **{self._shorten(track.title)}**. Check FFmpeg and YouTube access.",
                )
                if self.states.get(guild_id) is not state:
                    return
                continue

            voice_client = self._get_voice_client(guild_id)
            if (
                voice_client is None
                or not voice_client.is_connected()
                or self.states.get(guild_id) is not state
                or state.current is not track
                or state.stopping
            ):
                source.cleanup()
                return

            try:
                voice_client.play(source, after=self._after_callback(guild_id))
            except Exception:
                LOGGER.exception("Could not start voice playback")
                source.cleanup()
                if state.current is track:
                    state.current = None
                await self._send_to_state_channel(
                    state,
                    f"Couldn't start **{self._shorten(track.title)}**. Check voice connection.",
                )
                if self.states.get(guild_id) is not state:
                    return
                continue

            await self._send_to_state_channel(
                state,
                f"Now playing: **{self._shorten(track.title)}** "
                f"({self._format_duration(track.duration)})",
            )
            return

    @staticmethod
    async def _defer_interaction(ctx: commands.Context[Any]) -> None:
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.interaction.response.defer()

    @commands.hybrid_command(
        name="play",
        with_app_command=True,
        description="Play YouTube audio in a voice channel",
    )
    @app_commands.describe(query="YouTube URL or search text")
    async def play(self, ctx: commands.Context[Any], *, query: str) -> None:
        await self._defer_interaction(ctx)
        voice_client = await self._ensure_voice_client(ctx)
        if voice_client is None or ctx.guild is None:
            return

        state = self._state_for(ctx.guild.id)
        state.text_channel = ctx.channel

        async with ctx.typing():
            try:
                track = await self._extract_track(query, ctx.author)
            except MusicError as exc:
                await ctx.send(str(exc))
                return

        state.queue.append(track)
        position = len(state.queue)

        if self._is_voice_active(voice_client) or state.current is not None:
            await ctx.send(
                f"Added to queue at position {position}: **{self._shorten(track.title)}**"
            )
            return

        await ctx.send(f"Added to queue: **{self._shorten(track.title)}**")
        await self._play_next(ctx.guild.id)

    @commands.hybrid_command(
        name="skip",
        with_app_command=True,
        description="Skip the current track",
    )
    async def skip(self, ctx: commands.Context[Any]) -> None:
        if ctx.guild is None:
            await ctx.send("This command can be used only in a server.")
            return

        voice_client = self._get_voice_client(ctx.guild.id)
        if voice_client is None or not self._is_voice_active(voice_client):
            await ctx.send("Nothing is playing.")
            return

        state = self._state_for(ctx.guild.id)
        state.text_channel = ctx.channel
        title = state.current.title if state.current else "current track"
        voice_client.stop()
        await ctx.send(f"Skipped **{self._shorten(title)}**.")

    @commands.hybrid_command(
        name="pause",
        with_app_command=True,
        description="Pause the current track",
    )
    async def pause(self, ctx: commands.Context[Any]) -> None:
        if ctx.guild is None:
            await ctx.send("This command can be used only in a server.")
            return

        voice_client = self._get_voice_client(ctx.guild.id)
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not connected to a voice channel.")
            return
        if voice_client.is_paused():
            await ctx.send("Playback is already paused.")
            return
        if not voice_client.is_playing():
            await ctx.send("Nothing is playing.")
            return

        voice_client.pause()
        await ctx.send("Paused.")

    @commands.hybrid_command(
        name="resume",
        with_app_command=True,
        description="Resume the paused track",
    )
    async def resume(self, ctx: commands.Context[Any]) -> None:
        if ctx.guild is None:
            await ctx.send("This command can be used only in a server.")
            return

        voice_client = self._get_voice_client(ctx.guild.id)
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not connected to a voice channel.")
            return
        if not voice_client.is_paused():
            await ctx.send("Playback is not paused.")
            return

        voice_client.resume()
        await ctx.send("Resumed.")

    @commands.hybrid_command(
        name="stop",
        with_app_command=True,
        description="Stop playback and clear the queue",
    )
    async def stop(self, ctx: commands.Context[Any]) -> None:
        if ctx.guild is None:
            await ctx.send("This command can be used only in a server.")
            return

        state = self._state_for(ctx.guild.id)
        voice_client = self._get_voice_client(ctx.guild.id)
        had_tracks = bool(state.current or state.queue)

        state.queue.clear()
        state.current = None
        state.text_channel = ctx.channel

        if voice_client is not None and self._is_voice_active(voice_client):
            state.stopping = True
            voice_client.stop()
            await ctx.send("Stopped and cleared the queue.")
            return

        state.stopping = False
        await ctx.send("Cleared the queue." if had_tracks else "Nothing is playing.")

    @commands.hybrid_command(
        name="leave",
        with_app_command=True,
        description="Disconnect from the voice channel",
    )
    async def leave(self, ctx: commands.Context[Any]) -> None:
        if ctx.guild is None:
            await ctx.send("This command can be used only in a server.")
            return

        voice_client = self._get_voice_client(ctx.guild.id)
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("I'm not connected to a voice channel.")
            return

        state = self.states.get(ctx.guild.id)
        if state is not None:
            state.queue.clear()
            state.current = None
            state.stopping = True

        await voice_client.disconnect(force=True)
        self.states.pop(ctx.guild.id, None)
        await ctx.send("Disconnected and cleared the queue.")

    @commands.hybrid_command(
        name="queue",
        with_app_command=True,
        description="Show the music queue",
    )
    async def queue_command(self, ctx: commands.Context[Any]) -> None:
        if ctx.guild is None:
            await ctx.send("This command can be used only in a server.")
            return

        state = self.states.get(ctx.guild.id)
        if state is None or (state.current is None and not state.queue):
            await ctx.send("The queue is empty.")
            return

        embed = discord.Embed(title="Music queue", color=0xFF6961)
        if state.current is not None:
            embed.add_field(
                name="Now playing",
                value=(
                    f"**{self._shorten(state.current.title)}** "
                    f"({self._format_duration(state.current.duration)})\n"
                    f"Requested by {state.current.requested_by}"
                ),
                inline=False,
            )

        if state.queue:
            lines = []
            for index, track in enumerate(list(state.queue)[:MAX_QUEUE_DISPLAY], start=1):
                lines.append(
                    f"`{index}.` {self._shorten(track.title, 65)} "
                    f"({self._format_duration(track.duration)})"
                )

            remaining = len(state.queue) - MAX_QUEUE_DISPLAY
            if remaining > 0:
                lines.append(f"...and {remaining} more")

            embed.add_field(name="Up next", value="\n".join(lines), inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="nowplaying",
        aliases=["np"],
        with_app_command=True,
        description="Show the current track",
    )
    async def nowplaying(self, ctx: commands.Context[Any]) -> None:
        if ctx.guild is None:
            await ctx.send("This command can be used only in a server.")
            return

        state = self.states.get(ctx.guild.id)
        if state is None or state.current is None:
            await ctx.send("Nothing is playing.")
            return

        track = state.current
        await ctx.send(
            f"Now playing: **{self._shorten(track.title)}** "
            f"({self._format_duration(track.duration)}) requested by {track.requested_by}"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
