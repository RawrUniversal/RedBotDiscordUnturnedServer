import discord
import urllib.request, simplejson
import urlopen
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
            if data['success']:
                await self.bot.say("```Total Steam Players online: " + data['services']['online']['title'] + "\n" +
                "Steam Store Status: " + data['services']['store']['title'] + "\n" +
                "Steam Community Status: " + data['services']['community']['title'] + "\n" + 
                "Steam WebAPI Status: " + data['services']['webapi']['title'] + "\n" + 
                "CSGO Status: " + data['services']['csgo']['title'] + "\n" + 
                "CSGO Inventory Status: " + data['services']['csgo_community']['title'] + "\n" + 
                "CSGO Sessions Logon Status: " + data['services']['csgo_sessions']['title'] + "\n" + 
                "For more info on Steam's Status: https://steamstat.us/\n" + "```")

    @commands.command()
    async def moddeditem(self, itemid):
        """Search through the items for OPKIT Modded TurnD server!"""
        link = "http://theemeraldage.net/cost.php?id=" + itemid
        f = urlopen(link)
        await self.bot.say("Item ID: " + itemid + " " + f.read())
                
                
def setup(bot):
    bot.add_cog(MureUT(bot))
