"""Cog — Pokémon.

Fetches Pokémon data from PokéAPI (pokeapi.co — free, no API key required).

Commands
--------
$pokemon <name>    —  look up a Pokémon by name
$pokemon random    —  look up a random Pokémon (Gens 1–9, IDs 1–1025)
"""

import random

import aiohttp
import discord
from discord.ext import commands

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/{}"

# Generation 1–9 spans Pokédex IDs 1–1025.
MAX_POKEMON_ID = 1025

# Canonical stat display order with short labels.
STAT_LABELS: dict[str, str] = {
    "hp":              "HP ",
    "attack":          "Atk",
    "defense":         "Def",
    "special-attack":  "SpA",
    "special-defense": "SpD",
    "speed":           "Spe",
}


def stat_bar(value: int, max_val: int = 255, width: int = 10) -> str:
    """Return a fixed-width text bar representing a base stat value.

    Example: stat_bar(90, width=10) → '████████░░'
    """
    filled = round(value / max_val * width)
    return "█" * filled + "░" * (width - filled)


class Pokemon(commands.Cog):
    """Pokémon lookup via the PokéAPI (no API key required)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='pokemon')
    async def pokemon(self, ctx: commands.Context, *, name: str) -> None:
        """Look up a Pokémon by name, or get a random one.

        Usage: $pokemon <name|random>
        Examples:
            $pokemon pikachu
            $pokemon Charizard
            $pokemon random
        """
        # Resolve the target: a random Pokédex ID or the user's input.
        if name.strip().lower() == "random":
            target: str | int = random.randint(1, MAX_POKEMON_ID)
        else:
            target = name.strip().lower()

        async with aiohttp.ClientSession() as session:
            async with session.get(POKEAPI_URL.format(target)) as resp:
                if resp.status == 404:
                    await ctx.send(f"Couldn't find a Pokémon named **{name}**. Check your spelling.")
                    return
                if resp.status != 200:
                    await ctx.send("PokéAPI is unavailable right now. Try again later.")
                    return
                data = await resp.json()

        # ── Extract fields ─────────────────────────────────────────────────
        poke_name  = data["name"].replace("-", " ").title()
        poke_id    = data["id"]
        sprite_url = data["sprites"]["front_default"]

        # Types: e.g. "Fire / Flying"
        types = [t["type"]["name"].capitalize() for t in data["types"]]
        type_str = " / ".join(types)

        # Base stats in canonical order, with a visual bar and numeric value.
        raw_stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        stat_lines = "\n".join(
            f"`{label}` {stat_bar(raw_stats[key])}  **{raw_stats[key]}**"
            for key, label in STAT_LABELS.items()
        )

        # Abilities: regular ones first, hidden ability marked separately.
        regular  = [a["ability"]["name"].replace("-", " ").title()
                    for a in data["abilities"] if not a["is_hidden"]]
        hidden   = [a["ability"]["name"].replace("-", " ").title()
                    for a in data["abilities"] if a["is_hidden"]]
        ability_str = " / ".join(regular)
        if hidden:
            ability_str += f"\n*(Hidden: {', '.join(hidden)})*"

        # ── Build embed ────────────────────────────────────────────────────
        embed = discord.Embed(
            title=f"#{poke_id:04d}  {poke_name}",
            description=f"**Type:** {type_str}",
            color=discord.Color.red(),
        )
        embed.add_field(name="Base Stats", value=stat_lines, inline=False)
        embed.add_field(name="Abilities",  value=ability_str, inline=False)

        if sprite_url:
            embed.set_thumbnail(url=sprite_url)

        embed.set_footer(text="Powered by PokéAPI · pokeapi.co")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Pokemon(bot))
