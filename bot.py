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
    
def on_sigint(signal, frame):
        print('We have been interrupted.')
        sys.exit(0)

signal.signal(signal.SIGINT, on_sigint)    

#set up global logging.
logger = logging.getLogger()


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
    
    #Set up logging
    logger.setLevel(logging.INFO)
    log_format = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
    datefmt="[%Y-%m-%d %H:%M]")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)
    stdout_handler.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    file_handler = logging.FileHandler("bot.log", mode='w')
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    #attach logger
    bot.logger = logger
    
    #set debug
    if args.debug:
        bot.logger.setLevel(logging.DEBUG)
    
    for f in os.scandir():
        if f.is_dir() and os.path.exists(os.path.join(f.name, 'info.json')) :
            try:
                mod = importlib.import_module("%s.%s" % (f.name, f.name))
                mod.setup(bot)
                bot.logger.info("loaded module: %s" % f.name)
            except ModuleNotFoundError:
                bot.logger.warn("Failed to load module: %s" %f, exec_info=True)

    @bot.event
    async def on_ready():
        print('Logged in as %s(%s)' % (bot.user.name, bot.user.id))
        print('------')    
    
    print('Enter the url below into your browser to be prompted to add the bot to a server you have manage permissions on.')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(config.app_id))
    bot.run(config.token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord Bot.')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--profile', action='store_true')
    args = parser.parse_args()
    if args.profile:
        import cProfile as profile
        profile.run('main(args)', "stats.prof")
    else:
        main(args)
