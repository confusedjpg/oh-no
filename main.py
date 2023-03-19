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
OWNER_ID = int(os.getenv("OWNER_ID"))

# log everything to a file
# no need to keep logs of previous sessions, set mode to 'a' otherwise
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# set required intents
# for more privileged intents, going to the bot's dashboard might be a good idea
# for more info: https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.default()
intents.message_content = True

# note: never forget this intent when working with members
# otherwise you will debug your code for 1h before realising it
intents.members = True

# create the bot, without the help command because I am a big boy now and can do my own help command
# ...what the fuck am I doing
bot = commands.Bot(command_prefix=PREFIX, description="A general purpose bot.", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id}). \nReady to operate!")
    await bot.change_presence(activity=discord.Game(STATUS))

@bot.listen('on_message')
async def messageHandler(message: discord.Message):
    # a listener to process messages asynchronously
    # don't handle commands here
    if message.author.id == bot.application_id:
        return

# help command embed
# it's supposed to be a rich embed, containing useful and detailed informations about ALL commands, classified by categories
# for later reference: 
# keep in mind that a discord.ext.commands.Command object has attributes pointing to all the information you'd need to display in a help embed
@bot.command(name="help")
async def _help(ctx: commands.Context, command: str = None):
    """Displays a nice help embed
    
    command: A command on which you need more detailed info

    Usage::
        help log
    """

    if command != None and command in [cmd.name for cmd in bot.commands]:
        Embed = discord.Embed(title=command, description=[cmd.help for cmd in bot.commands if cmd.name == command][0], color=discord.Color.green())

    else:
        # create embed
        Embed = discord.Embed(title="help", description="A curated list of all commands the bot has.", color=discord.Color.green())
        
        # cycle through every command object
        value = ""
        for cmd in bot.commands:
            # then fetch and add their name + description to the embed
            description = cmd.help.split('\n')[0]
            value += f"{cmd.name} - {description}\n"
        Embed.add_field(name="Commands", value=value)

    # set author and footer
    Embed.set_author(name=bot.get_user(OWNER_ID).name, icon_url=bot.get_user(OWNER_ID).avatar.url)
    Embed.add_field(name="Note", value=f"Type `{bot.command_prefix}help <command>` to get more help with a specific command.", inline=False)

    # finally, send embed
    await ctx.send(embed=Embed)

@bot.command(name="log")
async def log(ctx: commands.Context):
    """Returns most recent log in file form
    
    Usage::
        log 
    
    (I mean really, what did you expect)
    """

    await ctx.send(file=discord.File('discord.log'))

# the next two commands seem very similar
# but I don't see how to improve them yet...too bad!
@bot.command(name="prefix")
async def prefix(ctx: commands.Context, prefix: str = None):
    """ Modify (or not) default prefix.
    
    prefix: Usually a character, but if you want a cursed prefix use a word, or a full on sentence: \"dumb prefix choice\".

    Usage::
        config prefix ! 
    """ 

    with open("config.pkl", "rb") as f:
        config = pickle.load(f)
    
    if not prefix:
        await ctx.send(f"Current prefix: `{config['prefix']}`.")
        return

    config["prefix"] = prefix
    with open("config.pkl", "wb") as f:
        pickle.dump(config, f)

    bot.command_prefix = prefix
    await ctx.send(f"Prefix successfully changed to `{prefix}`")

@bot.command(name="status")
async def status(ctx: commands.Context, status: str = None):
    """ Modify (or not) default status.
    
    status: A word, for a longer status use (double)quotes: \"...\".
    
    Usage::
        config status "Minecraft at 3a.m on a monday night"
    """

    with open("config.pkl", "rb") as f:
        config = pickle.load(f)
    
    if not status:
        await ctx.send(f"Current status: `{config['status']}`.")
        return

    config["status"] = status
    with open("config.pkl", "wb") as f:
        pickle.dump(config, f)

    await bot.change_presence(activity=discord.Game(status))
    await ctx.send(f"Status successfully changed to `{status}`")

# run bot
# log level can be changed to something more specific, if needed
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)