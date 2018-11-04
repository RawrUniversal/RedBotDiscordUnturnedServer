import discord
import array
import dbl
import logging
import asyncio
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
import numpy
import wargaming


numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}


class MureUT:

    """My custom cog that does stuff!"""
    
    def __init__(self, bot):
        self.bot = bot
        base_dir = os.path.join("data", "red")
        config_path = os.path.join(base_dir, "key.json")
        key = None
        with open(config_path) as ids:
            jdata = json.load(ids)
            key = jdata['key']
        self.token = key  #  set this to your DBL token
        self.dblpy = dbl.Client(self.bot, self.token)
        self.bot.loop.create_task(self.update_stats())
        
    def chunks(s, n):
        for start in range(0, len(s), n):
            yield s[start:start+n]

    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""

        while True:
            logger.info('attempting to post server count')
            try:
                await self.dblpy.post_server_count()
                logger.info('posted server count ({})'.format(len(self.bot.guilds)))
            except Exception as e:
                logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
            await asyncio.sleep(1800)
           
    @commands.command()
    async def steamstatus(self):
        """Steam status command!"""
        with urllib.request.urlopen("https://crowbar.steamstat.us/Barney") as url:
            data = simplejson.load(url)
            if data['success']:
                await self.bot.say(embed=MureUT.embed_status(data))

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
        Example: '!osrs yew logs' You can use name or id."""
        item = MureUT.check_item(itemid, 2)
        if item is False:
            await self.bot.say("That item doesn't exist!")
            return
        data = MureUT.request_item2_json(item)
        await self.bot.say(embed=MureUT.generate_embed2(data))
        
        
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
                

    def check_string(item):
        item = item.lower()  # set all characters of item string to lowercase
        item = item.capitalize()  # capitalize the first letter of the string
        return item


    def check_item(item, v):
        base_dir = os.path.join("data", "rs")
        config_path = os.path.join(base_dir, "items_rs.json")
        path = os.path.join(base_dir, "items.json")
        if v == 2:
            with open(path, encoding = "ISO-8859-1") as itemids:
                jdata = json.load(itemids)
                if item.capitalize() == 'Random':
                    value = str(randint(0, len(jdata)))
                    if value not in jdata['id']:
                        item = False
                        return item
                    item = value['id']
                    if value['tradeable'] is false:
                        item = False
                        return item
                    return item
                if item.isdigit():
                     for i in jdata:
                         if i['id'] == int(item):
                             return item
                else:
                    item = MureUT.check_string(item)
                    for i in jdata:
                        if item == i['name']:
                            return i['id']
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

    def generate_embed2(item_json):
        print(item_json)
        em = Embed(color=0x00F4FF,
                   title='{} ({}) | {}'.format(
                       item_json["item"]["name"],
                       item_json["item"]["id"],
                       item_json["item"]["description"]))
        em.add_field(name="Current Price Guide: **{}**".format(item_json['item']['current']['price']),
                     value="Today's Change: **{}**\n30 Day: **{}**\n90 Day: **{}**\n180 Day: **{}**"
                           "\n\nMembers Only?  **{}**\n".format(
                        item_json['item']['today']['price'], item_json['item']['day30']['change'],
                        item_json['item']['day90']['change'], item_json['item']['day180']['change'],
                        item_json['item']['members'].capitalize()))
        em.set_thumbnail(url=item_json['item']['icon_large'])
        em.set_footer(text=str(datetime.now()))
        return em
    
    def generate_embed(item_json):
        print(item_json)
        em = Embed(color=0x00F4FF,
                   title='{} ({}) | {}'.format(
                       item_json["item"]["name"],
                       item_json["item"]["id"],
                       item_json["item"]["description"]))

        em.add_field(name="Current Price Guide: **{}**".format(item_json['item']['current']['price']),
                     value="Today's Change: **{}**\n30 Day: **{}**\n90 Day: **{}**\n180 Day: **{}**"
                           "\n\nMembers Only?  **{}**\n".format(
                        item_json['item']['today']['price'], item_json['item']['day30']['change'],
                        item_json['item']['day90']['change'], item_json['item']['day180']['change'],
                        item_json['item']['members'].capitalize()))

        em.set_thumbnail(url=item_json['item']['icon_large'])

        em.set_footer(text=str(datetime.now()))

        return em
    
    def embed_status(item_json):
        em = Embed(color=0x00F4FF,
                   title='Steam Status | {}'.format(
                       item_json['services']['cms']['title']))

        em.add_field(name="Current Steam Status: **Total Steam Players online: {}**".format(
                        item_json['services']['online']['title']),
                     value="Steam Store Status: **{}**\nSteam Community Status: : **{}**\nSteam WebAPI Status: **{}**"
                           "\nCSGO Status:  **{}**\nCSGO Inventory Status: **{}**\n"
                           "CSGO Sessions Logon Status: **{}**\n"
                           "For more info on Steam's Status: [https://steamstat.us/](https://steamstat.us/)".format(
                        item_json['services']['store']['title'], item_json['services']['community']['title'],
                        item_json['services']['webapi']['title'], item_json['services']['csgo']['title'],
                        item_json['services']['csgo_community']['title'], item_json['services']['csgo_sessions']['title']))

        em.set_thumbnail(url="https://steamstore-a.akamaihd.net/public/shared/images/responsive/share_steam_logo.png")

        em.set_footer(text=str(datetime.now()))

        return em
    
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
                   title="Logs pages: {}/{} | Don't go too far foward or back!".format(page + 1, len(logs)))
        try:
            em.add_field(name="Logs: ", value=''.join(logs[int(page)]))
        except IndexError:
            return await self.bot.say("Nothing more found! | Don't go too far foward or back!" )
        if not message:
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, embed=em)
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
            if page == log.count('|') - 1:
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            return await self.logs_menu(ctx, info, cid=channel, message=message,
                                           page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = log.count('|') - 1  # Loop around to the last item
            else:
                next_page = page - 1
            return await self.logs_menu(ctx, info, cid=channel, message=message,
                                           page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)



def setup(bot):
    global logger
    logger = logging.getLogger('bot')
    bot.add_cog(MureUT(bot))
