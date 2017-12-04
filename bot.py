#!/usr/bin/env python3
# Based on https://github.com/rapptz/discord.py

import os
import sys
import asyncio
import importlib
import signal
import logging
import argparse

import discord
from discord.enums import ChannelType
from discord.ext import commands

sys.path.insert(0, "lib")




    
blacklist = ["__pycache__", 'lib', 'data', '.', '..', '.git']

def on_sigint(signal, frame):
        print('We have been interrupted.')
        sys.exit(0)

signal.signal(signal.SIGINT, on_sigint)    

def set_logger():
    "logger making function adapted from Red's."
    logger = logging.getLogger("bot.py")
    logger.setLevel(logging.INFO)

    red_format = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(red_format)
    
    stdout_handler.setLevel(logging.DEBUG)
    
    logger.addHandler(stdout_handler)

    return logger

def main(args):
    
    #make sure the config file exists    
    if(not os.path.exists('config.py')):
        with open('config.py', 'w') as config:
            config.write("app_id = ''\ntoken = ''")
            print("Put your client id and bot token from developer.discordapp.com in config.py")
            sys.exit(1)
    import config
    
    print("Starting YesMan")
    bot = commands.Bot(command_prefix='!', description="An agreeable bot.")
    
    #attach logger
    bot.logger = set_logger()
    
    #set debug
    if args.debug:
        bot.logger.setLevel(logging.DEBUG)
        bot.loop.set_debug(True)
    
    
    for f in os.scandir():
        if f.is_dir() and f.name not in blacklist:
            try:
                mod = importlib.import_module("%s.%s" % (f.name, f.name))
                mod.setup(bot)
            except ModuleNotFoundError:
                pass

    @bot.event
    async def on_ready():
        print('Logged in as %s(%s)' % (bot.user.name, bot.user.id))
        print('------')    
    
    print('Enter the url below into your browser to be prompted to add the bot to a server you have manage permissions on.')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(config.app_id))
    bot.run(config.token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if args.debug:
        import cProfile as profile
        logging.basicConfig(level=logging.DEBUG)
        profile.run('main(args)', "restats")
    else:
        logging.basicConfig(filename='bot.log', filemode="w")
        main(args)
