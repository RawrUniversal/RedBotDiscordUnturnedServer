import discord
import array
import logging
import asyncio
import urllib.request, simplejson
from cogs.utils.dataIO import dataIO
from .utils import checks
from discord.ext import commands
from discord import Embed
import requests
import json
import time
import os
from datetime import datetime
from random import randint
import numpy
import wargaming
import valve.source.a2s
import valve.source

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
cooldown = {}

class MureUT:

    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot
        
    def chunks(s, n):
        for start in range(0, len(s), n):
            yield s[start:start+n]

    @commands.command()
    async def steamstatus(self):
        """Steam status command!"""
        await self.bot.say(embed=MureUT.embed_status(MureUT.create_new_status()))
            
    @commands.command()
    async def unturned(self, *, idorname):
        """Unturned items command!"""
        base_dir = os.path.join("data", "red")
        config_path = os.path.join(base_dir, "items.json")
        with open(config_path, encoding="utf-8") as item_ids:
            jdata = json.load(item_ids)
            item = MureUT.check_unturned(jdata, idorname)
            if item is False:
                await self.bot.say("That item doesn't exist!")
                return
            else:
                await self.bot.say(embed=MureUT.unturnedjson(item))

    @commands.command()
    async def wows(self, name):
        """World Of Warships stats command!"""
        base_dir = os.path.join("data", "wows")
        config_path = os.path.join(base_dir, "wows.json")
        wows = None
        key = None
        with open(config_path) as ids:
            jdata = json.load(ids)
            key = jdata['key']
            wows = wargaming.WoWS(jdata['key'], region='na', language='en')
        aid = wows.account.list(search=name, limit=1)[0]['account_id']
        pdata = wows.account.info(application_id=key,account_id=aid,language="en")
        em = Embed(color=0x00F4FF,
               title='WoWS Stats | {}'.format(
                   pdata[aid]['nickname']))
        em.add_field(name="{}'s stats for War of Warships".format(pdata[aid]['nickname']),
                     value="Leveling Points: **{}**\nLeveling Tier: **{}**\nBattle fought: **{}**\n"
                     "Distance travelled: **{} miles**\nWins: **{}**\nLosses: **{}**\nDraws: **{}**\n"
                     "Total Damage Dealt: **{}**\nMax Damage Dealt: **{}**"
                     .format(pdata[aid]['leveling_points'],pdata[aid]['leveling_tier'],
                     pdata[aid]['statistics']['battles'],pdata[aid]['statistics']['distance'],
                     pdata[aid]['statistics']['pvp']['wins'],pdata[aid]['statistics']['pvp']['losses'],
                     pdata[aid]['statistics']['pvp']['draws'], pdata[aid]['statistics']['pvp']['damage_dealt'],
                     pdata[aid]['statistics']['pvp']['max_damage_dealt']))
        em.set_footer(text="Stats last updated: {}".format(str(datetime.fromtimestamp(pdata[aid]['stats_updated_at']))))
        await self.bot.say(embed=em)


    @commands.command()
    async def osrs(self, *, itemid):
        """Search through the items for Old School Runescape!
        Uses OSBuddy for prices! You can use name or id.
        Example: !osbuddy yew logs"""
        item = MureUT.check_item(itemid, 2)
        if item is False:
            await self.bot.say("That item doesn't exist!")
            return
        data = MureUT.request_item_json_osbuddy(item)
        data2 = MureUT.request_item2_json(item)
        await self.bot.say(embed=MureUT.generate_embed_osbuddy(data, data2))


    @commands.command()
    async def rs3(self, *, itemid):
        """Search through the items for Runescape 3!
        Example: '!rs3 yew logs' You can use name or id."""
        item = MureUT.check_item(itemid, 3)
        if item is False:
            await self.bot.say("That item doesn't exist!")
            return
        data = MureUT.request_item_json(item)
        await self.bot.say(embed=MureUT.generate_embed(data))


    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(administrator=True)
    async def logs(self, ctx, channelname, *, info):
        """Logs for channels!
        example: !logs #general test"""
        author = ctx.message.author
        server = author.server
        channel = discord.utils.get(server.channels, mention=channelname)
        return await self.logs_menu(ctx, info, cid=channel.id)

    
    def check_name(value):
        item = str(value)
        item = item.lower()
        return item
    
    def check_string(item):
        item = item.lower()
        item = item.capitalize()
        return item

    def check_unturned(jdata, idorname):
        item = MureUT.check_name(idorname)
        for key, i in jdata.items():
            if idorname.isdigit():
                if key == idorname:
                    return i
            else:
                if isinstance(item, str):
                    if MureUT.check_name(i["Name"]) == item:
                        return i
                    elif item in MureUT.check_name(i["Name"]):
                        return i
                continue
        item = False
        return item
    
    
    def check_item(item, v):
        base_dir = os.path.join("data", "rs")
        config_path = os.path.join(base_dir, "items_rs.json")
        if v == 2:
            with urllib.request.urlopen("https://storage.googleapis.com/osbuddy-exchange/summary.json") as response:
                data = response.read()
                encoding = response.info().get_content_charset('utf-8')
                jdata = json.loads(data.decode(encoding))
                if item.isdigit():
                     for i in jdata:
                         if i == int(item):
                             return jdata[i]['id']
                else:
                    item = MureUT.check_string(item)
                    for i in jdata:
                        if item == jdata[i]['name']:
                            return jdata[i]['id']
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
    
    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel
        if channel.id != 576479100454305812 or channel.id != 623213672461893682:
            return
        if channel.id not in cooldown:
            cooldown[channel.id] = time.time()
            return
        if time.time() - cooldown[channel.id] < 30:
            return
        if message.author.id == self.bot.user.id:
            return
        if "server up" in message.content.lower() or "server down" in message.content.lower():
            try:
                querier = valve.source.BaseQuerier(('136.243.44.134', 27015))
                server = valve.source.a2s.ServerQuerier(querier)
                ping = server.ping()
                await self.bot.send_message(message.channel, 'The server is currently online. Join if you would like.')
                await self.bot.send_message(message.channel, 'Check #servers or #change log for more information.')
                cooldown[channel.id] = time.time()
            except:
                await self.bot.send_message(message.channel, 'The server is currently offline. Please wait for it to come back up.')
                await self.bot.send_message(message.channel, 'Check #servers or #change log for more information.')
                cooldown[channel.id] = time.time()
        

    def request_item_json_osbuddy(item):
        with urllib.request.urlopen("https://storage.googleapis.com/osbuddy-exchange/summary.json") as response:
            item_info = simplejson.load(response)
            return item_info[str(item)]

    def request_item2_json(item):
        with urllib.request.urlopen("http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={}".format(str(item))) as response:
            item_info = simplejson.load(response)
            return item_info

    def request_item_json(item):
        BASE_URL = "http://services.runescape.com/m=itemdb_rs"
        end_point = "/api/catalogue/detail.json?item={}".format(str(item))
        with urllib.request.urlopen(BASE_URL + end_point) as response:
            item_info = simplejson.load(response)
            return item_info

    def generate_embed_osbuddy(item_json, item_json2):
        print(item_json)
        em = Embed(color=0x00F4FF,
                   title='{} ({}) | {}'.format(
                       item_json["name"],
                       item_json["id"],
                       item_json2["item"]["description"]), timestamp=datetime.now())
        em.add_field(name="Current Price Guide: **{}**".format(item_json2['item']['current']['price']),
                     value="OSBuddy Buy Price: **{}**\nOSBuddy Sell Price: **{}**\nOSBuddy Buy Quantity: **{}**\nOSBuddy Sell Quantity: **{}**"
                           "\n\nToday's Change: **{}**\n30 Day: **{}**\n90 Day: **{}**\n180 Day: **{}**"
                           "\n\nMembers Only?  **{}**\n".format(item_json['buy_average'],item_json['sell_average'],
                        item_json['buy_quantity'],item_json['sell_quantity'], item_json2['item']['today']['price'],
                        item_json2['item']['day30']['change'], item_json2['item']['day90']['change'],
                        item_json2['item']['day180']['change'], item_json2['item']['members'].capitalize()))
        em.set_thumbnail(url=item_json2['item']['icon_large'])
        return em

    def getraritycolor(item):
        if item == "Uncommon":
            item = 0x1f8b4c
        elif item == "Rare":
            item = 0x206694
        elif item == "Epic":
            item = 0x71368a
        elif item == "Legendary":
            item = 0xc832fa
        elif item == "Mythical":
            item = 0xfa3219
        else:
            item = 0xffffff
        return item
    
    def nocost(item):
        if item == 0.0:
            item = "N/A"
        return item
    
    def nosize(item):
        if item == 0:
            item = "N/A"
        return item
    
    def unturnedjson(i):
        em = Embed(color=MureUT.getraritycolor(MureUT.check_string(i["Rarity"])),title='{} ({})'.format(i["Name"],i["Id"]), timestamp=datetime.now())
        em.add_field(name="Current Buy-Sell price: **{}-{}**".format(MureUT.nocost(i["Buy"]),MureUT.nocost(i["Sell"])),
                      value="Item Name: **{}**\nItem ID: **{}**\nRarity: **{}**\n".format(
                      i["Name"], i["Id"], MureUT.check_string(i["Rarity"])))
        if i['gInfo'] != None:
            em.add_field(name="Extra Info about the item: ", value="Firerate: **{}**\nCalibers: **{}**\nRange: **{}**\nHeadShot: **{}**\nBodyShot: **{}**"
                         .format(i['gInfo']['Firerate'],i['gInfo']['Calibers'],i['gInfo']['Range'],round(i['gInfo']['Head']),round(i['gInfo']['Body'])), inline=False)
        if i['cInfo'] != None:
            em.add_field(name="Extra Info about the item: ", value="Armor: **{}**\nExplosion Armor: **{}**\nTotal Space: **{}**".format(i['cInfo']['Armor'],
                          i['cInfo']['ExArmor'], int(i['cInfo']['Height']) * int(i['cInfo']['Width'])), inline=False)
        if i['fInfo'] != None:
            em.add_field(name="Extra Info about the item: ", value="Heath: **{}**\nFood: **{}**\nWater: **{}**\nVirus: **{}**\nEnergy: **{}**".format(i['fInfo']['Health'],
                          i['fInfo']['Food'], i['fInfo']['Water'], i['fInfo']['Virus'], i['fInfo']['Energy']), inline=False)
        if i['mInfo'] != None:
            em.add_field(name="Extra Info about the item: ", value="Calibers: **{}**\nCapacity: **{}**\nExplodes: **{}**"
                         .format(i['mInfo']['Calibers'], i['mInfo']['Capacity'], i['mInfo']['Explode']), inline=False)
        if i['bInfo'] != None:
            em.add_field(name="Extra Info about the item: ", value="Health: **{}**\nStorage Size: **{}**"
                         .format(i['bInfo']['Health'], MureUT.nosize(i['bInfo']['Size'])), inline=False)
        em.set_thumbnail(url="https://i.imgur.com/pVJXblM.png")
        return em
    
    def generate_embed2(item_json):
        print(item_json)
        em = Embed(color=0x00F4FF,
                   title='{} ({}) | {}'.format(
                       item_json["item"]["name"],
                       item_json["item"]["id"],
                       item_json["item"]["description"]), timestamp=datetime.now())
        em.add_field(name="Current Price Guide: **{}**".format(item_json['item']['current']['price']),
                     value="Today's Change: **{}**\n30 Day: **{}**\n90 Day: **{}**\n180 Day: **{}**"
                           "\n\nMembers Only?  **{}**\n".format(
                        item_json['item']['today']['price'], item_json['item']['day30']['change'],
                        item_json['item']['day90']['change'], item_json['item']['day180']['change'],
                        item_json['item']['members'].capitalize()))
        em.set_thumbnail(url=item_json['item']['icon_large'])
        return em

    def generate_embed(item_json):
        print(item_json)
        em = Embed(color=0x00F4FF,
                   title='{} ({}) | {}'.format(
                       item_json["item"]["name"],
                       item_json["item"]["id"],
                       item_json["item"]["description"]), timestamp=datetime.now())

        em.add_field(name="Current Price Guide: **{}**".format(item_json['item']['current']['price']),
                     value="Today's Change: **{}**\n30 Day: **{}**\n90 Day: **{}**\n180 Day: **{}**"
                           "\n\nMembers Only?  **{}**\n".format(
                        item_json['item']['today']['price'], item_json['item']['day30']['change'],
                        item_json['item']['day90']['change'], item_json['item']['day180']['change'],
                        item_json['item']['members'].capitalize()))

        em.set_thumbnail(url=item_json['item']['icon_large'])
        return em

    def embed_status(item_json):
        em = Embed(color=0x00F4FF,
                   title='Steam Status | {}'.format(
                       item_json['steam']['online']), timestamp=datetime.now())

        em.add_field(name="Current Steam Status: **Total Steam Players online: {}**".format(
                        item_json['steam']['online']),
                     value="Steam Store Status: **{}**\nSteam Community Status: : **{}**\nSteam WebAPI Status: **{}**"
                           "\nCSGO Matchmaking Scheduler Status:  **{}**\nCSGO Inventory Status: **{}**\n"
                           "CSGO Sessions Logon Status: **{}**\nCSGO Total Players: **{}**\n"
                           "For more info on Steam's Status: [https://steamstat.us/](https://steamstat.us/)".format(
                        item_json['steam']['services']['store'], item_json['steam']['services']['community'],
                        item_json['steam']['services']['webApi'], item_json['csgo']['services']['matchmakingScheduler'],
                        item_json['csgo']['services']['playerInventories'], item_json['csgo']['services']['sessionsLogon'],
                        item_json['csgo']['online']))

        em.set_thumbnail(url="https://steamstore-a.akamaihd.net/public/shared/images/responsive/share_steam_logo.png")

        return em

    def create_new_status():
        """Creates status.json from scratch."""
        API_KEY = 0
        ONLINE_USERS_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=1"
        STORE_URL = "https://store.steampowered.com/"
        COMMUNITY_URL = "https://steamcommunity.com/"
        WEB_API_URL = "https://api.steampowered.com/ISteamWebAPIUtil/GetServerInfo/v1/"
        base_dir = os.path.join("data", "red")
        config_path = os.path.join(base_dir, "apikey.json")
        with open(config_path) as ids:
            jdata = json.load(ids)
            API_KEY = jdata['key']
        csgo_json = MureUT.get_json("https://api.steampowered.com/ICSGOServers_730/GetGameServersStatus/v1/?key=" + API_KEY)["result"]

        status = {
            "steam": {
                "online": MureUT.get_json(ONLINE_USERS_URL)["response"]["player_count"],
                "services": {
                    "store": MureUT.get_status_code(STORE_URL),
                     "community": MureUT.get_status_code(COMMUNITY_URL),
                     "webApi": MureUT.get_status_code(WEB_API_URL)
                 }
             },
            "csgo": {
                "online": csgo_json["matchmaking"]["online_players"],
                "services": {
                    "sessionsLogon": csgo_json["services"]["SessionsLogon"],
                    "playerInventories": csgo_json["services"]["SteamCommunity"],
                    "matchmakingScheduler": csgo_json["matchmaking"]["scheduler"]
                },
                "servers": {
                }
            }
        }

        # Capitalize csgo services values
        status["csgo"]["services"] = {k: v.capitalize() for k, v in status["csgo"]["services"].items()}

        # Fill csgo servers load values, also capitalized
        status["csgo"]["servers"] = {k: v["load"].capitalize() for k, v in csgo_json["datacenters"].items()}
        return status
    

    def get_json(url):
        """Makes a request to a given URL and returns the response JSON data."""
        response = requests.get(url)
        return response.json()


    def get_status_code(url):
        """Makes a request to a given URL and returns the response status code."""
        try:
            response = requests.get(url, timeout=3)
        except requests.exceptions.RequestException as e:
            return "service unavailable"
        return response.reason
    
    
    async def logs_menu(self, ctx, info, cid=0,
                           message: discord.Message=None,
                           page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        author = ctx.message.author
        server = author.server
        channel = cid
        base = os.path.join("data", "gnu")
        server = os.path.join(base, str(server.id))
        if not os.path.exists(server):
            return await self.bot.say("You need to enable logging with '!clog on'!")
        file = os.path.join(server, str(channel))
        if cid == 0:
            return await self.bot.say("You need to enable logging with '!clog on'!")
        text_file = open(file, "r", encoding="utf8")
        lines = text_file.read().split('\n')
        log = ""
        for meh in lines:
            if info in meh:
                log += meh + "\n|"
        if log.count('\n') == 0:
            return await self.bot.say("Nothing found!")
        logs = list(MureUT.chunks(log.split('|'), 10))
        em = Embed(color=0x00F4FF,
                   title="Logs pages: {}/{} | Don't go too far foward or back!".format(page + 1, len(logs)), timestamp=datetime.now())
        try:
            log = '|'.join(str(e) for e in logs)
            em.add_field(name="Logs: ", value=''.join(logs[int(page)]))
        except IndexError:
            await self.bot.say("Nothing more found! | Don't go too far foward or back!")
            return await self.bot.delete_message(message)
        if not message:
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            try:
                message = await self.bot.edit_message(message, embed=em)
            except discord.HTTPException:
                return await self.logs_menu(ctx, info, cid=channel, message=message,
                    page=page, timeout=timeout)
        react = await self.bot.wait_for_reaction(
            message=message, user=ctx.message.author, timeout=timeout,
            emoji=["➡", "⬅", "❌"]
        )
        if react is None:
            await self.bot.remove_reaction(message, "⬅", self.bot.user)
            await self.bot.remove_reaction(message, "❌", self.bot.user)
            await self.bot.remove_reaction(message, "➡", self.bot.user)
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "next":
            next_page = 0
            if page == log.count('|'):
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            await self.bot.remove_reaction(message, "➡", ctx.message.author)
            return await self.logs_menu(ctx, info, cid=channel, message=message,
                                           page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = log.count('|')  # Loop around to the last item
            else:
                next_page = page - 1
            await self.bot.remove_reaction(message, "⬅", ctx.message.author)
            return await self.logs_menu(ctx, info, cid=channel, message=message,
                                           page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)



def setup(bot):
    global logger
    logger = logging.getLogger('bot')
    n = MureUT(bot)
    bot.add_listener(n.on_message, 'on_message')
    bot.add_cog(n)
