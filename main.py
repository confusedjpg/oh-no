import os
import logging

import discord
from dotenv import load_dotenv

# set up env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# log everything to a file
# no need to keep logs of previous sessions, set mode to 'a' otherwise
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}. Ready to operate!")

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)