import asyncio
import os
import json

from discord.ext import commands
from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

#Syntatic sugar for tinydb queries.
Message = Query()

# TODO Migrate to a better database
# * tinydb loads the whole db into memory. This doens't scale.
# * No way to flush cache manualy or detect closing from SIGINT. 
#     Can't use Caching safely.(Using it //anyway//.)
# Consider:
# * ZODB http://www.zodb.org/en/latest/
# * CodernityDB http://labs.codernity.com/codernitydb/



class Archive:
    def get_user_messages(self, userid):
        """Returns iterator over all the given user's messages in the archive."""
        return ["NOt IMplemented"]
    
    def get_channel_messages(self, channel):
        """Returns iterator over all the messages in the given channel, in order."""
        return []
        
    def add_messages(self, messages):
        """ Adds <messages> to the databese. Returns nuber of messages added """
        pass

class TinyDBArchive(Archive):
    
    def __init__(self, dbpath):
        # self.db = TinyDB(dbfile, storage=CachingMiddleware(JSONStorage))
        self.db = TinyDB(dbpath)
    
    def get_user_messages(self, userid):
        """ Generator that produces all messages from the given user in the archive"""
        return ["NOt IMplemented"]
    
    def get_channel_messages(self, channel):
        return self.db.search(Message.channel_id == channel.id)
        
    def add_messages(self, messages):
        """ Adds <messages> to the databese. Returns nuber of messages added """
        added = 0
        for msg in messages:
            if not self.db.contains(Message.id  == msg['id']):
                added += 1
                self.db.insert(msg)
        return added

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
        self.archive = TinyDBArchive(self.dbpath)
        
    async def _fetch_channel_messages(self, channel):
        """Gets all the messages from a channel in one big unsorted list."""
        messages = await self._fetch_messages(channel)

        last_snowflake = messages[-1]['id']
        while True:
            new_messages = await self._fetch_messages(channel, before=last_snowflake)
            if len(new_messages) == 0:
                break
            messages.extend(new_messages)
            last_snowflake=new_messages[-1]['id']

        return messages
    

    async def _fetch_messages(self, channel, limit=100, before=None, after=None):
        """Use the discord client to get some messages from the provided channel"""
        payload = {'limit':limit}
        if before:
            payload["before"] = before
        if after:
            payload['after'] = after
        
        url = '{0.CHANNELS}/{1}/messages'.format(self.bot.http, channel.id)
        messages = await self.bot.http.get( url, params=payload )
        return messages
    
    async def _update_channel(self, channel):
        """ Gets messages from the channel ignoring ones that are already in db.
            Won't update database for deleded or changed messages."""
        # Figure out the latest message we have from channel
        latest_id = 0
        for msg in self.archive.get_channel_messages(channel):
            latest_id = max(latest_id, int(msg['id']))
        # if we have nothing on the channel get all the messages
        # discord api doesn't give old messages with after=0 so we have to go backwards.
        if latest_id == 0:
            messages = await self._fetch_channel_messages(channel)
            added = self.archive.add_messages(messages)
            return added
        ## Get new messages.
        reached_current = False
        total_added = 0
        while (not reached_current):
            messages = await self._fetch_messages(channel, after=latest_id)
            if len(messages) == 0 :
                break
            added = self.archive.add_messages(messages)
            for msg in messages:
                latest_id = max(latest_id, int(msg['id']))
            reached_current = added < len(messages)
            total_added += added
        return total_added

    @commands.command(aliases=[], pass_context=True)
    @asyncio.coroutine
    async def slurp(self, ctx):
        """"Quick and dirty download of a channel's contents."""
        bot = ctx.bot
        channel = ctx.message.channel
        
        messages = await self._fetch_channel_messages(bot, channel)
        
        outpath = self.get_storage(channel)
        with open(outpath, 'w') as outfile:
            json.dump(messages, outfile)
        
        await bot.say("got %d messages from #%s." % (len(messages), channel.name))

    @commands.command(name="archive", pass_context = True)
    @asyncio.coroutine
    async def archive_command(self, ctx, channel_p : str):
        bot = ctx.bot
        
        channel = bot.get_channel(channel_p)
        
        if channel == None:
            await bot.send_message(channel, "Can't find channel %s." % (channel_p))
            return
        
        added = await self._update_channel(channel)
        await bot.say("got %d messages from #%s." % (added, channel.name))

    @commands.command(pass_context = True)
    @asyncio.coroutine
    async def archive_all(self, ctx):
        bot = ctx.bot
        for channel in bot.get_all_channels():
            #print("%s:%s, %s" % ( channel.id, channel.name, channel.type))
            if channel.type is ChannelType.text:
                try:
                    added = await self._update_channel(bot, channel)
                    await bot.say("got %d messages from #%s." % (added, channel.name))
                except Exception as e:
                    await self.bot.say("Couldn't archive %s because: %s" % (channel.name, repr(e)))

def setup(bot):
    bot.add_cog(Archiver(bot))
