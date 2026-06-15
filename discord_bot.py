"""Discord bot — State Birds and Valorant utilities.

Commands
--------
$hello              — greet the bot
$bird  <state>      — look up a US state bird (multi-word states supported)
$agent              — get a random Valorant agent
$agents <map>       — show META agents for a map, then optionally pick one
$cok   <@user|name> — join that user's voice channel and play a 35-second countdown
$play  <file>       — play any local audio file in your current voice channel
"""

import asyncio
import logging
import os
import random
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
# Use the standard logger instead of raw print() so output level is controllable.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Bot Setup ──────────────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

# ── Data: State Birds ──────────────────────────────────────────────────────────
# Module-level constant so it is built once, not on every command invocation.
STATE_BIRDS: dict[str, str] = {
    'Alabama':        'Yellowhammer (Northern Flicker)',
    'Alaska':         'Willow Ptarmigan',
    'Arizona':        'Cactus Wren',
    'Arkansas':       'Northern Mockingbird',
    'California':     'California Quail',
    'Colorado':       'Lark Bunting',
    'Connecticut':    'American Robin',
    'Delaware':       'Blue Hen Chicken',
    'Florida':        'Northern Mockingbird',
    'Georgia':        'Brown Thrasher',
    'Hawaii':         'Nene (Hawaiian Goose)',
    'Idaho':          'Mountain Bluebird',
    'Illinois':       'Northern Cardinal',
    'Indiana':        'Northern Cardinal',
    'Iowa':           'Eastern Goldfinch',
    'Kansas':         'Western Meadowlark',
    'Kentucky':       'Northern Cardinal',
    'Louisiana':      'Brown Pelican',
    'Maine':          'Black-Capped Chickadee',
    'Maryland':       'Baltimore Oriole',
    'Massachusetts':  'Black-Capped Chickadee',
    'Michigan':       'American Robin',
    'Minnesota':      'Common Loon',
    'Mississippi':    'Northern Mockingbird',
    'Missouri':       'Eastern Bluebird',
    'Montana':        'Western Meadowlark',
    'Nebraska':       'Western Meadowlark',
    'Nevada':         'Mountain Bluebird',
    'New Hampshire':  'Purple Finch',
    'New Jersey':     'Eastern Goldfinch',
    'New Mexico':     'Greater Roadrunner',
    'New York':       'Eastern Bluebird',
    'North Carolina': 'Northern Cardinal',
    'North Dakota':   'Western Meadowlark',
    'Ohio':           'Northern Cardinal',
    'Oklahoma':       'Scissor-Tailed Flycatcher',
    'Oregon':         'Western Meadowlark',
    'Pennsylvania':   'Ruffed Grouse',
    'Rhode Island':   'Rhode Island Red',
    'South Carolina': 'Carolina Wren',
    'South Dakota':   'Ring-Necked Pheasant',
    'Tennessee':      'Northern Mockingbird',
    'Texas':          'Northern Mockingbird',
    'Utah':           'California Gull',
    'Vermont':        'Hermit Thrush',
    'Virginia':       'Northern Cardinal',
    'Washington':     'Willow Goldfinch',
    'West Virginia':  'Northern Cardinal',
    'Wisconsin':      'American Robin',
    'Wyoming':        'Western Meadowlark',
}

# ── Data: Valorant ─────────────────────────────────────────────────────────────
# All playable agents (update this list when new agents are released).
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
# Agent names used directly here instead of index references for clarity.
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

# ── Config ─────────────────────────────────────────────────────────────────────
# Audio file for $cok.  Override the default path via the COK_AUDIO env variable.
COK_AUDIO_PATH: str = os.getenv(
    'COK_AUDIO',
    r'C:\Users\tjgot\OneDrive\Desktop\30 Second Timer With Jeopardy Thinking Music.mp3',
)
COK_DURATION: int = 35  # seconds the bot stays in the channel before disconnecting


# ── Events ─────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    """Log confirmation once the bot has connected to Discord."""
    logger.info('Logged in as %s (ID: %s)', bot.user, bot.user.id)


# ── General Commands ───────────────────────────────────────────────────────────

@bot.command(name='hello')
async def hello(ctx):
    """Respond with a greeting.

    Usage: $hello
    """
    await ctx.send("Sup bitch")


# ── State Bird Commands ────────────────────────────────────────────────────────

@bot.command(name='bird')
async def bird(ctx, *, state: str):
    """Return the official state bird for a given US state.

    Uses title() so multi-word states like 'New Hampshire' are handled correctly.
    The original code used capitalize(), which lowercases every word after the first.

    Usage: $bird <state>
    Examples:
        $bird California
        $bird New Hampshire
    """
    # title() correctly handles multi-word names: "new york" → "New York"
    state_formatted = state.strip().title()
    bird_name = STATE_BIRDS.get(state_formatted)

    if bird_name:
        await ctx.send(f"The state bird of **{state_formatted}** is the {bird_name}.")
    else:
        await ctx.send(
            f"Couldn't find a state bird for **{state_formatted}**. "
            "Check your spelling and try again."
        )


# ── Valorant Commands ──────────────────────────────────────────────────────────

@bot.command(name='agent')
async def agent(ctx):
    """Assign a random Valorant agent.

    Usage: $agent
    """
    chosen = random.choice(VAL_AGENTS)
    await ctx.send(f"Looks like you're playing **{chosen}**!")


@bot.command(name='agents')
async def agents(ctx, *, map_name: str):
    """Show the META agent picks for a Valorant map, then offer to pick one at random.

    After listing the META, waits up to 30 seconds for a y/n reply.
    Only listens to the original command author to avoid cross-talk.

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

    # Scope the listener to the author so other users can't hijack the prompt.
    def from_author(m: discord.Message) -> bool:
        return m.channel == ctx.channel and m.author == ctx.author

    while True:
        try:
            response = await bot.wait_for('message', check=from_author, timeout=30)
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


# ── Voice Commands ─────────────────────────────────────────────────────────────

@bot.command(name='cok')
async def cok(ctx, *, arg: str):
    """Clutch or Kick — join a member's voice channel and play a countdown timer.

    Accepts a @mention or a plain username/display name.

    Usage: $cok <@mention or username>
    """
    # Resolve the target member: try mention first, then fall back to name search.
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


@bot.command(name='play')
async def play(ctx, *, file_name: str):
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

    # Poll until playback is done before disconnecting.
    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError("TOKEN environment variable is not set. Add it to your .env file.")
    bot.run(token)
