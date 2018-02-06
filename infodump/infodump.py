import asyncio
import logging
import sys

import discord
import discord.client as client
from discord.ext import commands
from tabulate import tabulate


class InfoDumper:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["show"], pass_context=True)
    async def info(self, ctx):
        """Show technical info"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("See `help %s` for usage info." % ctx.command)
            
    @info.command(name="events", pass_context=True)
    @asyncio.coroutine
    async def _show_ctx(self, ctx):
        await self.bot.say(str(self.bot.extra_events.keys()))

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

    @info.command(name="cogs", aliases=[], pass_context=True)
    @asyncio.coroutine
    async def _show_cogs(self, ctx, query=None):
        """Shows info about the installed cogs."""
        for name in ctx.bot.cogs:
            ctx.bot.logger.info("examining "+name)
            cog = self.bot.cogs[name]
            table = list()
            for p in dir(cog):
                if p[0:2] == "__": continue
                table.append(p, type(cog.__getattribute__(p)), cog.__getattribute__(p))
            ctx.bot.logger.info("%s\n" % name  + tabulate(table))
            await self.bot.say("##%s\n" % name + tabulate(table))

    @info.command()
    async def user(self, user:discord.Member=None):
        await self.bot.say(user)
        await self.bot.say(json.dumps(user))
    
    async def on_command_error(self, exc, ctx):
        await self.bot.send_message(ctx.message.channel, str(exc))


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
    n = InfoDumper(bot)
    bot.add_cog(n)
