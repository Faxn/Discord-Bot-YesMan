import asyncio
import os
import json

from discord.ext import commands
from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

#Syntatic sugar for tinydb queries.
Message = Query()

db = TinyDB('data/messsages.db', storage=CachingMiddleware(JSONStorage))
        
    
async def update_channel(client, channel):
    print("updating %s" % (channel.name))
    ## if we have nothing on the channel get all the messages
    if db.get(Message.channel_id == channel.id) is None:
        messages = get_all_messages(client, self.channel)
        db.insert_multiple(messages);
        return 
    ## if we have some messages get the more recent ones.
    present = db.search(Message.channel_id == channel.id)
    latest_id = 0
    for msg in present:
        latest_id = max(latest_id, int(msg['id']))
    print("\tlatest id: %d" % (latest_id))
    ## Get new messages.
    message_itr = await get_messages(client, channel, after=latest_id)
    for msg in message_itr:
        #TODO add to archive iff not in archive
        #TODO request more as long as discord returns more.
        latest_id = max(latest_id, msg.id)
        print("\t%s\n\t\t%s" % (msg.id, msg.content))


async def get_messages(client, channel, limit=100, before=None, after=None):
    payload = {'limit':limit}
    if before:
        payload["before"] = before
    if after:
        payload['after'] = after
    
    url = '{0.CHANNELS}/{1}/messages'.format(client.http, channel.id)
    messages = await client.http.get( url, params=payload )
    return messages
    
async def get_all_messages(client, channel):
    messages = await get_messages(client, channel)
    
    last_snowflake = messages[-1]['id']
    while True:
        print("getting messages before %r" % (last_snowflake))
        new_messages = await get_messages(client, channel, last_snowflake)
        if len(new_messages) == 0:
            break
        messages.extend(new_messages)
        last_snowflake=new_messages[-1]['id']
    
    with open(get_storage(channel), 'w') as outfile:
        import json
        outfile.write(json.dumps(messages))
        
    return messages
        

def get_storage(channel):
    "Returns the filename where the given channel should be stored."
    os.makedirs("data/channels/", exist_ok=True)
    return "data/channels/%s-%s.json" % (channel.id, channel.name )
    


def build_corpus(userid):
    corpus = []
    for fname in os.listdir("data/channels/"):
        with open("data/channels/"+fname) as fp:
           messages = json.load(fp)
        for m in messages:
            if (m["author"]["id"] == userid):
                corpus.append(m["content"])
           
    with open("corpus-%s.json"%(userid), 'w') as fp:
        json.dump( corpus, fp)

def build_generic_corpus():
    corpus = []
    for fname in os.listdir("data/channels/"):
        with open("data/channels/"+fname) as fp:
           messages = json.load(fp)
        for m in messages:
            corpus.append(m["content"])
           
    with open("corpus-generic.json", 'w') as fp:
        json.dump( corpus, fp)


class Archiver:
    
    def __init__(self, bot):
        pass

    @commands.command(aliases=[], pass_context=True)
    @asyncio.coroutine
    async def slurp(ctx):
        bot = ctx.bot
        channel = ctx.message.channel
        
        messages = await util.get_all_messages(bot, channel)
        await bot.send_message(channel, "got %d messages." % (len(messages)))
        
        return

    @commands.command(aliases=[], pass_context = True)
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

    @commands.command(aliases=[], pass_context = True)
    @asyncio.coroutine
    async def show_users(ctx):
        bot = ctx.bot
        out = ""
        for member in ctx.message.server.members:
            out += "%s(%s)" % (member.name, member.id)
        await bot.send_message(channel, out)

    @commands.command(aliases=[], pass_context = True)
    @asyncio.coroutine
    async def show_all_users(ctx):
        bot = ctx.bot
        out = ""
        for member in bot.get_all_members():
            out += "%s(%s)" % (member.name, member.id)
        await bot.send_message(channel, out)


    @commands.command(aliases=[], pass_context = True)
    @asyncio.coroutine
    async def archive_3(ctx, channel_p : str):
        bot = ctx.bot
        
        channel = bot.get_channel(channel_p)
        
        messages = await util.get_all_messages(bot, channel)
        await bot.send_message(channel, "got %d messages." % (len(messages)))
        
        return

    @commands.command(pass_context = True)
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
