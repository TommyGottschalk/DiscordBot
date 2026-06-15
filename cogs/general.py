"""Cog — General.

Catch-all for simple utility commands that don't belong to a specific category.

Commands
--------
$hello  —  greet the bot
"""

from discord.ext import commands


class General(commands.Cog):
    """General-purpose commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='hello')
    async def hello(self, ctx: commands.Context) -> None:
        """Respond with a greeting.

        Usage: $hello
        """
        await ctx.send("Sup bitch")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
