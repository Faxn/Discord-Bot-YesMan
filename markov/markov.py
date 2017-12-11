import random
import json
import asyncio
import os
import re

import markovify
import discord
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
        self.chain_cls = markovify.NewlineText
        self._load_settings()
        self.topics = dict()
        self._load_topics()
    
    def _load_settings(self):
        s_file = self.path.join('settings.json')
        if os.path.exists(s_file):
            with open(s_file) as fp:
                self.settings = json.load(fp)
        else:
            self.settings = dict()
    
    def _load_topics(self):
        for f in os.scandir(self.path):
            if re.match('.*\.topic\.json$', f.name):
                name = re.search('(.*)\.topic\.json$', f.name).groups()[0]
                with open(f) as topic_file:
                    self.topics[name] = self.chain_cls.from_json(topic_file.read())
    
    @commands.command(pass_context=True)
    @asyncio.coroutine
    async def speak(self, ctx):
        if not self.joeify:
            with open('data/corpus-133104714886807552.json') as fp:
                joe = json.load(fp)
            joetext = '\n'.join(joe)
            self.joeify = markovify.NewlineText(joetext)
        msg = self.joeify.make_sentence()
        msg = msg.replace('@', '') # Hack to Remove @mentions. TODO make this smarter.
        await self.bot.say(msg)
        try:
            await bot.delete_message(ctx.message)
        except:
            pass
    
       
    @commands.group(pass_context = True)
    async def markov(self):
        # TODO stub
        hlp = self.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
    
    #@markov.command()
    @commands.command(pass_context = True)
    async def ingest_archive(self, ctx, topic : str, user: discord.Member):
        assert isinstance(user, discord.Member)
        archive = self.bot.cogs['Archiver'].archive
        lines = [x['content'] for x in archive.get_messages(user=user)]
        corpus = "\n".join(lines)
        new_chain = self.chain_cls(corpus, state_size=1)
        if topic in self.topics:
            old_chain = self.topics[topic]
            combined_chain = markovify.combine([new_chain, old_chain])
            self.topics[topic] = combined_chain
        else:
            self.topics[topic] = new_chain
        await self.bot.say("generated chain for user:%s." % user)
        path = os.path.join(self.path, topic+".topic.json")
        with open(path, 'w') as fp:
            fp.write(new_chain.to_json())
    
    #@markov.command()
    @commands.command()
    async def list_topics(self):
        sentence = "\n".join(self.topics)
        sentence = sentence.replace('@', '') # Hack to Remove @mentions. TODO make this smarter.
        await self.bot.say(sentence)
    
    #@markov.command()
    @commands.command()
    async def generate(self, topic : str):
        sentence = self.topics[topic].make_sentence()
        sentence = sentence.replace('@', '') # Hack to Remove @mentions. TODO make this smarter.
        await self.bot.say(sentence)
            
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
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()
    main()


