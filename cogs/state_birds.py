"""Cog — US State Birds.

Commands
--------
$bird <state>  —  return the official state bird for a US state
"""

from discord.ext import commands

# Maps every US state to its official state bird (module-level so it's built once).
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


class StateBirds(commands.Cog):
    """Commands related to US state birds."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='bird')
    async def bird(self, ctx: commands.Context, *, state: str) -> None:
        """Return the official state bird for a given US state.

        Uses title() so multi-word states like 'New Hampshire' are handled correctly.

        Usage: $bird <state>
        Examples:
            $bird California
            $bird New Hampshire
        """
        # title() correctly capitalises every word: "new york" → "New York"
        state_formatted = state.strip().title()
        bird_name = STATE_BIRDS.get(state_formatted)

        if bird_name:
            await ctx.send(f"The state bird of **{state_formatted}** is the {bird_name}.")
        else:
            await ctx.send(
                f"Couldn't find a state bird for **{state_formatted}**. "
                "Check your spelling and try again."
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StateBirds(bot))
