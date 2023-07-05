import discord
from discord import ApplicationContext, Option
from discord.ext import commands
import datetime
import wikipedia
from typing import Union
from main import default_colour, start_time
from discord.ui import Modal, InputText
from discord import Interaction
import time, datetime
import psutil, platform, cpuinfo

class other_bs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    class bmimodal(Modal):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.add_item(InputText(label = "What is your bodyweight?", placeholder = "Enter your weight in Kilograms.", required = True, min_length = 1, max_length = 3))

            self.add_item(InputText(label = "What is your height?", placeholder = "Enter your height in centimetres.", required = True, min_length = 1, max_length = 3))

        async def callback(self, interaction: Interaction):
            weight = int(self.children[0].value)
            height = int(self.children[1].value)/100

            bmr = round(weight/(height * height), 1)

            await interaction.response.send_message("Your BMI is **{}**".format(bmr), ephemeral = True)

    @commands.slash_command(description = "Search for the meaning of anything on Wikipedia!")
    async def define(self, 
                    ctx: ApplicationContext, 
                    args: Option(
                        str, 
                        "The term to search for on Wikipedia."
                    )
                ):
        await ctx.respond('Searching wikipedia...')
        async with ctx.typing():
            try:
                em = discord.Embed(title = "According to wikipedia...", description = f'```{wikipedia.summary(args, sentences = 2)}```', color = default_colour)
                em.set_footer(text = ctx.author, icon_url = ctx.author.avatar.url)
                em.timestamp = datetime.datetime.now()
                await ctx.send(content = None, embed = em)
            except:
                await ctx.edit(content = "No suitable definition found on Wikipedia.")

    @commands.slash_command(name = "bmi", description = "Calculate your body mass index.")
    async def _bmi(self, ctx: ApplicationContext):
        await ctx.interaction.response.send_modal(self.bmimodal(title = "Calculate your body mass index."))

    @commands.slash_command(description = "Sends the uptime of the bot.")
    async def uptime(self, ctx: ApplicationContext):
        with ctx.typing():
            current_time = time.time()
            difference = int(round(current_time - start_time))
            text = str(datetime.timedelta(seconds=difference))
            embed = discord.Embed(title = 'Current Uptime', description = f'\u200b\n> {text}', colour=default_colour)
            embed.add_field(name='\u200b', value=f'Latency: {round(self.bot.latency*1000, 2)}ms')
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar)
            await ctx.respond(embed=embed)

    @commands.slash_command(description = "Shows information about this bot.")
    async def info(self, ctx: ApplicationContext):
        #channel = ctx.channel
        await ctx.defer()
        em = discord.Embed(title=f"About this Bot.", description=f"This is a multi-purpose bot made using Py-Cord", color = default_colour)
        em.add_field(name="Name: ", value = self.bot.user.name)
        em.add_field(name="Id: ", value = self.bot.user.id)
        em.add_field(name="Nickname: ", value = "N/A" if ctx.me.display_name == self.bot.user.name else ctx.me.display_name)
        em.add_field(name="Running on Python Version: ", value=f"v{platform.python_version()}")
        em.add_field(name="Using Py-cord Version: ", value=f"v{discord.__version__}")
        em.add_field(name="Made by: ", value="`Low-Key.py#3418`")
        em.add_field(name="CPU info: ", value=cpuinfo.get_cpu_info()["brand_raw"])
        em.add_field(name="Running on: ", value=platform.platform())
        em.add_field(name="Current RAM Usage: ", value=f"{psutil.virtual_memory()[2]}%")
        em.add_field(name="Current CPU Usage: ", value=f"{psutil.cpu_percent(4)}%")
        em.add_field(name="Servercount: ", value=len(self.bot.guilds))
        em.add_field(name="Usercount: ", value=len(set(self.bot.get_all_members())))
        em.add_field(name="Commands Loaded: ", value=len([x.name for x in self.bot.application_commands if not isinstance(x, discord.SlashCommandGroup)]))
        em.add_field(name="Command Groups Loaded: ", value=len([x.name for x in self.bot.application_commands if isinstance(x, discord.SlashCommandGroup)]))
        em.set_footer(text = self.bot.user, icon_url = self.bot.user.avatar.url)
        em.set_thumbnail(url = self.bot.user.avatar.url)
        em.timestamp = datetime.datetime.now()
        await ctx.respond(embed = em, content = None)


def setup(bot: Union[discord.Bot, commands.Bot]):
    bot.add_cog(other_bs(bot))