import discord
import urllib.request, simplejson
from cogs.utils.dataIO import dataIO
from .utils import checks
from discord.ext import commands
from discord import Embed
import requests
import json
import os
from datetime import datetime
from random import randint

class MureUT:

    """My custom cog that does stuff!"""

    base_dir = os.path.join("data", "rs")
    config_path = os.path.join(base_dir, "items_rs.json")
    
    def __init__(self, bot):
        self.bot = bot
        
    def chunks(s, n):
        for start in range(0, len(s), n):
            yield s[start:start+n]

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
                "For more info on Steam's Status: https://steamstat.us/```")

    @commands.command()
    async def rs(self, itemid):
        """Search through the items for Runescape!"""
        item = MureUT.check_item(itemid)
        if item is False:
            await self.bot.say("That item doesn't exist!")
            return

        data = MureUT.request_item_json(item)
        await self.bot.say(embed=MureUT.generate_embed(data))

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(administrator=True)
    async def logs(self, ctx, info):
        """Logs for channels!"""
        author = ctx.message.author
        server = author.server
        channel = ctx.message.channel
        link = "http://unturnedvegas.win/logs.php"
        data = {'serverid':server.id,
        'channelid':channel.id,
        'info':info}
        r = requests.post(url = link, data = data)
        idk = r.text
        for chunk in MureUT.chunks(idk, 1990):
            await self.bot.say("```" + chunk + "```")
                

    def check_string(item):
        item = item.lower()  # set all characters of item string to lowercase
        item = item.capitalize()  # capitalize the first letter of the string
        return item


    def check_item(message):
        base_dir = os.path.join("data", "rs")
        config_path = os.path.join(base_dir, "items_rs.json")
        item = message[1:]
        print(item)

        if item.capitalize() == 'Random':
            with open(config_path) as item_ids:
                jdata = json.load(item_ids)
                item = jdata[randint(0, len(jdata))]['id']
                return item

        if item.isdigit():
            with open(config_path) as item_ids:
                jdata = json.load(item_ids)

            for i in jdata:
                if i['id'] == int(item):
                    return item

        else:
            item = MureUT.check_string(item)
            with open(config_path) as item_ids:
                jdata = json.load(item_ids)

            for i in jdata:
                if item == i['name']:
                    return i['id']

        item = False
        return item


    def request_item_json(item):
        BASE_URL = "http://services.runescape.com/m=itemdb_rs"
        end_point = "/api/catalogue/detail.json?item={}".format(str(item))
        response = requests.get(BASE_URL + end_point)

        item_info = json.loads(response.content.decode("utf-8"))
        return item_info


    def generate_embed(item_json):
        print(item_json)
        em = Embed(color=0x00F4FF,
                   title='{} ({}) | {}'.format(
                       item_json["item"]["name"].title(),
                       item_json["item"]["id"],
                       item_json["item"]["description"].title()))

        em.add_field(name="Current Price Guide: **{}**".format(item_json['item']['current']['price']),
                     value="Today's Change: **{}**\n30 Day: **{}**\n90 Day: **{}**\n180 Day: **{}**"
                           "\n\nMembers Only?  **{}**\n".format(
                        item_json['item']['today']['price'], item_json['item']['day30']['change'],
                        item_json['item']['day90']['change'], item_json['item']['day180']['change'],
                        item_json['item']['members'].capitalize()))

        em.set_thumbnail(url=item_json['item']['icon_large'])

        em.set_footer(text=str(datetime.now()))

        return em



def setup(bot):
    bot.add_cog(MureUT(bot))
