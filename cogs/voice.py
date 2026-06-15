"""Cog — Voice.

Commands
--------
$cok  <@mention|username>  —  join that user's voice channel and play a 35s countdown
$play <file>               —  play any local audio file in your current voice channel
"""

import asyncio
import logging
import os
import re

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

# Audio file for $cok. Override the default path via the COK_AUDIO env variable.
COK_AUDIO_PATH: str = os.getenv(
    'COK_AUDIO',
    r'C:\Users\tjgot\OneDrive\Desktop\30 Second Timer With Jeopardy Thinking Music.mp3',
)
COK_DURATION: int = 35  # seconds the bot stays before disconnecting


class Voice(commands.Cog):
    """Voice-channel commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='cok')
    async def cok(self, ctx: commands.Context, *, arg: str) -> None:
        """Clutch or Kick — join a member's voice channel and play a countdown timer.

        Accepts a @mention or a plain username/display name.

        Usage: $cok <@mention or username>
        """
        # Resolve target member: try mention ID first, then fall back to name search.
        mention_ids = re.findall(r'\d+', arg)
        if mention_ids:
            member = ctx.guild.get_member(int(mention_ids[0]))
        else:
            member = discord.utils.find(
                lambda m: m.name == arg or m.display_name == arg,
                ctx.guild.members,
            )

        if not member:
            await ctx.send(f'Member "{arg}" not found!')
            return

        if not member.voice:
            await ctx.send(f'**{member.display_name}** is not in a voice channel!')
            return

        channel = member.voice.channel
        logger.info('Joining %s for member %s', channel.name, member.name)

        voice_client = await channel.connect()
        await ctx.send(f'Joined **{channel.name}** — tick tock! 🎵')

        # Stream the countdown audio file.
        source = discord.FFmpegPCMAudio(COK_AUDIO_PATH)
        voice_client.play(source)

        await asyncio.sleep(COK_DURATION)

        if voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send(f'Disconnected from **{channel.name}** after {COK_DURATION} seconds.')

    @commands.command(name='play')
    async def play(self, ctx: commands.Context, *, file_name: str) -> None:
        """Play a local audio file in the invoking user's current voice channel.

        The bot auto-disconnects once playback finishes.

        Usage: $play <file path>
        """
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command.")
            return

        channel = ctx.author.voice.channel
        voice_client = await channel.connect()

        source = discord.FFmpegPCMAudio(file_name)
        voice_client.play(source)
        await ctx.send(f'Playing **{file_name}** in **{channel.name}**.')

        # Poll until playback is done, then auto-disconnect.
        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Voice(bot))
