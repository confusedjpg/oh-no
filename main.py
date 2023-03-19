import os
import logging
import pickle

import discord
from discord.ext import commands # easier command integration
from dotenv import load_dotenv

# first time configuration
if not os.path.isfile("config.pkl"):
    with open("config.pkl", "wb") as f:
        pickle.dump({"prefix": input('Choose prefix: '), "status": input("Choose status: ")}, f)

# temporary variables to be used a bit further in the bot initialisation
with open("config.pkl", "rb") as f:
    config = pickle.load(f)
    PREFIX, STATUS =  config["prefix"], config["status"]

# set up env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# log everything to a file
# no need to keep logs of previous sessions, set mode to 'a' otherwise
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# set required intents
# for more privileged intents, going to the bot's dashboard might be required
# for more info: https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, description="A general purpose bot.", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id}). \nReady to operate!")
    await bot.change_presence(activity=discord.Game(STATUS))

# add a listener to process messages asynchronously
# don't handle commands here
@bot.listen('on_message')
async def messageHandler(message: discord.Message):
    pass

@bot.command(name="log", description="Get latest log file")
async def log(ctx: commands.Context):
    """Returns most recent log in file form"""

    await ctx.send(file=discord.File('discord.log'))

# configuration command group
@bot.group(name="config", description="Configure defaults")
async def config(ctx: commands.Context):
    """ Returns current configuration if no parameters are submitted.
        Otherwise changes defaults"""

    if ctx.invoked_subcommand is None:
        with open("config.pkl", "rb") as f:
            await ctx.send(f"Current bot configuration is: {pickle.load(f)}")

# the next two subcommands seem very similar
# but I don't see how to improve them yet...too bad!
@config.command(name="prefix")
async def prefix(ctx: commands.Context, prefix: str = commands.parameter(default=None, description="Usually a character, but if you want a cursed prefix use a word, or a full on sentence: \"dumb prefix choice\".")):
    """ Modify (or not) default prefix.
    
    Usage::

        config prefix ! 
    """ 

    with open("config.pkl", "rb") as f:
        config = pickle.load(f)
    
    if not prefix:
        await ctx.send(f"You didn't provide any prefix, so I left it as: `{config['prefix']}`.")
        return

    config["prefix"] = prefix
    with open("config.pkl", "wb") as f:
        pickle.dump(config, f)

    bot.command_prefix = prefix
    await ctx.send(f"Prefix successfully changed to `{prefix}`")

@config.command(name="status")
async def status(ctx: commands.Context, status: str = commands.parameter(default=None, description="A word, for a longer status use (double)quotes: \"...\".")):
    """ Modify (or not) default status.
    Usage::

        config status "Minecraft at 3a.m on a monday night"
    """

    with open("config.pkl", "rb") as f:
        config = pickle.load(f)
    
    if not status:
        await ctx.send(f"You didn't provide any status, so I left it as: `{config['status']}`.")
        return

    config["status"] = status
    with open("config.pkl", "wb") as f:
        pickle.dump(config, f)

    await bot.change_presence(activity=discord.Game(status))
    await ctx.send(f"Status successfully changed to `{status}`")

# run bot
# log level can be changed to something more specific, if needed
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)