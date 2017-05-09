import asyncio
import os
import json
import logging

from discord.ext import commands
from discord.enums import ChannelType
from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

#Syntatic sugar for tinydb queries.
logger = None
Message = Query()

# TODO Migrate to a better database
# * tinydb loads the whole db into memory. This doens't scale.
# * No way to flush cache manualy or detect closing from SIGINT. 
#     Can't use Caching safely.(Using it //anyway//.)
# Consider:
# * ZODB http://www.zodb.org/en/latest/
# * CodernityDB http://labs.codernity.com/codernitydb/



class Archive:
    
    def get_all_messages(self):
        raise Exception("Not Implemented")
    
    def get_messages(self, user=None, channel=None):
        "Gets messages optionally restricted by user or channel."
        messages = iter(self.get_all_messages())
        while True:
            m = next(messages)
            if user and user.id != m['author']['id']:
                continue
            if channel and channel.id != m['channel_id']:
                continue
            yield m
            
    def add_messages(self, messages, all_new=False):
        """ Adds <messages> to the databese. Returns nuber of messages added """
        raise Exception("Not Implemented")
    
    async def async_add_messages(self, messages, *args, **kwargs):
        return self.add_messages(*args, **kwargs)
    
    def flush(self):
        pass

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
        futures = []        
        for msg in messages:
            await asyncio.sleep(0)
            self.db.insert(msg)
        return len(messages)
    
    def flush(self):
        flushed = False
        if '_storage' in dir(self.db) and 'flush' in dir(self.db._storage):
            self.db._storage.flush()
    

class Archiver:
    
    def get_storage(self, channel):
        """Returns the filename where the given channel should be stored."""
        outfile = os.path.join(self.path, "%s-%s.json" % (channel.id, channel.name ))
        return outfile
    
    def __init__(self, bot):
        self.bot = bot
        self.path = os.path.join("data", "archiver")
        os.makedirs(self.path, exist_ok=True)
        self.dbpath = os.path.join(self.path, "messages.json")
        self.archive = TinyDBArchive(self.dbpath, bot.loop)


    async def _fetch_messages(self, channel, limit=100, before=None, after=None):
        """Use the discord client to get some messages from the provided channel"""
        await asyncio.sleep(0)
        payload = {'limit':limit}
        if before:
            payload["before"] = before
        if after:
            payload['after'] = after
        
        url = '{0.CHANNELS}/{1}/messages'.format(self.bot.http, channel.id)
        logger.debug("Fetching messages from '%s' with options: %s", channel.name, payload)
        messages = await self.bot.http.get( url, params=payload )
        return messages


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
    global logger
    try:
        logger = logging.getLogger(bot.logger.name+".archiver")
    except AttributeError:
        logger = logging.getLogger("archiver")
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.addHandler(stdout_handler)
    bot.add_cog(Archiver(bot))
