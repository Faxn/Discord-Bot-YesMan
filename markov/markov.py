import random
import json
import asyncio
import os

import markovify
from discord.ext import commands

##EXAMPLE CHAIN
EXCHAIN = { "fish" : { 'food': 1, 'smell': 1}}

#flag for the end of the message.
TERMINAL = 345935

class markov:
    @staticmethod
    def build_chain(corpus : list):
        chain = {}
        for line in corpus:
            toks = line.split() + [TERMINAL]
            for i in range(len(toks)-1):
                #Make sure we have a dict for this key
                if(not toks[i] in chain):
                    chain[toks[i]] = {}
                trunk = chain[toks[i]]
                #increment if this is a repeat leaf
                if(toks[i+1] in trunk):
                    trunk[toks[i+1]]+=1
                #or add the leaf if it's novel
                else:
                    trunk[toks[i+1]] = 1
        return chain

    @staticmethod
    def clean_chain(chain):
        clean = []
        for k in chain:
            if(len(chain[k]) == 1):
                clean.append(k)
        for k in clean:
            del chain[k]

    @staticmethod
    def run_chain(chain, start=None):
        if(start is None):
            start = random.choice(list(chain.keys()))
        msg = [start]
        while True:
            trunk = chain[msg[-1]]
            keys = trunk.keys()
            nxtTokList = []
            for k in keys:
                nxtTokList += [k]*trunk[k]
            nxtTok = random.choice(nxtTokList)
            if(nxtTok == TERMINAL): break
            msg.append(nxtTok)
        return ' '.join(msg)



# COG

with open('data/corpus-133104714886807552.json') as fp:
    joe = json.load(fp)
joeChain = markov.build_chain(joe)


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
    
    @commands.command(pass_context=True)
    @asyncio.coroutine
    async def speak(self, ctx):
        msg = markov.run_chain(joeChain)
        await ctx.bot.send_message(ctx.message.channel, msg)
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
    pass

if __name__ == "__main__":
    main()


