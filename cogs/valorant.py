"""Cog — Valorant.

Commands
--------
$agent           —  assign a random Valorant agent
$agents <map>    —  show META agents for a map, then optionally pick one
"""

import asyncio
import random

import discord
from discord.ext import commands

# All currently playable agents (update when new agents release).
VAL_AGENTS: list[str] = [
    'Astra', 'Breach', 'Brimstone', 'Chamber', 'Cypher',
    'Deadlock', 'Fade', 'Gekko', 'Harbor', 'Iso',
    'Jett', 'KAY/O', 'Killjoy', 'Neon', 'Omen',
    'Phoenix', 'Raze', 'Reyna', 'Sage', 'Skye',
    'Sova', 'Viper', 'Vyse', 'Yoru',
]

# All active maps.
VAL_MAPS: list[str] = [
    'Abyss', 'Ascent', 'Bind', 'Breeze', 'Fracture',
    'Haven', 'Icebox', 'Lotus', 'Pearl', 'Split', 'Sunset',
]

# High-pick-rate agents per map.  Empty list = no data yet.
MOST_PICKED: dict[str, list[str]] = {
    'Abyss':    [],
    'Ascent':   ['Jett', 'Sova', 'Omen', 'Killjoy', 'Reyna'],
    'Bind':     ['Raze', 'Brimstone', 'Jett', 'Skye', 'Cypher'],
    'Breeze':   ['Jett', 'Viper', 'Sova', 'Cypher', 'Reyna'],
    'Fracture': [],
    'Haven':    [],
    'Icebox':   ['Jett', 'Viper', 'Reyna', 'Sova', 'Killjoy'],
    'Lotus':    ['Raze', 'Omen', 'Jett', 'Killjoy', 'Reyna'],
    'Pearl':    [],
    'Split':    ['Jett', 'Raze', 'Cypher', 'Skye', 'Omen'],
    'Sunset':   ['Cypher', 'Omen', 'Jett', 'Raze', 'Fade'],
}


class Valorant(commands.Cog):
    """Valorant agent and map META commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='agent')
    async def agent(self, ctx: commands.Context) -> None:
        """Assign a random Valorant agent.

        Usage: $agent
        """
        chosen = random.choice(VAL_AGENTS)
        await ctx.send(f"Looks like you're playing **{chosen}**!")

    @commands.command(name='agents')
    async def agents(self, ctx: commands.Context, *, map_name: str) -> None:
        """Show META agents for a Valorant map, then offer to pick one at random.

        Waits up to 30 seconds for a y/n reply from the original author only.

        Usage: $agents <map>
        Example: $agents Ascent
        """
        map_formatted = map_name.strip().title()

        if map_formatted not in VAL_MAPS:
            await ctx.send(
                f"Couldn't find map **{map_formatted}**. "
                f"Available maps: {', '.join(VAL_MAPS)}"
            )
            return

        meta = MOST_PICKED.get(map_formatted, [])
        if not meta:
            await ctx.send(f"No META data available for **{map_formatted}** yet.")
            return

        await ctx.send(f"The META on **{map_formatted}** is: {', '.join(meta)}")
        await ctx.send("Would you like an agent from the META picks? (y/n)")

        # Scope the listener to the original author so other users can't hijack it.
        def from_author(m: discord.Message) -> bool:
            return m.channel == ctx.channel and m.author == ctx.author

        while True:
            try:
                response = await self.bot.wait_for('message', check=from_author, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send("Timed out — no response received.")
                break

            if response.content.lower() == 'y':
                await ctx.send(f"Looks like you're playing **{random.choice(meta)}**!")
                break
            elif response.content.lower() == 'n':
                await ctx.send("Boring! Go play your comfort pick.")
                break
            else:
                await ctx.send("Please reply with **y** or **n**.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Valorant(bot))
