
# Based on https://github.com/rapptz/discord.py

import os, sys, random
import util
import asyncio


#make sure the config file exists
if(not os.path.exists('config.py')):
    with open('config.py', 'w') as config:
        config.write("app_id = ''\ntoken = ''")
        print("Put your client id and bot token from developer.discordapp.com in config.py")
        sys.exit(1)


import discord
from discord.enums import ChannelType
from discord.http import HTTPClient
from discord.ext import commands

# A dice bot for use with Discord
bot = commands.Bot(command_prefix='!', description="An agreeable bot.")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.listen('on_message')
async def on_message(message):
    if(message.author.id != bot.user.id):
        if(not '!' in message.content):
            await bot.send_message(message.channel, 'I agree')
    

@bot.command(aliases=[], pass_context = True)
@asyncio.coroutine
async def slurp(ctx):
    bot = ctx.bot
    channel = ctx.message.channel
    
    messages = await util.get_all_messages(bot, channel)
    await bot.send_message(channel, "got %d messages." % (len(messages)))
    
    return

@bot.command(aliases=[], pass_context = True)
@asyncio.coroutine
async def archive(ctx, channel_p : str):
    bot = ctx.bot
    
    channel = bot.get_channel(channel_p)
    
    messages = await util.get_all_messages(bot, channel)
    await bot.send_message(channel, "got %d messages." % (len(messages)))
    
    return


@bot.command(aliases=[], pass_context = True)
@asyncio.coroutine
async def show_channels(ctx):
    bot = ctx.bot
    
    channels = {}
    out=""
    
    for channel in bot.get_all_channels():
        channels[channel.name] = channel
        out += "%s\t%s/n" % (channel.id, channel.name)
    print(out)
    print(repr(channels))
    await bot.send_message(ctx.message.channel, out)
    
    return


@bot.command(pass_context = True)
@asyncio.coroutine
async def archive_all(ctx):
    bot = ctx.bot
    for channel in bot.get_all_channels():
        print("%s:%s, %s" % ( channel.id, channel.name, channel.type))
        if (channel.type is ChannelType.text and 
        not os.path.exists(util.get_storage(channel))):
            try:
                messages = await util.get_all_messages(bot, channel)
                print("got %d message" % (len(messages)))
            except Exception as e:
                print (repr(e))


import config
print('Enter the url below into your browser to be prompted to add the bot to a server you have manage permissions on.')
print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(config.app_id))
bot.run(config.token)

    
