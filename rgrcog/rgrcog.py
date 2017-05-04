import asyncio

from discord.ext import commands
import rgr

class RGR:
    
    def __init__(self, bot):
        self.bot = bot
    
    
    # Parse !rgr verbiage
    @commands.command(aliases=["r", "roll", "dice"], pass_context=True, rest_is_raw=True, description='Rolls dice. Uses an in development domain specific language.')
    @asyncio.coroutine
    async def rgr(self, ctx, *roll : str):    
        try:
            # discord.py parses arguments for us, we can't have that.
            expr = " ".join(roll)
            print(expr)
            response = rgr.roll(expr)
            await self.bot.say("{} rolls {}".format(ctx.message.author, response))
        except Exception as err:
            print(err)
            await self.bot.say("Could not complete {}'s roll:\n{}".format(ctx.message.author, err))


def setup(bot):
    bot.add_cog(RGR(bot))
