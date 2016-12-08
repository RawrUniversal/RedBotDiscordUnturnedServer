import discord
import valve.source.a2s
from discord.ext import commands
SERVER_ADDRESS = ("167.114.156.67", "27037")


class MureUT:

    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mure(self):
        """This does stuff!"""
        server = valve.source.a2s.ServerQuerier(SERVER_ADDRESS)
        info = server.info()
        players = server.players()
        await self.bot.say("{player_count}/{max_players} "
                           "{server_name}".format(**info))
        for player in sorted(players["players"] key=lambda p["score"]):
                await self.bot.say("{score} {name}".format(**player))


def setup(bot):
    bot.add_cog(mure(bot))
