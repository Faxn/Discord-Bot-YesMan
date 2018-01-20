import asyncio
import os
import json
import logging

import discord
from discord.ext import commands
from discord.enums import ChannelType
from discord.http import Route

#default logger in case we aren't in a bot, or the bot doesn't have a logger.
logger = logging.getLogger(__name__)

#tinydb archiver
try:
    from tinydb import TinyDB, Query, where
    from tinydb.storages import JSONStorage
    from tinydb.middlewares import CachingMiddleware
except ImportError as e:
    logger.info('Failed to import TinyDB', exc_info=True)
    TinyDB = False

#mongoDB Archiver
try:
    import motor.motor_asyncio
    Motor = True
except ImportError as e:
    logger.info('Failed to import motor for mongoDB', exc_info=True)
    Motor = False

# TODO Migrate to a better database
# * tinydb loads the whole db into memory. This doens't scale.
# * No way to flush cache manualy or detect closing from SIGINT. 
#     Can't use Caching safely.(Using it //anyway//.)
# Consider:
# * ZODB http://www.zodb.org/en/latest/
# * CodernityDB http://labs.codernity.com/codernitydb/

archive_backends = {}
DEFAULT_PATH = {}

class Archive:
    
    def get_all_messages(self):
        raise Exception("Not Implemented")
    
    def get_messages(self, user=None, channel=None):
        "Gets messages optionally restricted by user or channel."
        messages = iter(self.get_all_messages())
        while True:
            m = next(messages)
            if isinstance(user, discord.Member):
                if user.id != m['author']['id']:                
                    continue
            elif user and user != m['author']['id']:
                continue
            if channel and channel.id != m['channel_id']:
                continue
            logger.debug("logger found: %s\n", m)
            yield m
            
    def add_messages(self, messages, all_new=False):
        """ Adds <messages> to the databese. Returns nuber of messages added """
        #TODO: Remove
        raise Exception("Not Implemented")
    
    async def async_add_messages(self, messages, *args, **kwargs):
        return self.add_messages(*args, **kwargs)
    
    def flush(self):
        pass
   

if TinyDB:
    #Syntatic sugar for tinydb queries.
    Message = Query()

    class TinyDBArchive(Archive):
        
        def __init__(self, dbpath, loop=None):
            self.path = dbpath
            self.db = TinyDB(self.path, storage=CachingMiddleware(JSONStorage))
            
        def get_all_messages(self):
            return self.db.all()
        
        def zget_messages(self):
            # TODO remove or finish.
            return self.db.search(Message.author.id == member.id)
            msgs = self.db.search(Message.channel_id == channel.id)
            msgs.sort(key=lambda x: x['timestamp'])
            return msgs
            
        def add_messages(self, messages, all_new=False):
            """ Adds <messages> to the database. Returns number of messages added """
            added = 0
            for msg in messages:
                if all_new or not self.db.contains(Message.id  == msg['id']):
                    added += 1
                    self.db.insert(msg)
            return added
        
        async def async_add_messages(self, messages, all_new=False):
            added = 0
            for msg in messages:
                await asyncio.sleep(0)
                if all_new or not self.db.contains(Message.id  == msg['id']):
                    self.db.insert(msg)
                    added += 1
            return added
        
        def flush(self):
            flushed = False
            if '_storage' in dir(self.db) and 'flush' in dir(self.db._storage):
                self.db._storage.flush()

    archive_backends['TinyDB'] = TinyDBArchive
    DEFAULT_PATH['TinyDB'] = os.path.join("data", "archiver", "messages.json")

if Motor:
    class MongoMotorArchive(Archive):
        def __init__(self, dbpath, loop=None):
            client = motor.motor_asyncio.AsyncIOMotorClient(dbpath)
            self.db = client.get_database()
            self.loop = loop or asyncio.get_event_loop()
        async def async_add_messages(self, messages, all_new=False):
            #TODO: Batching Might be nice.
            added = 0
            for m in messages:
                m['_id'] = m['id']
                if all_new:
                    added += 1
                    await self.db.messages.insert_one(m)
                else:
                    t = await self.db.messages.find_one({ '_id':m['_id'] })
                    if not t:
                        added += 1
                        await self.db.messages.insert_one(m)
            return added
        def get_all_messages(self):
            cursor = self.db.messages.find()
            f = cursor.to_list(None)
            return self.loop.run_until_complete(f)
                    
    archive_backends['MongoDB'] = MongoMotorArchive
    DEFAULT_PATH['MongoDB'] = "mongodb://localhost/discordArchiver"
            


class Archiver:
    
    def __init__(self, bot):
        self.bot = bot
        self.path = os.path.join("data", "archiver")
        os.makedirs(self.path, exist_ok=True)
        self.dbpath = DEFAULT_PATH['TinyDB']
        self.archive = TinyDBArchive(self.dbpath, bot.loop)


    async def _fetch_messages(self, channel, limit=100, before=None, after=None):
        """Use the discord client to get some messages from the provided channel"""
        await asyncio.sleep(0)
        payload = {'limit':limit}
        url = "/channels/{0}/messages?limit="+str(limit)
        if before:
            payload["before"] = before
            url += "&before=" + str(before)
        if after:
            payload['after'] = after
            url += "&after=" + str(after)
        #url = '{0.CHANNELS}/{1}/messages'.format(self.bot.http, channel.id)
        r = Route('GET', url.format(channel.id))
        logger.debug("Fetching messages from '%s' with options: %s", channel.name, payload)
        #messages = await self.bot.http.get( url, params=payload )
        messages = await self.bot.http.request(r)
        return messages

    @commands.command(pass_context = True)
    @asyncio.coroutine
    async def test_fetch(self, ctx, channel: discord.Channel):
        #channel = self.bot.get_channel(channel_id)
        messages = await self._fetch_messages(channel, limit=11, after="281962999743250452")
        for m in messages:
            print(m['id'])
    
    
    async def _archive_channel(self, channel):
        """ Gets newest messages from the channel ignoring ones that are already in db.
            Won't update database for deleded or changed messages."""
        added = 0
        # Figure out if we have anything from the channel at all
        messages = iter(self.archive.get_messages(channel=channel))
        try:
            msg1 = next(messages)
        except StopIteration:
            # we had nothing on this channel
            messages = await self._fetch_messages(channel)
            if len(messages) > 0:
                added += self.archive.add_messages(messages, all_new=True)
                msg1 = messages[0]
            else:
                # empty channel. Nothing to do.
                return 0
        
        # Figure out the latest and oldest message we have from channel        
        oldest_id = int(msg1['id'])
        latest_id = oldest_id
        for msg in messages:
            await asyncio.sleep(0)
            oldest_id = min(latest_id, int(msg['id']))
            latest_id = max(latest_id, int(msg['id']))

        # Get new messages.
        while True:
            messages = await self._fetch_messages(channel, after=latest_id)
            if len(messages) == 0 :
                break
            # added += self.archive.add_messages(messages, all_new=True)
            added +=await  self.archive.async_add_messages(messages, all_new=True)
            for msg in messages:
                latest_id = max(latest_id, int(msg['id']))

        # Get old messages.
        while True:
            messages = await self._fetch_messages(channel, before=oldest_id)
            if len(messages) == 0 :
                break
            added += await self.archive.async_add_messages(messages, all_new=True)
            for msg in messages:
                oldest_id = min(oldest_id, int(msg['id']))
        # make sure the archive gets saved to disk.
        self.archive.flush()
        return added

    @commands.command(name="archive", pass_context = True)
    @asyncio.coroutine
    async def archive_command(self, ctx, channel_p : str):
        "Download messages from server to bot's database."
        bot = ctx.bot
        
        channel = bot.get_channel(channel_p)
        
        if channel == None:
            await bot.say("Can't find channel %s." % (channel_p))
            return
        
        await bot.say("Archiving Channel %s" % channel_p)
        added = await self._archive_channel(channel)
        await bot.say("got %d messages from #%s." % (added, channel.name))

    @commands.command(pass_context = True)
    @asyncio.coroutine
    async def archive_all(self, ctx):
        bot = ctx.bot
        for channel in bot.get_all_channels():
            #print("%s:%s, %s" % ( channel.id, channel.name, channel.type))
            if channel.type is ChannelType.text:
                try:
                    added = await self._archive_channel(channel)
                    await bot.say("got %d messages from %s#%s." % (added, channel.server.name, channel.name))
                except Exception as e:
                    await self.bot.say("Couldn't archive %s because: %s" % (channel.name, repr(e)))
        self.bot.say("Done archiving Everything.")




def setup(bot):
    try:
        logger = logging.getLogger(bot.logger.name+".archiver")
        logger.setLevel(logging.DEBUG)
    except AttributeError:
        #the default logger at the top of the file will be used.
        pass
    bot.add_cog(Archiver(bot))
