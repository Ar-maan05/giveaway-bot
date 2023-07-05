import discord
from discord.ext import commands
from discord import ApplicationContext
import datetime
from typing import Union
from main import default_colour

class ping_cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(description = "Shows the latency of the bot!")
    async def ping(
            self, 
            ctx: ApplicationContext
        ):
        embed = discord.Embed(
            description = f"\u200b\n> My latency is: **{round(self.bot.latency * 1000, 2)} ms!**\n\u200b", 
            timestamp = datetime.datetime.now(),
            color = default_colour
            )
        embed.set_author(
            name = "Latency!", 
            icon_url = ctx.me.display_avatar.url
            )
        await ctx.respond(embed = embed)

def setup(bot: Union[commands.Bot, discord.Bot]):
    bot.add_cog(ping_cog(bot))
        