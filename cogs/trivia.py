"""Cog — Trivia.

Fetches a random multiple-choice question from the Open Trivia Database
(opentdb.com — free, no API key required) and lets users vote by reacting.

Commands
--------
$trivia  —  post a question; react 🇦🇧🇨🇩 within 20 s; answer revealed after timeout
"""

import asyncio
import html
import random

import aiohttp
import discord
from discord.ext import commands

OPENTDB_URL = "https://opentdb.com/api.php?amount=1&type=multiple"

# Regional indicator emojis used as answer letters A–D.
LETTERS: list[str] = ['🇦', '🇧', '🇨', '🇩']

VOTE_TIMEOUT: int = 20  # seconds before the answer is revealed

# opentdb response codes
OPENTDB_SUCCESS      = 0
OPENTDB_RATE_LIMITED = 5


class Trivia(commands.Cog):
    """Interactive multiple-choice trivia powered by Open Trivia DB."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='trivia')
    async def trivia(self, ctx: commands.Context) -> None:
        """Post a random multiple-choice trivia question.

        React with 🇦, 🇧, 🇨, or 🇩 within 20 seconds to cast your vote.
        The correct answer and vote tallies are revealed when time's up.

        Usage: $trivia
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(OPENTDB_URL) as resp:
                if resp.status != 200:
                    await ctx.send("Couldn't reach the trivia API. Try again in a moment.")
                    return
                data = await resp.json()

        if data.get('response_code') == OPENTDB_RATE_LIMITED:
            await ctx.send("Trivia API is rate-limited. Wait a few seconds and try again.")
            return

        result = data['results'][0]

        # opentdb encodes special characters as HTML entities — decode them all.
        question  = html.unescape(result['question'])
        correct   = html.unescape(result['correct_answer'])
        wrong     = [html.unescape(a) for a in result['incorrect_answers']]
        category  = html.unescape(result['category'])
        difficulty = result['difficulty'].capitalize()

        # Shuffle all four answers and note which letter maps to the correct one.
        answers = wrong + [correct]
        random.shuffle(answers)
        correct_letter = LETTERS[answers.index(correct)]

        # ── Build and send the question embed ──────────────────────────────
        choices = "\n".join(f"{LETTERS[i]}  {answers[i]}" for i in range(4))
        embed = discord.Embed(
            title=f"❓ {question}",
            description=f"{choices}\n\n*React with your answer — {VOTE_TIMEOUT}s on the clock!*",
            color=discord.Color.blurple(),
        )
        embed.set_footer(text=f"{category}  ·  {difficulty}")

        msg = await ctx.send(embed=embed)

        # Add the four reaction options in order.
        for letter in LETTERS:
            await msg.add_reaction(letter)

        await asyncio.sleep(VOTE_TIMEOUT)

        # Re-fetch the message so reaction counts reflect all votes cast.
        msg = await ctx.channel.fetch_message(msg.id)

        # Tally votes, subtracting 1 per reaction to exclude the bot's own reaction.
        counts: dict[str, int] = {}
        for reaction in msg.reactions:
            emoji = str(reaction.emoji)
            if emoji in LETTERS:
                counts[emoji] = max(reaction.count - 1, 0)

        # Build a results line: show each letter's count and tick the winner.
        results = "  |  ".join(
            f"{letter} **{counts.get(letter, 0)}**{'  ✅' if letter == correct_letter else ''}"
            for letter in LETTERS
        )

        result_embed = discord.Embed(
            title="⏰ Time's up!",
            description=(
                f"The correct answer was {correct_letter}  **{correct}**\n\n"
                f"{results}"
            ),
            color=discord.Color.green(),
        )
        await ctx.send(embed=result_embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Trivia(bot))
