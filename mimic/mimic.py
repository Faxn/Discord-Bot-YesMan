import json
import asyncio

from discord.ext import commands

from . import markov

with open('data/corpus-133104714886807552.json') as fp:
    joe = json.load(fp)
joeChain = markov.build_chain(joe)


class Mimic:
    @commands.command(pass_context=True)
    @asyncio.coroutine
    async def speak(ctx):
        msg = markov.run_chain(joeChain)
        await ctx.bot.send_message(ctx.message.channel, msg)
        try:
            await bot.delete_message(ctx.message)
        except:
            pass
