import discord
from discord.ext import commands
from discord import Webhook, ApplicationContext, Option, Interaction, ButtonStyle
import os
import aiohttp
from time_convert import time_convert
import time as time_module, datetime
import json
from discord.ui import View, Button
import asyncio
from main import timer_users

class timer_view(View):
    def __init__(self):
        super().__init__(timeout=None)

    '''@discord.ui.button(emoji = "⏲️", label="")
    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        with open('C:\\Users\\armaa\\Desktop\\vscode\\giveaway\\timer_users\\{}.json'.format(interaction.message.id), 'r+') as file:
            data = json.load(file)
            if interaction.user.id not in data['users']:
                data['users'].append(interaction.user.id)
                file.write(json.dumps(data))
                file.close()
                await interaction.response.send_message("You will be notified when the timer ends!", ephemeral = True)
            else:
                data['users'].remove(interaction.user.id)
                file.write(json.dumps(data))
                file.close()
                await interaction.response.send_message("You will no longer be notified when the timer ends!", ephemeral = True)'''

    @discord.ui.button(emoji = "⏲️")
    async def timer_callback(
            self, 
            button: Button, 
            interaction: Interaction
        ):
        os.chdir(timer_users)
        
        with open(f'{interaction.message.id}.json', 'r+') as conf:
            data = json.load(conf)

            
        if interaction.user.id in data['users']:
                
            
                    
            f = open(f'{interaction.message.id}.json', 'w')
                    
            f.write(json.dumps(data))
                    
            f.close()
                    
            await interaction.response.send_message('Your will no longer be notified when the timer ends!', ephemeral = True)
                
                
        else:
                
                data['users'].append(interaction.user.id)
                
                f = open(f'{interaction.message.id}.json', 'w')
                
                f.write(json.dumps(data))
                
                f.close()
                
                await interaction.response.send_message('You will be notified when the timer ends!', ephemeral = True)

class timer(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.slash_command(description = "Start a timer anywhere!")
    async def timer(self, ctx: ApplicationContext, time: Option(str, "The timer for the giveaway.", required = True), title: Option(str, "The title for the timer.", required = False)):

        if title is None:
            title = "Timer"

        t = time_convert(time)

        if(t<10):
            return await ctx.respond("Time must be at least 10 seconds!")

        final = int(time_module.time()) + t
        em=discord.Embed(description=f"Ending <t:{final}:R>", color=ctx.author.color, timestamp=datetime.datetime.now()+datetime.timedelta(seconds=t))
        em.set_author(name=title)
        em.set_footer(text="Ends at")

        m = await ctx.send(embed = em)


        abc_dict = {
            "u r": "gay",
            "users": []
        }

        f = open(f'{timer_users}\\{m.id}.json', 'w')
        f.write(json.dumps(abc_dict))
        f.close()

        await m.edit(view = timer_view())

        await ctx.respond("Successfully started the timer!", ephemeral = True)
        channel = ctx.channel

        await asyncio.sleep(t)

        with open(f'{timer_users}\\{m.id}.json', 'r') as conf:
            data = json.load(conf)

        users = ""

        for i in data['users']:
            users+=(f'<@{i}>')

        em = discord.Embed(title = "Timer Ended!", description = f"Ended: <t:{final}:R>")

        ended_view = View()
        ended_view.add_item(discord.ui.Button(emoji = "⏲️", disabled = True))

        await m.edit(embed = em, view = ended_view)
        await channel.send(users, delete_after = 1)

        os.remove(f'{timer_users}\\{m.id}.json')

def setup(bot):
    bot.add_cog(timer(bot))