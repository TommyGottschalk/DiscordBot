"""Cog — Advice.

Fetches random one-line advice from the Advice Slip API
(api.adviceslip.com — free, no API key required).

Commands
--------
$advice  —  a random piece of advice
"""

import aiohttp
import discord
from discord.ext import commands

ADVICE_URL = "https://api.adviceslip.com/advice"


class Advice(commands.Cog):
    """Random advice via the Advice Slip API (no API key required)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="advice")
    async def advice(self, ctx: commands.Context) -> None:
        """Show a random piece of advice.

        Usage: $advice
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(ADVICE_URL) as resp:
                if resp.status != 200:
                    await ctx.send("Advice Slip API is unavailable right now. Try again later.")
                    return
                data = await resp.json()

        embed = discord.Embed(
            description=f"💡 {data['slip']['advice']}",
            color=discord.Color.gold(),
        )
        embed.set_footer(text="Powered by Advice Slip · adviceslip.com")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Advice(bot))
