#!/usr/bin/env python3
# Based on https://github.com/rapptz/discord.py

import os
import sys
import asyncio

import discord
from discord.enums import ChannelType
from discord.ext import commands

sys.path.insert(0, "lib")
bot = commands.Bot(command_prefix='!', description="An agreeable bot.")


@bot.event
async def on_ready():
    print('Logged in as %s(%s)' % (bot.user.name, bot.user.id))
    print('------')

#@bot.listen('on_message')
async def on_message(message):
    if(message.author.id != bot.user.id):
        if(not '!' in message.content):
            await bot.send_message(message.channel, 'I agree')
    

import infodump.infodump
infodump.infodump.setup(bot)

import archiver.archiver
archiver.archiver.setup(bot)

import mimic.mimic
mimic.mimic.setup(bot)

import notifier.notifier
notifier.notifier.setup(bot)

import rgrcog.rgrcog
rgrcog.rgrcog.setup(bot)


def main():
    import signal
    
    print("Starting YesMan")

    def on_sigint(signal, frame):
        print('We have been interrupted.')
        sys.exit(0)
    signal.signal(signal.SIGINT, on_sigint)    
    
    #make sure the config file exists
    if(not os.path.exists('config.py')):
        with open('config.py', 'w') as config:
            config.write("app_id = ''\ntoken = ''")
            print("Put your client id and bot token from developer.discordapp.com in config.py")
            sys.exit(1)
    import config
    print('Enter the url below into your browser to be prompted to add the bot to a server you have manage permissions on.')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(config.app_id))
    bot.run(config.token)


if __name__ == "__main__":
    main()
