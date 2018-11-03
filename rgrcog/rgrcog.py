import asyncio
import json
import logging
import os

from discord.ext import commands
import rgr

logger = logging.getLogger(__name__)

class RGR:
        
    def __init__(self, bot):
        self.bot = bot
        self.path = os.path.join("data", "rgrcog")
        os.makedirs(self.path, exist_ok=True)
        self.config_path = os.path.join(self.path, "config.json")
        self._load_config()
        self._save_config()
        
    def _load_config(self):
        "Loads the config from the file to 'self.config' ."
        self.config = {'listen_channels':{}}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as config_fp:
                json_config = json.load(config_fp)
            # collections.ChainMap is the normal Way to do this, but json.dump can't handle it (python 3.6.3).
            self.config.update(json_config)
    
    def _save_config(self):
        "Write out 'self.config' to the config file."
        with open(self.config_path, 'w') as config_fp:
            json.dump(self.config, config_fp, indent=4)
    
    
    
    # Parse !rgr verbiage
    @commands.command(aliases=["r", "roll", "dice"], pass_context=True, rest_is_raw=True, description='Rolls dice. Uses an in development domain specific language.')
    @asyncio.coroutine
    async def rgr(self, ctx, *roll : str):
        try:
            # discord.py parses arguments for us, we can't have that.
            expr = " ".join(roll)
            logger.debug(expr)
            _, response, _ = rgr.roll(expr)
            await self.bot.say("{} rolls {}".format(ctx.message.author, response))
        except Exception as err:
            logger.warn(err)
            await self.bot.say("Could not complete {}'s roll:\n{}".format(ctx.message.author, err))
    
    @commands.command(aliases=["rollChannel", "autoRoll"], pass_context=True, rest_is_raw=True, description='Sets the current channel roll status')
    @asyncio.coroutine
    async def set_auto_roll(self, ctx, enabled: bool=True):    
        self.config['listen_channels'][ctx.message.channel.id] = enabled
        self._save_config()
    
    @asyncio.coroutine
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        if self.config['listen_channels'][message.channel.id]: 
            try:
                logger.debug("Rolling: %s", message.content)
                _, response, _ = rgr.roll(message.content)
                await self.bot.send_message(message.channel,  "{} rol {}".format(message.author, response))
            except Exception as e:
                logger.debug("Problem while rolling: %s",e)


def setup(bot):
    cog = RGR(bot)
    bot.add_cog(cog)
    #bot.add_listener(cog.on_message)
