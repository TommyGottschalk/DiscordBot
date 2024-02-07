"""State Bird and Valorant bot"""

import random
import os
import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    """Shows bot login status"""
    print(f'We have logged in as {bot.user}')


@bot.command(name='hello')
async def hello(ctx):
    """Responds to command with prompt"""
    await ctx.send("Sup bitch")


@bot.command(name='bird')  #Naming the input user types to call command
async def bird(ctx, arg):
    """Calls dictionary to retrieve key from prompt"""
    state_bird = {
        'Alabama': 'Yellowhammer (northern flicker)',
        'Alaska': 'Willow ptarmigan',
        'Arizona': 'Cactus wren',
        'Arkansas': 'Northern mockingbird',
        'California': 'California quail',
        'Colorado': 'Lark bunting',
        'Connecticut': 'American robin',
        'Delaware': 'Blue hen chicken',
        'Florida': 'Northern mockingbird',
        'Georgia': 'Brown thrasher',
        'Hawaii': 'Nene (Hawaiian goose)',
        'Idaho': 'Mountain bluebird',
        'Illinois': 'Northern cardinal',
        'Indiana': 'Northern cardinal',
        'Iowa': 'Eastern goldfinch',
        'Kansas': 'Western meadowlark',
        'Kentucky': 'Northern cardinal',
        'Louisiana': 'Brown pelican',
        'Maine': 'Black-capped chickadee',
        'Maryland': 'Baltimore oriole',
        'Massachusetts': 'Black-capped chickadee',
        'Michigan': 'American robin',
        'Minnesota': 'Common loon',
        'Mississippi': 'Northern mockingbird',
        'Missouri': 'Eastern bluebird',
        'Montana': 'Western meadowlark',
        'Nebraska': 'Western meadowlark',
        'Nevada': 'Mountain bluebird',
        'New Hampshire': 'Purple finch',
        'New Jersey': 'Eastern goldfinch',
        'New Mexico': 'Greater roadrunner',
        'New York': 'Eastern bluebird',
        'North Carolina': 'Northern cardinal',
        'North Dakota': 'Western meadowlark',
        'Ohio': 'Northern cardinal',
        'Oklahoma': 'Scissor-tailed flycatcher',
        'Oregon': 'Western meadowlark',
        'Pennsylvania': 'Ruffed grouse',
        'Rhode Island': 'Rhode Island red',
        'South Carolina': 'Carolina wren',
        'South Dakota': 'Ring-necked pheasant',
        'Tennessee': 'Northern mockingbird',
        'Texas': 'Northern mockingbird',
        'Utah': 'California gull',
        'Vermont': 'Hermit thrush',
        'Virginia': 'Northern cardinal',
        'Washington': 'Willow goldfinch',
        'West Virginia': 'Northern cardinal',
        'Wisconsin': 'American robin',
        'Wyoming': 'Western meadowlark',
    }
    arg_formatted = arg.lower().capitalize()    #setting arg to lower and capitalizing first char
    if arg_formatted in state_bird:  #if user input(arg) is in dictionary 'stateBird'
        chosen_bird = state_bird[arg_formatted]  #Declaring chosen_bird to state_bird key
        await ctx.send(f"The state bird of {arg_formatted} is the {chosen_bird}")  #print messgae
    else:
        await ctx.send(f"I can't seem to find the state bird for {arg_formatted}")

valAgents = [
    (0, 'Astra'), (1, 'Breach'), (2, 'Brimstone'), (3, 'Chamber'),
    (4, 'Cypher'), (5, 'Deadlock'), (6, 'Fade'), (7, 'Gekko'), (8, 'Harbor'), (9, 'Iso'),
    (10, 'Jett'), (11, 'KAY/O'), (12, 'Killjoy'), (13, 'Neon'), (14, 'Omen'), (15, 'Phoenix'),
    (16, 'Raze'), (17, 'Reyna'), (18, 'Sage'), (19, 'Skye'),
    (20, 'Sova'), (21, 'Viper'), (22, 'Yoru'),
]

valMaps = [
    (0, 'Ascent'), (1, 'Bind'), (2, 'Breeze'), (3, 'Fracture'), (4, 'Haven'),
    (5, 'Icebox'), (6, 'Lotus'), (7, 'Pearl'), (8, 'Split'), (9, 'Sunset'),
]

mostPicked = {
        valMaps[0]: [valAgents[10], valAgents[20], valAgents[14], valAgents[12], valAgents[17]],
        valMaps[1]: [valAgents[16], valAgents[2], valAgents[10], valAgents[19], valAgents[4]],
        valMaps[2]: [valAgents[10], valAgents[21], valAgents[20], valAgents[4], valAgents[17]],
        valMaps[3]: [None],
        valMaps[4]: [None],
        valMaps[5]: [valAgents[10], valAgents[21], valAgents[17], valAgents[20], valAgents[12]],
        valMaps[6]: [valAgents[16], valAgents[14], valAgents[10], valAgents[12], valAgents[17]],
        valMaps[7]: [None],
        valMaps[8]: [valAgents[10], valAgents[16], valAgents[4], valAgents[19], valAgents[14]],
        valMaps[9]: [valAgents[4], valAgents[14], valAgents[10], valAgents[16], valAgents[6]],
    }


@bot.command(name='agent')
async def agent(ctx):
    """Assigns user random choice from valAgents list"""
    random_agent = random.choice(valAgents) #random element to select user agent
    await ctx.send(f"Looks like you're playing {random_agent}") #prints selected random agent


@bot.command(name='agents')
async def agents(ctx, arg): #function takes in an arg(user input for map)
    """Prints META agents on selected map"""
    arg_formatted = arg.lower().capitalize()
    if arg_formatted in valMaps:
        meta = mostPicked[arg_formatted]
        await ctx.send(f"The META on {arg_formatted} is {meta}")
    else:
        await ctx.send(f"I couldn't find the map {arg_formatted}")


bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    pass
