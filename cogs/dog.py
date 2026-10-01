"""Cog — Dog.

Fetches random dog images from the Dog CEO API
(dog.ceo/api — free, no API key required).

Commands
--------
$dog          —  a random dog image
$dog <breed>  —  a random image of a specific breed
"""

import aiohttp
import discord
from discord.ext import commands

RANDOM_URL = "https://dog.ceo/api/breeds/image/random"
BREED_URL = "https://dog.ceo/api/breed/{}/images/random"


class Dog(commands.Cog):
    """Random dog images via the Dog CEO API (no API key required)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="dog")
    async def dog(self, ctx: commands.Context, *, breed: str | None = None) -> None:
        """Show a random dog image, or a random image of a specific breed.

        Usage: $dog [breed]
        Examples:
            $dog
            $dog husky
            $dog retriever golden  (sub-breeds go "breed subbreed", per the Dog CEO API)
        """
        url = RANDOM_URL if not breed else BREED_URL.format(breed.strip().lower().replace(" ", "/"))

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 404:
                    await ctx.send(f"Couldn't find a breed called **{breed}**. Check your spelling.")
                    return
                if resp.status != 200:
                    await ctx.send("Dog CEO API is unavailable right now. Try again later.")
                    return
                data = await resp.json()

        if data.get("status") != "success":
            await ctx.send(f"Couldn't find a breed called **{breed}**. Check your spelling.")
            return

        embed = discord.Embed(
            title=f"🐶 {breed.title() if breed else 'Random Dog'}",
            color=discord.Color.orange(),
        )
        embed.set_image(url=data["message"])
        embed.set_footer(text="Powered by Dog CEO · dog.ceo")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dog(bot))
