# included modules
import os
import logging
import shelve
import random as rd

# third-party modules
import discord
from discord.ext import commands # easier command integration
from dotenv import load_dotenv

# local "modules"
from tools import *

with shelve.open("config.shlv") as conf:
    # temporary variables to be used a bit further in the bot initialisation
    PREFIX, STATUS =  conf.setdefault("prefix", "!"), conf.setdefault("status", "!help")
    print("Prefix:", PREFIX, "Status:", STATUS)

# set up env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# log everything to a file
# no need to keep logs of previous sessions, set mode to 'a' otherwise
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# set required intents
# for more privileged intents, going to the bot's dashboard might be a good idea
# for more info: https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents().all()
#intents.message_content = True
#intents.presences = True

# note: never forget this intent when working with members
# otherwise you will debug your code for 1h before realising it
#intents.members = True

# create the bot, without the help command because I am a big boy now and can do my own help command
# ...what the fuck am I doing
bot = commands.Bot(command_prefix=PREFIX, description="A general purpose bot.", intents=intents, help_command=None)

# initially fetch some copypastas
print("Getting a few copypastas...")
COPYPASTAS = fetchCopypasta()

@bot.event
async def on_ready():
    # notify login and set default status
    print(f"Logged in as {bot.user} (ID: {bot.user.id}). \nReady to operate!")
    await bot.change_presence(activity=discord.Game(STATUS))

    # make the help embed only once as it would be useless to do it every single time
    # this could be made into a function instead
    global HELP
    # create embed
    HELP = discord.Embed(title="help", description="A curated list of all commands the bot has.", color=discord.Color.green())

    # get all tags
    tags = set()
    for cmd in bot.commands:
        tags.add(cmd.tag)

    # add every category to the embed
    for tag in tags:
        value = ""
        for cmd in bot.commands:
            if cmd.tag == tag:
                description = cmd.help.split('\n')[0]
                value += f"`{cmd.name}` - {description}\n"
        HELP.add_field(name=tag.capitalize(), value=value)


@bot.listen('on_message')
async def messageHandler(message: discord.Message):
    # a listener to process messages asynchronously
    # don't handle commands here
    #if message.author.id == bot.application_id:
    #    return
    pass

@bot.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    # if someone is listening to Spotify, add their song to the bot's "music taste list"
    if after.activity and (after.activity.name == "Spotify"):
        handleSongs(after.activity)

# mostly tool commands

# help command embed
@addTag("utility")
@bot.command(name="help")
async def _help(ctx: commands.Context, command: str = None):
    """Displays a nice help embed
    
    :param command: A command on which you need more detailed info

    Usage::
        help log
    """

    if command != None and command in [cmd.name for cmd in bot.commands]:
        Embed = discord.Embed(title=command, description=[cmd.help for cmd in bot.commands if cmd.name == command][0], color=discord.Color.green())

    else:
        # get default embed made earlier
        # yes, with a global variable
        Embed = HELP

    # set author and footer
    Embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    Embed.set_footer(text=f"Note: type `{bot.command_prefix}help <command>` to get more help with a specific command.")

    # finally, send embed
    await ctx.send(embed=Embed)

@addTag("bot")
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
@addTag("bot")
@bot.command(name="prefix")
async def prefix(ctx: commands.Context, *prefix: str):
    """ Modify (or not) default prefix
    
    :param prefix: Usually a character, but if you want a cursed prefix use a word, or even a full on sentence (I'm not saying it's a dumb idea, but it is)

    Usage::
        config prefix ! 
    """ 
    # unpack that tuple into a string
    prefix = ' '.join(prefix)

    # get config data off the shelf
    with shelve.open("config.shlv") as conf:
        _prefix = conf["prefix"]
    
        # default answer
        if not prefix:
            await ctx.send(f"Current prefix: `{_prefix}`.")
            return
        
        conf["prefix"] = prefix

    # change prefix locally
    bot.command_prefix = prefix
    await ctx.send(f"Prefix successfully changed to `{prefix}`")

@addTag("bot")
@bot.command(name="status")
async def status(ctx: commands.Context, *status: str):
    """ Modify (or not) default status
    
    :param status: A word, or a sentence. Basically anything your heart desires
    
    Usage::
        config status "Minecraft at 3a.m on a monday night"
    """
    # almost same as prefix

    # unpack that tuple into a string
    status = ' '.join(status)

    # open shelf
    with shelve.open("config.shlv") as conf:
        _status = conf["status"]
    
        # default answer, in case of empty args
        if not status:
            await ctx.send(f"Current status: `{_status}`.")
            return
        
        conf["status"] = status

    # change status locally
    await bot.change_presence(activity=discord.Game(status))
    await ctx.send(f"Status successfully changed to `{status}`")

@addTag("bot")
@bot.command(name="haha")
async def haha(ctx: commands.Context):
    """Like a ping command; 
    Returns a response + latency"""

    # send back latency rounded in ms
    # this is the most beautiful thing in this code
    await ctx.send(f"""⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢀⣤⣤⣄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣴⣤⣤⣤⣴⣾⣿⣿⣿⣿⡄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠠⠾⢿⣿⣿⠟⠋⠁⠤⣬⣽⣿⡇⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⡄⠄⠄⢀⣽⣦⡎⠁⠒⠒⢻⣿⣿⣄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⢀⣧⡀⢀⣾⣿⣿⣧⣦⣴⣾⣿⣿⣿⣿⣧⠄⠄⣠⣴⣆⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⡻⣿⣿⣿⣿⣧⢸⣿⣿⣿⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠘⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⣿⣿⣿⣝⣿⡟⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠸⣄⢺⣿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⢿⠄⡀⠄⣸⣿⡿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠸⡆⠄⣀⣛⣫⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠇⠄⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠐⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⠿⠽⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢸⣿⣿⣿⡿⠟⠛⠉⠄⠄⠄⠄⠄⠄⠄⠄\nhaha jonathan, i am a bot\n{int(bot.latency*1000)}ms""")

@addTag("utility")
@bot.command(name="weather")
async def weather(ctx: commands.Context, location: str = None, units: str = "metric"):
    """Get weather at a location.
    Returns data for a random location if nothing is provided
    
    :param location: A city works best. Use quotes for spaced input
    :param units: The units you want data in. Can be standard, metric or imperial

    Usage::
        weather Stockholm
        weather "Los Angeles" imperial
    """

    units = units.lower()
    if units not in ["metric", "standard", "imperial"]:
        units = "metric"

    try:
        name, weather, main, wind = getWeather(location, units=units)
    except:
        await ctx.send("Uh oh! Your location doesn't seem to exist, or the website is down :sob:")
        return

    Embed = discord.Embed(title=name, description=weather["description"])

    unit = '°K' if units == 'standard' else '°C' if units == 'metric' else '°F'

    Embed.add_field(name="Temperature", value=(
        f"Temperature: `{main['temp']}{unit}`\n"
        f"Feels like: `{main['feels_like']}{unit}`\n"
        f"Min temperature: `{main['temp_min']}{unit}`\n"
        f"Max temperature: `{main['temp_max']}{unit}`\n"
    ))

    Embed.add_field(name="Additional factors", value=(
        f"Pressure: `{main['pressure']} hPa`\n"
        f"Humidity: `{main['humidity']}%`\n"
        f"Wind speed: `{wind['speed']} {'miles/hour' if units == 'imperial' else 'meter/sec'}`\n"
        f"Wind direction: `{wind['deg']}°`\n"
    ))

    Embed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png")
    Embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    # manually inserting an url feels cursed but here we are
    Embed.set_footer(text="Information provided by openweathermap.org", icon_url="https://openweathermap.org/themes/openweathermap/assets/img/mobile_app/android-app-top-banner.png")

    await ctx.send(embed=Embed)

# entertainment commands

@addTag("entertainment")
@bot.command(name="copypasta")
async def copypasta(ctx: commands.Context):
    """Get a random copypasta"""

    # it is what it is...
    global COPYPASTAS

    # if list of copypastas is empty, re-fetch copypastas
    if not COPYPASTAS:
        await ctx.send("Wait hold on, I gotta fetch some fresh copypastas...")
        COPYPASTAS = fetchCopypasta()
    
    if COPYPASTAS == None:
        await ctx.send("Uh oh! The copypasta store seems to be empty right now :sob:")
        return

    # fetch one from the list and delete it
    rand = rd.choice(list(COPYPASTAS.keys()))
    title, copypasta = rand, COPYPASTAS[rand]
    del COPYPASTAS[rand]

    # make an embed, for prettier visuals
    Embed = discord.Embed(title=title, description=copypasta)
    Embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    Embed.set_footer(text="Note: this command relies on how https://www.twitchquotes.com/random/feed is built. This means that it can break at any point.")

    # finally, send embed
    await ctx.send(embed=Embed)

@addTag("entertainment")
@bot.command(name="xkcd")
async def xkcd(ctx: commands.Context):
    """Get a random xkcd comic"""

    # do you even work?
    try:
        title, url, desc = fetchComic()
    except:
        await ctx.send("Uh oh! Randall forgot to pay for the domain name...")

    # making of the embed
    Embed = discord.Embed(title=title, description="xkcd.com")
    Embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    Embed.set_image(url=url)
    Embed.set_footer(text=desc)

    await ctx.send(embed=Embed)

@addTag("entertainment")
@bot.command(name="song")
async def song(ctx: commands.Context):
    """Fetch a random song the bot likes
    The bot takes the songs from a "database" he builds over time.
    He takes songs from the users in the servers he's in: it's what makes it his "music taste".
    So, go on, listen to some music when the bot is there!"""
    
    # get a random song's data
    try:
        data = rd.choice(list(handleSongs().values()))
    except:
        await ctx.channel.send("I have no musical taste...yet :sob:")

    # create embed accordingly
    Embed = discord.Embed(description=f"by {', '.join(data['artists'])}\non {data['album']}", color=data["color"])
    Embed.set_author(name=data['title'], url=data["track_url"])
    Embed.set_thumbnail(url=data["album_cover_url"])
    
    await ctx.channel.send(embed=Embed)

# run bot
# log level can be changed to something more specific, if needed
bot.run(TOKEN, log_handler=handler)