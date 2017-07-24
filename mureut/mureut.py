import discord
import urllib.request, simplejson
from discord.ext import commands

class MureUT:

    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def steamstatus(self):
        """Steam status command!"""
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
        link = "http://unturnedvegas.win/cost.php?id=" + itemid
        f = urllib.request.urlopen(link)
        await self.bot.say(f.read().decode('utf-8'))

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(administrator=True)
    async def logs(self, info, channel : discord.Channel):
        """Logs for channels!"""
        link = "http://unturnedvegas.win/logs.php?serverid=" + discord.Server.id + "&channelid=" + channel.id + "&info=" + info
        f = urllib.request.urlopen(link)
        await self.bot.say("```" + f.read().decode('utf-8') + "```")
                
                
def setup(bot):
    bot.add_cog(MureUT(bot))
