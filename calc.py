import discord
from discord.ext import commands
from discord import ApplicationContext
from main import default_colour

class calc(commands.Cog):
  def __init__(self, bot):
    super().__init__()
    self.bot = bot

  @commands.slash_command(description = "Sends a calculator made with buttons!")
  async def calculate(self, ctx: ApplicationContext):
    class calculator(discord.ui.Button):
        def __init__(self, label, row, style = discord.ButtonStyle.secondary):
            super().__init__(label = label, style = style, row = row)
        
        async def callback(self, interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("You can't use that!", ephemeral = True)
                return
            try:
              if self.label != "AC" and int(eval(interaction.message.embeds[0].description))>99999999999999:
                await interaction.response.send_message("Don't try to break me", ephemeral=True)
                return
            except:
              pass
            try:
                if self.label == 'AC':
                    em = interaction.message.embeds[0]
                    em.description = '0'
                    await interaction.response.edit_message(embed = em)
                    
                elif self.label == '=':
                    em = interaction.message.embeds[0]
                    em.description = str(eval(em.description))
                    await interaction.response.edit_message(embed = em)
                    
                elif self.label == '⌫':
                    em = interaction.message.embeds[0]
                    m = em.description[::-1]
                    m = m[0]
                    em.description = str(int((int(em.description)-int(m))/10))
                    await interaction.response.edit_message(embed = em)
                    
                elif self.label == '%':
                    em = interaction.message.embeds[0]
                    em.description = str(int(eval(em.description))/100)
                    await interaction.response.edit_message(embed = em)
                    
                else:
                    em = interaction.message.embeds[0]
                    em.description = em.description + self.label if em.description not in ['0', '00'] else self.label
                    await interaction.response.edit_message(embed = em)
                    
            except:
                await interaction.response.send_message("That calulation doesn't even make sense. Don't try to break me!", ephemeral=True)
                
    embed = discord.Embed(title=f"{ctx.author.name}'s Calculator", description='0', color = default_colour)
    view = discord.ui.View()
    for i in range(10):
        row = i//3
        if i == 0:
            view.add_item(calculator('AC', 0, discord.ButtonStyle.danger))
        elif i==3:
            view.add_item(calculator('+', 1, discord.ButtonStyle.blurple))
        elif i==6:
            view.add_item(calculator('-', 2, discord.ButtonStyle.blurple))
        elif i==9:
            view.add_item(calculator('/', 3, discord.ButtonStyle.blurple))
        if i+1 != 10:
            view.add_item(calculator(str(i+1), row))
            if i==2:
                view.add_item(calculator('⌫', 0, discord.ButtonStyle.danger))
            elif i==5:
                view.add_item(calculator('*', 1, discord.ButtonStyle.blurple))
            elif i==8:
                view.add_item(calculator('%', 2, discord.ButtonStyle.blurple))
                
        else:
            view.add_item(calculator('00', 3))
            view.add_item(calculator('0', 3))
            view.add_item(calculator('.', 3))
            view.add_item(calculator('=', 3, discord.ButtonStyle.success))

    await ctx.respond(embed = embed, view = view)

def setup(bot):
  bot.add_cog(calc(bot))