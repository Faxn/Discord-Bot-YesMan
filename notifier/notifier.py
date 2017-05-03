import asyncio

import discord
from discord.ext import commands

class Notifier:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    @asyncio.coroutine
    async def notify(self, ctx, delay:int):
        """Notifies the user with an @mention afer <delay> seconds."""
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


def setup(bot):
    bot.add_cog(Notifier(bot))

