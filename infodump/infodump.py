import asyncio

import discord
from discord.ext import commands

class InfoDumper:

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases=[], pass_context = True)
    @asyncio.coroutine
    async def show_channels(self, ctx):
        """Dumps the names and snowflake ids of every channel the bot can see."""
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
    async def show_users(self, ctx):
        """Dumps the names and ids of every user on the current server."""
        bot = ctx.bot
        out = ""
        for member in ctx.message.server.members:
            out += "%s(%s)" % (member.name, member.id)
        await bot.send_message(channel, out)

    @commands.command(aliases=[], pass_context = True)
    @asyncio.coroutine
    async def show_all_users(self, ctx):
        """Dumps the name and ids of every user the bot can see."""
        bot = ctx.bot
        out = ""
        for member in bot.get_all_members():
            out += "%s(%s)" % (member.name, member.id)
        await bot.send_message(channel, out)



def setup(bot):
    bot.add_cog(InfoDumper(bot))

