#!/usr/bin/env python3
# Based on https://github.com/rapptz/discord.py

import os
import sys
import asyncio
import importlib
import signal

import discord
from discord.enums import ChannelType
from discord.ext import commands

sys.path.insert(0, "lib")




    
blacklist = ["__pycache__", 'lib', 'data', '.', '..', '.git']

def on_sigint(signal, frame):
        print('We have been interrupted.')
        sys.exit(0)

signal.signal(signal.SIGINT, on_sigint)    



def main():
    
    #make sure the config file exists
    if(not os.path.exists('config.py')):
        with open('config.py', 'w') as config:
            config.write("app_id = ''\ntoken = ''")
            print("Put your client id and bot token from developer.discordapp.com in config.py")
            sys.exit(1)
    import config
    
    print("Starting YesMan")
    bot = commands.Bot(command_prefix='!', description="An agreeable bot.")
    
    for f in os.scandir():
        if f.is_dir() and f.name not in blacklist:
            mod = importlib.import_module("%s.%s" % (f.name, f.name))
            mod.setup(bot)

    @bot.event
    async def on_ready():
        print('Logged in as %s(%s)' % (bot.user.name, bot.user.id))
        print('------')    
    
    print('Enter the url below into your browser to be prompted to add the bot to a server you have manage permissions on.')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(config.app_id))
    bot.run(config.token)


if __name__ == "__main__":
    main()
