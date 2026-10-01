"""Cog — Minecraft Server Status.

Checks a Minecraft server via the Minecraft Server Status API
(api.mcsrvstat.us — free, no API key required) and reports who's online.

A background task polls the server on an interval and posts to a configured
channel only when something changes (server goes on/offline, a player joins
or leaves) — it never spams the channel with unchanged status.

Commands
--------
$mcstatus  —  check the configured Minecraft server right now

Environment variables
----------------------
MC_SERVER_ADDRESS        —  required. Server address, e.g. "play.example.com"
                             or "play.example.com:25566".
MC_STATUS_CHANNEL_ID     —  optional. Channel ID for automatic join/leave
                             alerts. If unset, the background task is disabled
                             and only the manual $mcstatus command works.
MC_STATUS_INTERVAL_MINUTES —  optional, default 2. How often to poll.
                             mcsrvstat.us caches results for about a minute,
                             so polling faster than that gains nothing.
"""

import logging
import os

import aiohttp
import discord
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)

MCSRVSTAT_URL = "https://api.mcsrvstat.us/3/{}"

MC_SERVER_ADDRESS = os.getenv("MC_SERVER_ADDRESS", "").strip()
MC_STATUS_INTERVAL_MINUTES = float(os.getenv("MC_STATUS_INTERVAL_MINUTES", "2"))

_raw_channel_id = os.getenv("MC_STATUS_CHANNEL_ID", "").strip()
MC_STATUS_CHANNEL_ID: int | None = None
if _raw_channel_id:
    try:
        MC_STATUS_CHANNEL_ID = int(_raw_channel_id)
    except ValueError:
        logger.warning(
            "MC_STATUS_CHANNEL_ID=%r is not a valid channel ID — "
            "automatic Minecraft status alerts are disabled.",
            _raw_channel_id,
        )


async def fetch_status(session: aiohttp.ClientSession, address: str) -> dict | None:
    """Query mcsrvstat.us for a server's status. Returns None on request failure."""
    async with session.get(MCSRVSTAT_URL.format(address)) as resp:
        if resp.status != 200:
            return None
        return await resp.json()


def build_status_embed(address: str, status: dict) -> discord.Embed:
    """Build an embed summarizing a server status payload from mcsrvstat.us."""
    if not status.get("online"):
        embed = discord.Embed(
            title="🔴 Server Offline",
            description=f"**{address}** is not responding.",
            color=discord.Color.red(),
        )
        embed.set_footer(text="Powered by mcsrvstat.us")
        return embed

    players = status.get("players", {})
    online_count = players.get("online", 0)
    max_count = players.get("max", 0)
    names = [p["name"] for p in players.get("list", [])]

    embed = discord.Embed(
        title="🟢 Server Online",
        description=f"**{address}**",
        color=discord.Color.green(),
    )
    embed.add_field(name="Players", value=f"{online_count}/{max_count}", inline=True)
    if "version" in status:
        embed.add_field(name="Version", value=status["version"], inline=True)
    if names:
        embed.add_field(name="Online Now", value=", ".join(names), inline=False)
    embed.set_footer(text="Powered by mcsrvstat.us")
    return embed


class Minecraft(commands.Cog):
    """Minecraft server status via mcsrvstat.us (no API key required)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # Remembers the last-seen state so the auto-check can diff it and
        # only post when something actually changed.
        self._last_online: bool | None = None
        self._last_players: set[str] = set()

    async def cog_load(self) -> None:
        if not MC_SERVER_ADDRESS:
            logger.info(
                "MC_SERVER_ADDRESS not set — Minecraft status checks are disabled."
            )
        elif MC_STATUS_CHANNEL_ID is not None:
            self.auto_check.start()
        else:
            logger.info(
                "MC_STATUS_CHANNEL_ID not set — automatic Minecraft status "
                "alerts are disabled. $mcstatus still works on demand."
            )

    async def cog_unload(self) -> None:
        self.auto_check.cancel()

    @commands.command(name="mcstatus")
    async def mcstatus(self, ctx: commands.Context) -> None:
        """Check the configured Minecraft server's status right now.

        Usage: $mcstatus
        """
        if not MC_SERVER_ADDRESS:
            await ctx.send(
                "No Minecraft server configured. Set MC_SERVER_ADDRESS in the bot's .env file."
            )
            return

        async with aiohttp.ClientSession() as session:
            status = await fetch_status(session, MC_SERVER_ADDRESS)

        if status is None:
            await ctx.send("Couldn't reach the Minecraft status API. Try again later.")
            return

        await ctx.send(embed=build_status_embed(MC_SERVER_ADDRESS, status))

    @tasks.loop(minutes=MC_STATUS_INTERVAL_MINUTES)
    async def auto_check(self) -> None:
        """Poll the server on an interval and alert only on state changes."""
        async with aiohttp.ClientSession() as session:
            status = await fetch_status(session, MC_SERVER_ADDRESS)

        if status is None:
            logger.warning("Minecraft status check failed: API request unsuccessful.")
            return

        channel = self.bot.get_channel(MC_STATUS_CHANNEL_ID)
        if channel is None:
            logger.warning(
                "MC_STATUS_CHANNEL_ID=%s does not resolve to a channel the bot can see.",
                MC_STATUS_CHANNEL_ID,
            )
            return

        online = bool(status.get("online"))
        players = {p["name"] for p in status.get("players", {}).get("list", [])}

        # First run after startup: record the baseline silently, don't alert.
        if self._last_online is None:
            self._last_online = online
            self._last_players = players
            return

        if online != self._last_online:
            if online:
                await channel.send(f"🟢 **{MC_SERVER_ADDRESS}** is back online!")
            else:
                await channel.send(f"🔴 **{MC_SERVER_ADDRESS}** went offline.")

        if online:
            joined = players - self._last_players
            left = self._last_players - players
            for name in sorted(joined):
                await channel.send(f"🟩 **{name}** joined the server.")
            for name in sorted(left):
                await channel.send(f"🟥 **{name}** left the server.")

        self._last_online = online
        self._last_players = players


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Minecraft(bot))
