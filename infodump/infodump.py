import asyncio
import logging
import sys

from discord.ext import commands


class InfoDumper:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["show"], pass_context=True)
    async def info(self, ctx):
        """Show technical info"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("See `help %s` for usage info." % ctx.command)
            
    @info.command(name="ctx", pass_context=True)
    @asyncio.coroutine
    async def _show_ctx(self, ctx):
        await self.bot.say(dir(ctx))

    @info.command(name="channels", aliases=[], pass_context=True)
    @asyncio.coroutine
    async def _show_channels(self, ctx):
        """names, ids, and types of every channel the bot can see."""
        bot = ctx.bot

        channels = {}
        out = "`ID\t\t\tTYPE\tNAME\n"
        for channel in bot.get_all_channels():
            channels[channel.name] = channel
            out += "%s\t%s\t%s\n" % (channel.id, channel.type, channel.name)
        logger.info(out)
        await bot.send_message(ctx.message.channel, out+'`')

    @info.command(name="users", aliases=[], pass_context=True)
    @asyncio.coroutine
    async def _show_users(self, ctx):
        """Dumps the names and ids of every user on the current server."""
        out = "`ID\t\t\tNAME\n"
        members = self.bot.get_all_members()
        for member in members:
            out += "%s\t%s\n" % (member.id, member.name)
        await self.bot.say(out+'`')


def setup(bot):
    global logger
    try:
        logger = logging.getLogger(bot.logger.name+".infodump")
    except AttributeError:
        logger = logging.getLogger("infodump")
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.addHandler(stdout_handler)
    bot.add_cog(InfoDumper(bot))
