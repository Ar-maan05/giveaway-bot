import discord
from discord.ui import Modal, InputText
from discord import Interaction, ApplicationContext
from discord.ext import commands
from typing import Union

class bmimodal(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_item(InputText(label = "What is your bodyweight?", placeholder = "Enter your weight in Kilograms.", required = True, min_length = 1, max_length = 3))

        self.add_item(InputText(label = "What is your height?", placeholder = "Enter your height in centimetres.", required = True, min_length = 1, max_length = 3))

    async def callback(self, interaction: Interaction):
        weight = int(self.children[0].value)
        height = int(self.children[1].value)/100

        bmr = round(weight/(height * height), 1)

        await interaction.response.send_message("Your BMR is **{}**".format(bmr), ephemeral = True)

class bmi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name = "bmi", description = "Calculate your body mass index.")
    async def _bmi(self, ctx: ApplicationContext):
        await ctx.interaction.response.send_modal(bmimodal(title = "Calculate your body mass index."))

def setup(bot: Union[commands.Bot, discord.Bot]):
    bot.add_cog(bmi(bot))