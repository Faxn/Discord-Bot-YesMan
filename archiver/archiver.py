import asyncio
import os
import json

from discord.ext import commands
from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

#Syntatic sugar for tinydb queries.
Message = Query()


class Archiver:
    
    def __init__(self, bot):
        self.bot = bot
        self.path = os.path.join("data", "archiver")
        os.makedirs(self.path, exist_ok=True)
        self.dbpath = os.path.join(self.path, "messages.json")
        # TODO Migrate to a better database
        # * tinydb loads the whole db into memory. This doens't scale.
        # * No way to flush cache manualy or detect closing from SIGINT. 
        #     Can't use Caching safely.(Using it //anyway//.)
        # Consider:
        # * ZODB http://www.zodb.org/en/latest/
        # * CodernityDB http://labs.codernity.com/codernitydb/
        self.db = TinyDB(self.dbpath, storage=CachingMiddleware(JSONStorage))
        # self.db = TinyDB(self.dbpath)
        
    def get_storage(self, channel):
        """Returns the filename where the given channel should be stored."""
        outfile = os.path.join(self.path, "%s-%s.json" % (channel.id, channel.name ))
        return outfile

        
    def get_user_messages(self, userid):
        """Returns a generator that produces the content of all messages from the given user in the archive"""
        return ["NOt IMplemented"]
    
    
    async def get_all_messages(self, channel):
        messages = await self.get_messages(client, channel)
        
        last_snowflake = messages[-1]['id']
        while True:
            print("getting messages before %r" % (last_snowflake))
            new_messages = await get_messages(client, channel, last_snowflake)
            if len(new_messages) == 0:
                break
            messages.extend(new_messages)
            last_snowflake=new_messages[-1]['id']
        
        with open(get_storage(channel), 'w') as outfile:
            outfile.write(json.dumps(messages))
            
        return messages
    

    async def get_messages(self, channel, limit=100, before=None, after=None):
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
        """ Gets messages from the channel ignoring ones that are laready in db.
            Won't pay update database for deleded or changed messages."""
        print("updating %s" % (channel.name))
        present = self.db.search(Message.channel_id == channel.id)
        latest_id = 0
        for msg in present:
            latest_id = max(latest_id, int(msg['id']))
        print("\tlatest id: %d" % (latest_id))
        ## Get new messages.
        reached_current = False
        found_msg = True
        while (not reached_current) and found_msg:
            foud_msg = False
            message_itr = await self.get_messages(channel, after=latest_id)
            for msg in message_itr:
                if not self.db.contains(Message.id  == msg['id']):
                    found_msg = True
                    self.db.insert(msg)
                else:
                    reached_current = True
                latest_id = max(latest_id, int(msg['id']))
                print("\t%s\n\t\t%s" % (msg['id'], msg['content']))
      

    @commands.command(aliases=[], pass_context=True)
    @asyncio.coroutine
    async def slurp(self, ctx):
        """"Quick and dirty download of a channel's contents."""
        bot = ctx.bot
        channel = ctx.message.channel
        
        messages = await self.get_all_messages(bot, channel)
        await bot.send_message(channel, "got %d messages." % (len(messages)))
        
        return

    @commands.command(aliases=[], pass_context = True)
    @asyncio.coroutine
    async def archive(self, ctx, channel_p : str):
        bot = ctx.bot
        
        channel = bot.get_channel(channel_p)
        
        if channel == None:
            await bot.send_message(channel, "Can't find channel %s." % (channel_p))
            return
        
        await self._update_channel(channel)
        await bot.send_message(channel, "got %d messages." % (len(messages)))
        
        return

    @commands.command(pass_context = True)
    @asyncio.coroutine
    async def archive_all(self, ctx):
        bot = ctx.bot
        for channel in bot.get_all_channels():
            #print("%s:%s, %s" % ( channel.id, channel.name, channel.type))
            if channel.type is ChannelType.text:
                try:
                    messages = await self._update_channel(bot, channel)
                    print("got %d message" % (len(messages)))
                except Exception as e:
                    print (repr(e))
    
    def __unload(self):
        # TODO Get this to happen on close in red bot. 
        print("It's okay, the database was safely closed.")
        self.db.close()

def setup(bot):
    bot.add_cog(Archiver(bot))
