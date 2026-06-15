"""Discord Bot — entry point.

Loads all cogs as extensions and starts the bot.
Add new cogs to the COGS list to register their commands automatically.
"""

import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Cog Registry ───────────────────────────────────────────────────────────────
# Each entry is a dot-path to a module containing an async setup(bot) function.
COGS = [
    "cogs.general",
    "cogs.state_birds",
    "cogs.valorant",
    "cogs.voice",
    "cogs.trivia",
    "cogs.weather",
    "cogs.pokemon",
]

# ── Bot Setup ──────────────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    """Log confirmation once the bot has connected to Discord."""
    logger.info('Logged in as %s (ID: %s)', bot.user, bot.user.id)


# ── Entry Point ────────────────────────────────────────────────────────────────
async def main():
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
            logger.info('Loaded cog: %s', cog)

        token = os.getenv("TOKEN")
        if not token:
            raise RuntimeError("TOKEN environment variable is not set. Add it to your .env file.")

        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
