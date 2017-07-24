import discord
import urllib.request, simplejson
from .utils import checks
from discord.ext import commands

class MureUT:

    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    def split(s, numsplits, default=None, sep=None, ignore_extra=False):
        parts = s.split(sep, numsplits)
        if len(parts) > numsplits:
             if ignore_extra:
                 del parts[numsplits:]
            else:
                 raise ValueError(‘too many values to split’)
            else:
                 parts.extend(default for i in xrange(numsplits – len(parts)))
            return parts
        
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
    async def logs(self, ctx, info):
        """Logs for channels!"""
        author = ctx.message.author
        server = author.server
        channel = ctx.message.channel
        link = "http://unturnedvegas.win/logs.php?serverid=" + str(server.id) + "&channelid=" + str(channel.id) + "&info=" + info
        f = urllib.request.urlopen(link)
        idk = f.read().decode('utf-8')
        for new in self.split(idk, 2000):
            await self.bot.say("```" + new + "```")
                
                
def setup(bot):
    bot.add_cog(MureUT(bot))
