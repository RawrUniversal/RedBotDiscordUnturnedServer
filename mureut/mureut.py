import discord
import urllib.request, simplejson
from discord.ext import commands

class MureUT:

    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def steamstatus(self):
        """This does stuff!"""
        with urllib.request.urlopen("https://crowbar.steamstat.us/Barney") as url:
            data = simplejson.load(url)
            if data['success'] == true:
                await self.bot.say("Total Steam Players online: " + data['services']['online']['title'])
                await self.bot.say("Steam Store Status: " + data['services']['store']['title'])
                await self.bot.say("Steam Community Status: " + data['services']['community']['title'])
                await self.bot.say("Steam Database Status: " + data['services']['database']['title'])


def setup(bot):
    bot.add_cog(MureUT(bot))
