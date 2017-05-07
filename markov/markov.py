import random
import json
import asyncio
import os

import markovify
from discord.ext import commands


def build_corpus(userid):
    corpus = []
    for fname in os.listdir("data/channels/"):
        with open("data/channels/"+fname) as fp:
           messages = json.load(fp)
        for m in messages:
            if (m["author"]["id"] == userid):
                corpus.append(m["content"])
           
    with open("corpus-%s.json"%(userid), 'w') as fp:
        json.dump( corpus, fp)

def build_generic_corpus():
    corpus = []
    for fname in os.listdir("data/channels/"):
        with open("data/channels/"+fname) as fp:
           messages = json.load(fp)
        for m in messages:
            corpus.append(m["content"])
           
    with open("corpus-generic.json", 'w') as fp:
        json.dump( corpus, fp)

class Markov:
    
    def __init__(self, bot):
        self.path = os.path.join("data", "markov")
        os.makedirs(self.path, exist_ok=True)
        self.bot = bot
        self.joeify = None
    
    @commands.command(pass_context=True)
    @asyncio.coroutine
    async def speak(self, ctx):
        if not self.joeify:
            with open('data/corpus-133104714886807552.json') as fp:
                joe = json.load(fp)
            joetext = '\n'.join(joe)
            self.joeify = markovify.NewlineText(joetext)
        msg = self.joeify.make_sentence()
        await self.bot.say(msg)
        try:
            await bot.delete_message(ctx.message)
        except:
            pass
            
    #@bot.listen('on_message')
    async def zon_message(self, message):
        if(message.author.id != bot.user.id):
            if(not '!' in message.content):
                await bot.send_message(message.channel, 'I agree')



def setup(bot):
    bot.add_cog(Markov(bot))
    
def main():
    joetext = '\n'.join(joe)
    joeify = markovify.Text(joetext)
    for i in range(10):
        print(joeify.make_sentence())
        print()

if __name__ == '__main__':
    main()


