"""Cog — Cat Facts.

Fetches random cat facts from the Cat Facts API
(catfact.ninja — free, no API key required).

Commands
--------
$catfact  —  a random cat fact
"""

import aiohttp
import discord
from discord.ext import commands

CATFACT_URL = "https://catfact.ninja/fact"


class CatFact(commands.Cog):
    """Random cat facts via catfact.ninja (no API key required)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="catfact")
    async def catfact(self, ctx: commands.Context) -> None:
        """Show a random cat fact.

        Usage: $catfact
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(CATFACT_URL) as resp:
                if resp.status != 200:
                    await ctx.send("Cat Facts API is unavailable right now. Try again later.")
                    return
                data = await resp.json()

        embed = discord.Embed(
            description=f"🐱 {data['fact']}",
            color=discord.Color.dark_gold(),
        )
        embed.set_footer(text="Powered by catfact.ninja")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CatFact(bot))
