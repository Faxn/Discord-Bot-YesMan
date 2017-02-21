
# Based on https://github.com/rapptz/discord.py

import os, sys, random
import util


#make sure the config file exists
if(not os.path.exists('config.py')):
    with open('config.py', 'w') as config:
        config.write("app_id = ''\ntoken = ''")
        print("Put your client id and bot token from developer.discordapp.com in config.py")
        sys.exit(1)


import discord
from discord.http import HTTPClient
import asyncio

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
    

@bot.command(pass_context = True)
@asyncio.coroutine
async def slurp(ctx):
    bot = ctx.bot
    channel = ctx.message.channel
    
    messages = await util.get_all_messages(bot, channel)
    await bot.send_message(channel, "got %d messages." % (len(messages)))
    
    with open("response.json", 'w') as outfile:
        import json
        outfile.write(json.dumps(messages))
    
    
    return



import config
print('Enter the url below into your browser to be prompted to add the bot to a server you have manage permissions on.')
print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(config.app_id))
bot.run(config.token)

    
