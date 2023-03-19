import os
import logging

import discord
from discord.ext import commands # easier command integration
from dotenv import load_dotenv

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

bot = commands.Bot(command_prefix=".", description="A general purpose bot.", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id}). \nReady to operate!")

# add a listener to process messages asynchronously
# don't handle commands here
@bot.listen('on_message')
async def printIt(message):
    print(f"{message.author} said: {message.content}")

bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)