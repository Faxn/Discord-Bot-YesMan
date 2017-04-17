
# Based on https://github.com/rapptz/discord.py

import os, sys, random
import archive
import archive as util
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
    
## Control Commands
########################################################################



## Archiving Commands
########################################################################
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
async def show_channels(ctx):
    bot = ctx.bot
    
    channels = {}
    out=""
    
    for channel in bot.get_all_channels():
        channels[channel.name] = channel
        out += "%s\t%s\n" % (channel.id, channel.name)
    print(out)
    print(repr(channels))
    await bot.send_message(ctx.message.channel, out)
    
    return

@bot.command(aliases=[], pass_context = True)
@asyncio.coroutine
async def show_users(ctx):
    bot = ctx.bot
    out = ""
    for member in ctx.message.server.members:
        out += "%s(%s)" % (member.name, member.id)
    await bot.send_message(channel, out)

@bot.command(aliases=[], pass_context = True)
@asyncio.coroutine
async def show_all_users(ctx):
    bot = ctx.bot
    out = ""
    for member in bot.get_all_members():
        out += "%s(%s)" % (member.name, member.id)
    await bot.send_message(channel, out)


@bot.command(aliases=[], pass_context = True)
@asyncio.coroutine
async def archive_3(ctx, channel_p : str):
    bot = ctx.bot
    
    channel = bot.get_channel(channel_p)
    
    messages = await util.get_all_messages(bot, channel)
    await bot.send_message(channel, "got %d messages." % (len(messages)))
    
    return

@bot.command(pass_context = True)
@asyncio.coroutine
async def archive_all(ctx):
    bot = ctx.bot
    for channel in bot.get_all_channels():
        #print("%s:%s, %s" % ( channel.id, channel.name, channel.type))
        if channel.type is ChannelType.text:
            try:
                messages = await archive.update_channel(bot, channel)
                print("got %d message" % (len(messages)))
            except Exception as e:
                print (repr(e))

## Mimicry Comands
########################################################################


import markov, json
with open('corpus-133104714886807552.json') as fp:
    joe = json.load(fp)
joeChain = markov.build_chain(joe)

@bot.command(pass_context=True)
@asyncio.coroutine
async def speak(ctx):
    msg = markov.run_chain(joeChain)
    await ctx.bot.send_message(ctx.message.channel, msg)
    try:
        await bot.delete_message(ctx.message)
    except:
        pass

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
    
    
    


import config
print('Enter the url below into your browser to be prompted to add the bot to a server you have manage permissions on.')
print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(config.app_id))
bot.run(config.token)

    
