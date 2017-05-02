#!/usr/bin/env python3
# Based on https://github.com/rapptz/discord.py

import os
import sys
import asyncio

import discord
from discord.enums import ChannelType
from discord.ext import commands



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
    

import archiver.archiver
bot.add_cog(archiver.archiver.Archiver)

import mimic.mimic
bot.add_cog(mimic.mimic.Mimic)


## Util Command
########################################################################
@bot.command(pass_context=True)
@asyncio.coroutine
async def notify(ctx, delay:int):
    user = ctx.message.author
    ack = await ctx.bot.send_message(ctx.message.channel, "I will notify you in %d seconds." % (delay))
    await asyncio.sleep(delay)
    await ctx.bot.send_message(ctx.message.channel, "Hey %s! I'm notifying you!" % (user.mention) )
    try:
        await bot.delete_message(ctx.message)
        await bot.delete_message(ack)
    #todo actually catch or avoid this error to keep the logs clean.
    except discord.ext.commands.errors.CommandInvokeError:
        pass


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
