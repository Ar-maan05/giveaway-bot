import discord
from discord.ext import commands
from discord import ApplicationContext, Option
from urllib.parse import quote_plus
from typing import Union


class Google(discord.ui.View):
    def __init__(self, query: str):
        super().__init__()
        query = quote_plus(query)
        url = f"https://www.google.com/search?q={query}"
        self.add_item(discord.ui.Button(label="Click Here", url=url))
        
        
class google_cog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
            
    @commands.slash_command(description = "Search for anything on google!")
    async def google(self, ctx: ApplicationContext, *, query: Option(str, "Arguement to search on google.")):
        await ctx.respond(f"Google Result for: `{query}`", view=Google(query))

def setup(bot: Union[discord.Bot, commands.Bot]):
    bot.add_cog(google_cog(bot))