import asyncio
import datetime
import json
import os
import random
import discord
from discord.ext import commands, tasks
from discord import ApplicationContext, ButtonStyle, CategoryChannel, Embed, Interaction, InteractionMessage, VoiceChannel
from discord.commands import Option, SlashCommandGroup
from check_int import check_int
from time_convert import time_convert
import time as time_module
from typing import Union
from discord.ui import View, Button, Select
from discord.commands import permissions
from finduser import finduser
from findrole import findrole
import shutil
from main import timer_users, server_configs, giveaway_configs, ended_giveaways

default_colour = 0x87CEEB

default_dict = {
    "giveaway_role": "none",
    "giveaway_manager": "none",
    "default_msg": "none",
    "gaw_embed": {
                "title": "none",
                "description": "none"
                }
}
default = json.dumps(default_dict)





def perm_check(ctx: ApplicationContext):
    
    os.chdir(server_configs)
    
    if not os.path.exists(f'{ctx.guild.id}.json'):
    
        f = open(f'{ctx.guild.id}.json', 'w+')
        
        f.write(default)
            
        f.close()
    
    with open(f'{ctx.guild.id}.json', 'r') as conf:
        
        try:
        
            data = json.load(conf)
            
        except:
            
            f = open(f'{ctx.guild.id}.json', 'w')
            
            f.write(default)
            
            f.close()
            
            data = json.load(conf)
        
        if 'giveaway_manager' not in data or data['giveaway_manager'] == "none":
            return ctx.author.guild_permissions.manage_guild
        
        else:
            return ctx.author.guild_permissions.manage_guild or (ctx.guild.get_role(data['giveaway_manager']) in ctx.author.roles)
        
        
    
        

class end_button(View):
    def __init__(
        self, 
        timeout: Union[int, float], 
        winners: int, 
        prize: str, 
        bot: Union[commands.Bot, discord.Bot], 
        ctx: ApplicationContext
    ):
        super().__init__(timeout=timeout)
        self.winners = winners
        self.prize = prize
        self.bot = bot
        self.ctx = ctx
        
    @discord.ui.button(emoji = "🎊")
    async def join_callback(
            self, 
            button: Button, 
            interaction: Interaction
        ):
        os.chdir(giveaway_configs)
        
        with open(f'{interaction.message.id}.json', 'r+') as conf:
            data = json.load(conf)
            
        og_interaction: Interaction = interaction
            
        if interaction.user.id in data['entries']:
                
                leave_view = View(timeout = 300)
                
                leave_button = Button(label = 'Leave', style = ButtonStyle.red)
                
                async def leave_callback(interaction: Interaction):
                    data['entries'].remove(interaction.user.id)
                    
                    f = open(f'{og_interaction.message.id}.json', 'w')
                    
                    f.write(json.dumps(data))
                    
                    f.close()
                    
                    await interaction.response.send_message('Your entry has been marked as invalid.', ephemeral = True)
                    
                cancel_button = Button(label = 'Cancel')
                
                async def cancel_callback(interaction: Interaction):
                    await interaction.response.edit_message(content = 'Okay, I cancelled this interaction.', view = None, embed = None)
                    
                leave_button.callback = leave_callback
                
                cancel_button.callback = cancel_callback
                
                leave_view.add_item(leave_button) 
                leave_view.add_item(cancel_button)
                
                embed = Embed(title = 'You already joined this giveaway', description = "Click the 'Leave' button below to remove your entry in this giveaway.")
                
                embed.color = interaction.message.embeds[0].color
                
                embed.timestamp = datetime.datetime.now()
                
                await interaction.response.send_message(embeds = [embed], view = leave_view, ephemeral = True)
                
                
        else:
                
                data['entries'].append(interaction.user.id)
                
                f = open(f'{interaction.message.id}.json', 'w')
                
                f.write(json.dumps(data))
                
                f.close()
                
                await interaction.response.send_message('You successfully joined the giveaway!', ephemeral = True)
        
    @discord.ui.button(label = "End")
    async def callback(
            self, 
            button: Button, 
            interaction: Interaction
        ):
        
        os.chdir(server_configs)
        
        with open(f'{interaction.guild.id}.json', 'r') as conf:
            data = json.load(conf)
            
        r = interaction.guild.get_role(data['giveaway_manager']) if data['giveaway_manager'] != "none" else "none"
        
        if r != "none":
            if not interaction.user.guild_permissions.manage_guild:
                return await interaction.response.send_message('You do not have the required permission to perform this action', ephemeral = True)

        else:
            if not interaction.user.guild_permissions.manage_guild or r not in interaction.user.roles:
                return await interaction.response.send_message('You do not have the required permission to perform this action', ephemeral = True)
            
        await interaction.response.defer(ephemeral = True, invisible = False)
        
        
        os.chdir(giveaway_configs)
        
        jump_to_giveaway_view = View()
        jump_to_giveaway_view.add_item(Button(label = "Jump to giveaway", url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.message.id}"))
        
        gaw_message: InteractionMessage = await interaction.channel.fetch_message(interaction.message.id)
        
        f = open(f'{gaw_message.id}.json', 'r')
        
        data = json.load(f)
        
        f.close()
        
        users = [await self.bot.fetch_user(x) for x in data['entries']]

        
        if len(users) == 0:
            if os.path.exists(f'{gaw_message.id}.json'): 
                shutil.move(
                        f'{giveaway_configs}/{gaw_message.id}.json', 
                        f'{ended_giveaways}/{gaw_message.id}.json'
                    )
                try:
                    os.remove(f'{gaw_message.id}.json')
                except:
                    pass

            return await interaction.followup.send('There were no valid entries for this giveaway', view = jump_to_giveaway_view)
        
        if self.winners == 1:
            winner = random.choice(users)
            
            em = discord.Embed(
                    title = "You won a giveaway!", 
                    description = "Please wait patiently to receive your prize!", 
                    color = default_colour
                )
            
            em.set_footer(
                    text = f'{interaction.guild.name} Giveaway ended', 
                    icon_url = interaction.guild.icon.url
                )
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await winner.send(
                        embed = em, 
                        view = jump_to_giveaway_view
                    )
            
            except:
                pass
            
            em = discord.Embed(
                    title = 'Your giveaway ended!', 
                    description = f'The winners are **{winner}**', 
                    color = 0xe67e22
                )
            
            em.set_footer(
                    text = f'{interaction.guild.name} Giveaway ended', 
                    icon_url = interaction.guild.icon.url
                )
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await self.ctx.author.send(
                        embed = em, 
                        view = jump_to_giveaway_view
                    )
                
            except:
                pass
            
            await interaction.channel.send(
                    f"Congratulations {winner.mention}! You won the giveaway for **{self.prize}**!", 
                    view = jump_to_giveaway_view
                )
            
            gaw_embed = discord.Embed(
                    title = "Giveaway ended!", 
                    description = f"**Winners:** {winner.mention}", 
                    timestamp = datetime.datetime.now()
                )
            
            gaw_embed.set_footer(
                    text = f"Winners: {self.winners} | Ended at"
                )
            
            try:
            
                await interaction.message.edit(
                    embed = gaw_embed, view = reroll_button(
                        None, 
                        self.winners, 
                        self.prize, 
                        self.bot, 
                        self.ctx
                    )
                )
                
            except:
                
                await gaw_message.edit(
                        embed = gaw_embed, 
                        view = reroll_button(
                            None, 
                            self.winners, 
                            self.prize, 
                            self.bot, 
                            self.ctx
                        )
                    )
            
        elif self.winners == 2:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}**', color = 0xe67e22)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await self.ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await interaction.channel.send(f"Congratulations {w1.mention} {w2.mention}! You won the giveaway for **{self.prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {self.winners} | Ended at")
            
            try:
            
                await interaction.response.edit_message(embed = gaw_embed, view = reroll_button(None, self.winners, self.prize, self.bot, self.ctx))
                
            except:
                
                await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, self.winners, self.prize, self.bot, self.ctx))
            
        else:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            users.remove(w2)
            
            w3 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            try:
                await w3.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}, {w3}**', color = 0xe67e22)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await self.ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await interaction.channel.send(f"Congratulations {w1.mention} {w2.mention} {w3.mention}! You won the giveaway for **{self.prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}, {w3.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {self.winners} | Ended at")
            
            try:
            
                await interaction.response.edit_message(embed = gaw_embed, view = reroll_button(None, self.winners, self.prize, self.bot, self.ctx))
                
            except:
                
                await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, self.winners, self.prize, self.bot, self.ctx))

        await interaction.followup.send("The giveaway was ended!", ephemeral = True)
        
        if os.path.exists(f'{gaw_message.id}.json'): 
            #os.remove(f'{gaw_message.id}.json')
            shutil.move(f'{giveaway_configs}/{gaw_message.id}.json', f'{ended_giveaways}/{gaw_message.id}.json')
            try:
                os.remove(f'{gaw_message.id}.json')
            except:
                pass
                
                
        
            
class reroll_button(View):
    def __init__(self, timeout, winners, prize, bot, ctx):
        super().__init__(timeout=timeout)
        self.winners = winners
        self.prize = prize
        self.bot = bot
        self.ctx = ctx
        
    @discord.ui.button(label = "Reroll", custom_id = "reroll")
    async def callback(self, button: Button, interaction: Interaction):

        await interaction.response.defer(ephemeral = True, invisible = False)
        
        os.chdir(server_configs)
        
        with open(f'{interaction.guild.id}.json', 'r') as conf:
            data = json.load(conf)
            
        r = interaction.guild.get_role(data['giveaway_manager']) if data['giveaway_manager'] != "none" else "none"
        
        if r != "none":
            if not interaction.user.guild_permissions.manage_guild:
                return await interaction.response.send_message('You do not have the required permission to perform this action', ephemeral = True)

        else:
            if not interaction.user.guild_permissions.manage_guild or r not in interaction.user.roles:
                return await interaction.response.send_message('You do not have the required permission to perform this action', ephemeral = True)
        
        os.chdir(ended_giveaways)
        
        jump_to_giveaway_view = View()
        jump_to_giveaway_view.add_item(Button(label = "Jump to giveaway", url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.message.id}"))
        
        gaw_message: discord.Message = await interaction.channel.fetch_message(interaction.message.id)
        
        f = open(f'{gaw_message.id}.json', 'r')
        
        data = json.load(f)
        
        f.close()
        
        users = [await self.bot.fetch_user(x) for x in data['entries']]
        
        if self.winners == 1:
            winner = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await winner.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway was rerolled!', description = f'The winners are **{winner}**', color = 0xe67e22)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await self.ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await interaction.channel.send(f"Congratulations {winner.mention}! You won the reroll for **{self.prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {winner.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {self.winners} | Ended at")
            
            await interaction.message.edit(embed = gaw_embed)
            
        elif self.winners == 2:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway was rerolled!', description = f'The winners are **{w1}, {w2}**', color = 0xe67e22)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await self.ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await interaction.channel.send(f"Congratulations {w1.mention} {w2.mention}! You won the reroll for **{self.prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {self.winners} | Ended at")
            
            await interaction.message.edit(embed = gaw_embed)
            
        else:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            users.remove(w2)
            
            w3 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            try:
                await w3.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway was rerolled!', description = f'The winners are **{w1}, {w2}, {w3}**', color = 0xe67e22)
            
            em.set_footer(text = f'{interaction.guild.name} Giveaway ended', icon_url = interaction.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await self.ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await interaction.channel.send(f"Congratulations {w1.mention} {w2.mention} {w3.mention}! You won the reroll for **{self.prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}, {w3.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {self.winners} | Ended at")
            
            await interaction.message.edit(embed = gaw_embed)

        await interaction.followup.send("The giveaway was rerolled!", ephemeral = True)
            

async def check_gaws(self):
    
    try:
    
        os.chdir(giveaway_configs)
        
        for file in os.listdir(os.getcwd()):
            c = 0
            if file.endswith('.json'):
                with open(file, 'r') as conf:
                    data = json.load(conf)
                    if data['time'] > round(time_module.time()):continue
                    
                    msg, temp = file.split('.')
                    for guild in self.bot.guilds:
                        
                        if c>0: break
                        
                        c = 0
                        
                        for category in guild.channels:
                            
                            if c>0: break
                            
                            c = 0
                            
                            if isinstance(category, discord.VoiceChannel):continue
                            #c = category.channels if isinstance(category, discord.CategoryChannel) else category
                            if isinstance(category, discord.TextChannel):
                                
                                channel = category
                                print(channel)
                                
                                try:
                                    gaw_message = await channel.fetch_message(int(msg))
                                except Exception as e:
                                    print(e)
                                    continue
                                
                                c+=1
                                    
                                embed = gaw_message.embeds[0]
                                temp, author = embed.description.split(' by: ')
                                author = author.replace('<', '')
                                author = author.replace('@', '')
                                author = author.replace('!', '')
                                author = author.replace('>', '')
                                author = author.strip()
                                print(author)
                                author = await self.bot.fetch_user(int(author))
                                print(author)
                                winners, temp = embed.footer.text.split(' winners')
                                winners = int(winners)
                                prize = embed.title

                                
                                async for m in channel.history(limit = None):
                                    if m.author is None: continue
                                    if m.author.id == author.id:
                                        ctx = await self.bot.get_context(m)
                                        break
                                
                                f = open(f'{gaw_message.id}.json', 'r')
        
                                data = json.load(f)
                                
                                f.close()
                                
                                jump_to_giveaway_view = View()
                                
                                jump_to_giveaway_view.add_item(Button(label = "Jump to giveaway", url = f"https://discord.com/channels/{guild.id}/{channel.id}/{gaw_message.id}"))
                                
                                if len(data['entries']) == 0:
                                    await gaw_message.reply('There were no valid entries for this giveaway.', view = jump_to_giveaway_view)
                                    break
                                
                                users = [await self.bot.fetch_user(x) for x in data['entries']]
                                
                                if winners == 1:
                                    winner = random.choice(users)
                                
                                    em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
                                    
                                    em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                    
                                    em.timestamp = datetime.datetime.now()
                                    
                                    try:
                                        await winner.send(embed = em, view = jump_to_giveaway_view)
                                    
                                    except:
                                        pass
                                    
                                    em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{winner}**', color = 0xe67e22)
                                    
                                    em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                    
                                    em.timestamp = datetime.datetime.now()
                                    
                                    try:
                                        await author.send(embed = em, view = jump_to_giveaway_view)
                                        
                                    except:
                                        pass
                                    
                                    await channel.send(f"Congratulations {winner.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
                                    
                                    gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {winner.mention}", timestamp = datetime.datetime.now())
                                    
                                    gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
                                    
                                    
                                    
                                    await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
                                    
                                elif winners == 2:
                                    w1 = random.choice(users)
                                    users.remove(w1)
                                    
                                    w2 = random.choice(users)
                                    
                                    em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
                                    
                                    em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                    
                                    em.timestamp = datetime.datetime.now()
                                    
                                    try:
                                        await w1.send(embed = em, view = jump_to_giveaway_view)
                                    
                                    except:
                                        pass
                                    
                                    try:
                                        await w2.send(embed = em, view = jump_to_giveaway_view)
                                        
                                    except:
                                        pass
                                    
                                    em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}**', color = 0xe67e22)
                                    
                                    em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                    
                                    em.timestamp = datetime.datetime.now()
                                    
                                    try:
                                        await author.send(embed = em, view = jump_to_giveaway_view)
                                        
                                    except:
                                        pass
                                    
                                    await channel.send(f"Congratulations {w1.mention} {w2.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
                                    
                                    gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}", timestamp = datetime.datetime.now())
                                    
                                    gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
                                    
                                    await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
                                    
                                else:
                                    w1 = random.choice(users)
                                    users.remove(w1)
                                    
                                    w2 = random.choice(users)
                                    users.remove(w2)
                                    
                                    w3 = random.choice(users)
                                    
                                    em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
                                    
                                    em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                    
                                    em.timestamp = datetime.datetime.now()
                                    
                                    try:
                                        await w1.send(embed = em, view = jump_to_giveaway_view)
                                    
                                    except:
                                        pass
                                    
                                    try:
                                        await w2.send(embed = em, view = jump_to_giveaway_view)
                                        
                                    except:
                                        pass
                                    
                                    try:
                                        await w3.send(embed = em, view = jump_to_giveaway_view)
                                        
                                    except:
                                        pass
                                    
                                    em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}, {w3}**', color = 0xe67e22)
                                    
                                    em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                    
                                    em.timestamp = datetime.datetime.now()
                                    
                                    try:
                                        await author.send(embed = em, view = jump_to_giveaway_view)
                                        
                                    except:
                                        pass
                                    
                                    await channel.send(f"Congratulations {w1.mention} {w2.mention} {w3.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
                                    
                                    gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}, {w3.mention}", timestamp = datetime.datetime.now())
                                    
                                    gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
                                    
                                    await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
                                    
                                    continue
                            else:
                                for channel in category.channels:
                                    
                                    if isinstance(channel, VoiceChannel): continue
                                
                                    try:
                                        gaw_message = await channel.fetch_message(int(msg))
                                    except Exception as e:
                                        print(e)
                                        continue
                                    
                                    c+=1
                                    
                                    embed = gaw_message.embeds[0]
                                    temp, author = embed.description.split(' by: ')
                                    author = author.replace('<', '')
                                    author = author.replace('@', '')
                                    author = author.replace('!', '')
                                    author = author.replace('>', '')
                                    author = author.strip()
                                    print(author)
                                    author = await self.bot.fetch_user(int(author))
                                    print(author)
                                    winners, temp = embed.footer.text.split(' winners')
                                    winners = int(winners)
                                    prize = embed.title

                                    
                                    async for m in channel.history(limit = 500):
                                        if m.author is None: continue
                                        if m.author.id == author.id:
                                            ctx = await self.bot.get_context(m)
                                            break
                                    
                                    f = open(f'{gaw_message.id}.json', 'r')
        
                                    data = json.load(f)
                                    
                                    f.close()
                                    
                                    jump_to_giveaway_view = View()
                                
                                    jump_to_giveaway_view.add_item(Button(label = "Jump to giveaway", url = f"https://discord.com/channels/{guild.id}/{channel.id}/{gaw_message.id}"))
                                    
                                    if len(data['entries']) == 0:
                                        await gaw_message.reply('There were no valid entries for this giveaway.', view = jump_to_giveaway_view)
                                        break
                                    
                                    users = [await self.bot.fetch_user(x) for x in data['entries']]
                                    
                                    if winners == 1:
                                        winner = random.choice(users)
                                    
                                        em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
                                        
                                        em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                        
                                        em.timestamp = datetime.datetime.now()
                                        
                                        try:
                                            await winner.send(embed = em, view = jump_to_giveaway_view)
                                        
                                        except:
                                            pass
                                        
                                        em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{winner}**', color = 0xe67e22)
                                        
                                        em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                        
                                        em.timestamp = datetime.datetime.now()
                                        
                                        try:
                                            await author.send(embed = em, view = jump_to_giveaway_view)
                                            
                                        except:
                                            pass
                                        
                                        await channel.send(f"Congratulations {winner.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
                                        
                                        gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {winner.mention}", timestamp = datetime.datetime.now())
                                        
                                        gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
                                        
                                        
                                        
                                        await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
                                        
                                    elif winners == 2:
                                        w1 = random.choice(users)
                                        users.remove(w1)
                                        
                                        w2 = random.choice(users)
                                        
                                        em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
                                        
                                        em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                        
                                        em.timestamp = datetime.datetime.now()
                                        
                                        try:
                                            await w1.send(embed = em, view = jump_to_giveaway_view)
                                        
                                        except:
                                            pass
                                        
                                        try:
                                            await w2.send(embed = em, view = jump_to_giveaway_view)
                                            
                                        except:
                                            pass
                                        
                                        em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}**', color = 0xe67e22)
                                        
                                        em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                        
                                        em.timestamp = datetime.datetime.now()
                                        
                                        try:
                                            await author.send(embed = em, view = jump_to_giveaway_view)
                                            
                                        except:
                                            pass
                                        
                                        await channel.send(f"Congratulations {w1.mention} {w2.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
                                        
                                        gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}", timestamp = datetime.datetime.now())
                                        
                                        gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
                                        
                                        await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
                                        
                                    else:
                                        w1 = random.choice(users)
                                        users.remove(w1)
                                        
                                        w2 = random.choice(users)
                                        users.remove(w2)
                                        
                                        w3 = random.choice(users)
                                        
                                        em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
                                        
                                        em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                        
                                        em.timestamp = datetime.datetime.now()
                                        
                                        try:
                                            await w1.send(embed = em, view = jump_to_giveaway_view)
                                        
                                        except:
                                            pass
                                        
                                        try:
                                            await w2.send(embed = em, view = jump_to_giveaway_view)
                                            
                                        except:
                                            pass
                                        
                                        try:
                                            await w3.send(embed = em, view = jump_to_giveaway_view)
                                            
                                        except:
                                            pass
                                        
                                        em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}, {w3}**', color = 0xe67e22)
                                        
                                        em.set_footer(text = f'{guild.name} Giveaway ended', icon_url = guild.icon.url)
                                        
                                        em.timestamp = datetime.datetime.now()
                                        
                                        try:
                                            await author.send(embed = em, view = jump_to_giveaway_view)
                                            
                                        except:
                                            pass
                                        
                                        await channel.send(f"Congratulations {w1.mention} {w2.mention} {w3.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
                                        
                                        gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}, {w3.mention}", timestamp = datetime.datetime.now())
                                        
                                        gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
                                        
                                        await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
                                        
                                    break
                                    
            if os.path.exists(file): 
                #os.remove(f'{gaw_message.id}.json')
                shutil.move(f'{giveaway_configs}/{file}', f'{ended_giveaways}/{file}')
                try:
                    os.remove(file)
                except:
                    pass
            
    except Exception as e:
        print(e)
         

class giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
                                
                                
    @commands.Cog.listener()
    async def on_ready(self):
        await check_gaws(self)                            
            
    gaw = SlashCommandGroup("giveaway", "Giveaway commands group", guild_ids = [832087404994101278, 995343462968872990])
    
    @gaw.command(description = "Used to start a Giveaway")
    @commands.check(perm_check)
    async def start(
            self, 
            ctx: ApplicationContext,
            time: Option(str, "How long should the giveaway last?"),
            winners: Option(int, "Number of winners", choices = [1, 2, 3]),
            prize: Option(str, "Giveaway prize"),
            channel: Option(discord.TextChannel, "The channel for the giveaway (defaults to the current channel).", required = False),
            donor: Option(discord.Member, "Giveaway donor", required = False),
            #blacklist: Option(str, "Role(s) that cannot join this giveaway", required = False),
            blacklist: Option(discord.Role, "Role that cannot join this giveaway", required = False),
            role: Option(discord.Role, "Role required to join this giveaway", required = False),
            message: Option(str, "Message to send with the giveaway", required = False, default = None),
            ping: Option(str, 'Select "True" to ping your server\'s giveaways role', choices = ["True", "False"], required = False)
        ):
        await ctx.defer(ephemeral = True)
        
        check = True

        if channel is None: 
            channel = ctx.channel
            check = False


        os.chdir(giveaway_configs)
        
        end_time = time_convert(time)
        
        end_time_raw = round(time_module.time() + end_time)
        
        if end_time == -1:
            return await ctx.respond("Time cannot be less than 10 seconds!")
        
        os.chdir(server_configs)
        
        f = open(f'{ctx.guild.id}.json', 'r')
        
        data = json.load(f)
        
        f.close()
        
        os.chdir(giveaway_configs)
        
        embed = data['gaw_embed']
        
        #description = "\nReact with 🎊 to enter!" if embed['description'] != "none" else f"\n{embed['description']}"
        if(embed['description'] != "none"):
            description = f"\n{embed['description']}"
        else:
            description = "\nReact with 🎊 to enter!"

        embed['title'] = embed['title'].replace('{prize}', prize)

        em = discord.Embed(title = prize if embed['title'] == "none" else embed['title'], 
                           description = f"{description}\nEnds: <t:{end_time_raw}:R> (<t:{end_time_raw}>)\nHosted by: {ctx.author.mention}", 
                           color = discord.Color.nitro_pink(), 
                           timestamp = datetime.datetime.now()
                           )
        
        em.set_footer(text = f"{winners} winners | Ends at")
        
        if donor is not None:
            
            try:
                
                #donor = await finduser(ctx, donor)
                
                em.description += f"\nDonor: {donor.mention}"
                
            except:
                pass
            
            
        roles = []
        
        if role is not None:
            
            '''em_roles = ""
            
            role = role.split()
            
            for r in role:
                r = await findrole(ctx, r)
                
                if r is None:
                    continue 
                
                roles.append(r.id)
                
            for abc in roles:
                em_roles += f" <@&{abc}>"'''
            
            em.add_field(name = "Requirement:", value = f"> {role.mention}", inline = False)
                
        bl_roles = []
        
        '''if blacklist is not None:
            
            em_bl_roles = ""
            
            blacklist = blacklist.split()
            print(blacklist)
            
            for bl in blacklist:
                bl = await findrole(ctx, bl)
                
                if bl is None:
                    continue
                
                bl_roles.append(bl.id)
                
            for abc in bl_roles:
                em_bl_roles += f" <@&{abc}>"
            
            em.add_field(name = "Blacklisted roles:", value = f"> {em_bl_roles}", inline = False)'''
        
        if blacklist is not None:
            '''bl_roles = [role for role in blacklist]

            em_bl_roles = ""

            for abc in bl_roles:
                em_bl_roles += f" {abc.mention}"'''

            em.add_field(name = "Blacklisted roles:", value = f"> {blacklist.mention}", inline = False)

        
        try:
            gaw_message = await channel.send(embed = em,)
            gaw_context = await self.bot.get_context(gaw_message)
            await gaw_message.edit(view =  end_button(end_time, winners, prize, self.bot, gaw_context))

        except Exception as e:
            print(e)
            return await ctx.respond("I do not have permission to send messages in that channel.", ephemeral = True) 
        
        data = {
            "role": roles if len(roles) > 0 else "none",
            "bl": bl_roles if len(bl_roles) > 0 else "none",
            "time": round(end_time_raw),
            "entries": []
        }
        
        os.chdir(giveaway_configs)
        
        f = open(f'{gaw_message.id}.json', 'w+')
        
        f.close()
        
        
        with open(f'{gaw_message.id}.json', 'w') as conf:
            
            json_string = json.dumps(data)
            
            conf.write(json_string)
            
        
                
                
        jump_to_giveaway_view = View()
        
        jump_to_giveaway_view.add_item(
            Button(
                label = "Jump to giveaway",
                url = f"https://discord.com/channels/{ctx.guild.id}/{channel.id}/{gaw_message.id}"
                )
                                       )
        
        if message is not None:
            em = discord.Embed(description = message, color = discord.Color.nitro_pink())
            
            os.chdir(server_configs)
            
            if ping == "True":
                
                os.chdir(server_configs)
    
                if not os.path.exists(f'{ctx.guild.id}.json'):
                
                    f = open(f'{ctx.guild.id}.json', 'w+')
                    
                    f.write(default)
                        
                    f.close()
                
                with open(f'{ctx.guild.id}.json', 'r') as conf:
                    data = json.load(conf)
                    if 'giveaway_role' not in data or data['giveaway_role'] == "none":
                        await channel.send(embed = em)
                        return await ctx.respond('This guild does not have a configured giveaway role. To set a giveaway role use `/config set_giveaway_role <role ID or mention>`', ephemeral = True)
                
                    await channel.send(content = f"<@&{data['giveaway_role']}>", embed = em)
                    
            else:
                await channel.send(embed = em)
                
        else:
            
            os.chdir(server_configs)
        
            f = open(f'{ctx.guild.id}.json', 'r')
            
            #os.chdir('C:/Users/armaa/Desktop/vscode/giveaway')
            
            data = json.load(f)
            
            f.close()
            
            if data['default_msg'] != "none":
                
                em = discord.Embed(description = data['default_msg'], color = discord.Color.nitro_pink())
                
                if ping == True:
                
                    with open(f'{ctx.guild.id}.json', 'r') as conf:
                        data = json.load(conf)
                        if 'giveaway_role' not in data or data['giveaway_role'] == "none":
                            await channel.send(embed = em)
                            return await ctx.respond('This guild does not have a configured giveaway role. To set a giveaway role use `/config set_giveaway_role <role ID or mention>`', ephemeral = True)
                    
                        await channel.send(content = f"<@&{data['giveaway_role']}>", embed = em)
                        
                else:
                    await channel.send(embed = em)
                    
            else:
                
                if ping == True:
                    
                    with open(f'{ctx.guild.id}.json', 'r') as conf:
                        data = json.load(conf)
                        if 'giveaway_role' not in data or data['giveaway_role'] == "none":
                            await channel.send(embed = em)
                            return await ctx.respond('This guild does not have a configured giveaway role. To set a giveaway role use `/config set_giveaway_role <role ID or mention>`', ephemeral = True)
                    
                        await channel.send(content = f"<@&{data['giveaway_role']}>")
                
            
            
        
        if check is True:
            await ctx.respond("✅ Successfully started the giveaway in {}!".format(channel.mention), ephemeral = True)

        else:
            await ctx.respond("✅ Successfully started the giveaway!", ephemeral = True)
        
        await asyncio.sleep(end_time)
        
        gaw_message: discord.Message = await channel.fetch_message(gaw_message.id)
        
        os.chdir(giveaway_configs)
        
        if not os.path.exists(f'{gaw_message.id}.json'):
            return
        
        f = open(f'{gaw_message.id}.json', 'r')
        
        data = json.load(f)
        
        f.close()
        
        if len(data['entries']) == 0:
            if os.path.exists(f'{gaw_message.id}.json'): 
                #os.remove(f'{gaw_message.id}.json')
                shutil.move(f'{giveaway_configs}/{gaw_message.id}.json', f'{ended_giveaways}/{gaw_message.id}.json')
                try:
                    os.remove(f'{gaw_message.id}.json')
                except:
                    pass
            return await gaw_message.reply("There were no valid entries for this giveaway.", view = jump_to_giveaway_view)
        
        users = [await self.bot.fetch_user(x) for x in data['entries']]
        
        if winners == 1:
            winner = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await winner.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{winner}**', color = 0xe67e22)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await channel.send(f"Congratulations {winner.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {winner.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
            
        elif winners == 2:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}**', color = 0xe67e22)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await channel.send(f"Congratulations {w1.mention} {w2.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
            
        else:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            users.remove(w2)
            
            w3 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            try:
                await w3.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}, {w3}**', color = 0xe67e22)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await channel.send(f"Congratulations {w1.mention} {w2.mention} {w3.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}, {w3.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
            
        if os.path.exists(f'{gaw_message.id}.json'): 
            #os.remove(f'{gaw_message.id}.json')
            shutil.move(f'{giveaway_configs}/{gaw_message.id}.json', f'{ended_giveaways}/{gaw_message.id}.json')
            try:
                os.remove(f'{gaw_message.id}.json')
            except:
                pass
        
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        os.chdir(giveaway_configs)
        
        if not os.path.exists(f'{payload.message_id}.json'):
            return
            
            
        
        with open(f'{payload.message_id}.json', 'r') as conf:
            
            data = json.load(conf)
            
            print("this is called")
            
            if time_module.time() >= data['time']:
                return
                
                
            user = self.bot.get_user(payload.user_id)
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            
            print(payload.user_id)
            
            user = payload.member
            
            print(user)
            
            if user.bot:
                return
                    
            jump_to_gaw = View()
            
            jump_to_gaw.add_item(Button(label="Jump to giveaway", url=f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{message.id}"))
            
            embed = message.embeds[0]
            
            print(len(embed.fields))
            
            if data['role'] != "none" and data['bl'] != "none":
                 
                roles = data['role']
                    
                print(roles)
                    
            
                for r in roles:
                        if channel.guild.get_role(r) not in user.roles:
                            print(channel.guild.get_role(r))
                            em = discord.Embed(
                                    title = "Missing Giveaway Requirement!", 
                                    description = f"You are missing the `{channel.guild.get_role(r)}` role required to join this giveaway!",
                                    color = discord.Color.red(),
                                    timestamp=datetime.datetime.now()
                                )
                            em.set_footer(text = channel.guild.name)
                            await user.send(embed = em, view = jump_to_gaw)
                            await message.remove_reaction(payload.emoji, user)
                            return
                            
                            
                bl_roles = data['bl']
                
                
                for r in bl_roles:
                        if channel.guild.get_role(r) in user.roles:
                            em = discord.Embed(
                                    title = "You are blacklisted from joining this giveaway!", 
                                    description = "One or more of your roles is blacklisted from this giveaway!",
                                    color = discord.Color.red(),
                                    timestamp=datetime.datetime.now()
                                )
                            em.set_footer(text = channel.guild.name)
                            await user.send(embed = em, view = jump_to_gaw)
                            await message.remove_reaction(payload.emoji, user)
                            
            else:
                
                print("bruh")
                
                if data['role'] != "none":
                    
                    print("requirement")
                
                    roles = data['role']
                        
                    print(roles)
                        
                
                    for r in roles:
                            if channel.guild.get_role(r) not in user.roles:
                                print(channel.guild.get_role(r))
                                em = discord.Embed(
                                        title = "Missing Giveaway Requirement!", 
                                        description = f"You are missing the `{channel.guild.get_role(r)}` role required to join this giveaway!",
                                        color = discord.Color.red(),
                                        timestamp=datetime.datetime.now()
                                    )
                                em.set_footer(text = channel.guild.name)
                                await user.send(embed = em, view = jump_to_gaw)
                                await message.remove_reaction(payload.emoji, user)
                
                else:
                            
                            
                    
                    bl_roles = data['bl']
                                
                    #if len(bl_roles) > 0:
                    for r in bl_roles:
                            if channel.guild.get_role(r) in user.roles:
                                em = discord.Embed(
                                        title = "You are blacklisted from joining this giveaway!", 
                                        description = "One or more of your roles is blacklisted from this giveaway!",
                                        color = discord.Color.red(),
                                        timestamp=datetime.datetime.now()
                                    )
                                em.set_footer(text = channel.guild.name)
                                await user.send(embed = em, view = jump_to_gaw)
                                await message.remove_reaction(payload.emoji, user)
                            
                            
    @gaw.command(description = "Used to end a Giveaway")
    @commands.check(perm_check)
    async def end(self, ctx: ApplicationContext, message: Option(str, "Message ID of the giveaway message")):
        '''temp, message_id = message_id.split('-')'''

        os.chdir(giveaway_configs)
        
        gaw_message = await ctx.channel.fetch_message(int(message))
        
        f = open(f'{gaw_message.id}.json', 'r')
        
        data = json.load(f)
        
        f.close()
        
        users = [await self.bot.fetch_user(x) for x in data['entries']]
        
        jump_to_giveaway_view = View()
        
        jump_to_giveaway_view.add_item(
            Button(
                label = "Jump to giveaway",
                url = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{gaw_message.id}"
                )
                                       )
        
        embed: discord.Embed = gaw_message.embeds[0]
        
        footer = embed.footer
        
        winners, temp = footer.text.split('winners')
        
        winners = int(winners.strip())
        
        prize = embed.title
        
        if winners == 1:
            winner = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await winner.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{winner}**', color = 0xe67e22)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await ctx.send(f"Congratulations {winner.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {winner.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
            
        elif winners == 2:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}**', color = 0xe67e22)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await ctx.send(f"Congratulations {w1.mention} {w2.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
            
        else:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            users.remove(w2)
            
            w3 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            try:
                await w3.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway ended!', description = f'The winners are **{w1}, {w2}, {w3}**', color = 0xe67e22)
            
            em.set_footer(text = f'{ctx.guild.name} Giveaway ended', icon_url = ctx.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await ctx.send(f"Congratulations {w1.mention} {w2.mention} {w3.mention}! You won the giveaway for **{prize}**!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}, {w3.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed, view = reroll_button(None, winners, prize, self.bot, ctx))
           
        if os.path.exists(f'{gaw_message.id}.json'): 
            #os.remove(f'{gaw_message.id}.json')
            shutil.move(f'{giveaway_configs}/{gaw_message.id}.json', f'{ended_giveaways}/{gaw_message.id}.json')
            try:
                os.remove(f'{gaw_message.id}.json')
            except:
                pass

        await ctx.respond("Giveaway ended successfully!")
            
            
            
    '''config = SlashCommandGroup("config", "Configure your server's settings", guild_ids = [832087404994101278, 829221271568908319])'''
    
    '''@commands.slash_command(description = "Configure your server's settings", guild_ids = [832087404994101278, 829221271568908319])
    @commands.check(perm_check)
    async def config(
        self, 
        ctx: ApplicationContext, 
        type: Option(
            str, 
            "Select what you wish to configure", 
            choices = [
                "Giveaway Role", 
                "Giveaway Manager", 
                "Giveaway Message"
                ]
            ),
        action: Option(
            str,
            "Select the action you wish to perform",
            choices = [
                "Edit",
                "View"
            ]
        )
        ):
        
        os.chdir('C:/Users/armaa/Desktop/vscode/giveaway/server_configs')
        
        file = f'{ctx.guild.id}.json'
        
        if not os.path.exists(file):
            
            f = open(file, 'w+')
            
            f.write(default)
            
            f.close()
            
        with open(file, 'r') as conf:
            
            data = json.load(conf)
            
            if not data['giveaway_role']:
                
                f = open(file, 'w')
                
                f.write(default)
                
                f.close()
            
            if action == "Edit":
                
                if type == "Giveaway Role":
                    
                    await ctx.respond("Enter the Giveaway Role ID or mention. (Type 'none' If you wish to reset it)", ephemeral = True)
                    
                    def check(m):
                        return m.author.id == ctx.author.id
                    
                    m = await self.bot.wait_for('message', check = check, timeout=30)
                    
                    try:
                        
                        await m.delete()
                        
                        role = m.content
                        print(role)
                        
                        if role != "none":
                            role = role.replace('<', '')
                            role = role.replace('@', '')
                            role = role.replace('&', '')
                            role = role.replace('>', '')
                            
                            print(role)
                            
                            role = ctx.guild.get_role(int(role))
                        
                        data['giveaway_role'] = role.id if role != "none" else "none"
                        
                        f = open(f'{ctx.guild.id}.json', 'w')
                        
                        f.write(json.dumps(data))
                        
                        f.close()
                        
                        await ctx.respond(content = f"Successfully changed the giveaway role to **{role.name}**" if role != "none" else "Successfully reset the giveaway role!", ephemeral = True)
                    
                    except asyncio.TimeoutError:
                        
                        await ctx.respond('Timeout!', ephemeral = True)
                        
                elif type == "Giveaway Manager":
                    
                    await ctx.respond("Enter the Giveaway Manager role ID or mention. (Type 'none' If you wish to reset it)", ephemeral = True)
                    
                    def check(m):
                        return m.author.id == ctx.author.id
                    
                    m = await self.bot.wait_for('message', check = check, timeout=30)
                    
                    try:
                        
                        await m.delete()
                        
                        role = await findrole(ctx, m.content) if m.content != "none" else "none"
                        print(role)
                        
                        data['giveaway_manager'] = role.id if role != "none" else "none"
                        
                        f = open(f'{ctx.guild.id}.json', 'w')
                        
                        f.write(json.dumps(data))
                        
                        f.close()
                        
                        guild = await self.bot.fetch_guild(ctx.guild.id)
                        n = guild.get_role(int(role.id))
                        print(n)
                        
                        await ctx.respond(content = f"Successfully changed the giveaway manager role to **{n}**" if role != "none" else "Successfully reset the giveaway manager role!", ephemeral = True)
                    
                    except asyncio.TimeoutError:
                        
                        await ctx.respond('Timeout!', ephemeral = True)
                        #OTU0Mzk2NDAzOTczNjE5Nzgy.YjSg6g.HplIy0Sxfjc6XgEEn7ltZdlWMC4
                        
                else:
                    
                    await ctx.respond("Enter the default Giveaway Message. (Type 'none' If you wish to reset it)", ephemeral = True)
                    
                    def check(m):
                        return m.author.id == ctx.author.id
                    
                    m = await self.bot.wait_for('message', check = check, timeout=30)
                    
                    try:
                        
                        await m.delete()
                        
                        data['default_msg'] = m.content
                        
                        f = open(f'{ctx.guild.id}.json', 'w')
                        
                        f.write(json.dumps(data))
                        
                        f.close()
                        
                        await ctx.respond(content = f"Successfully changed the default giveaway message to **{m.content}**" if m.content != "none" else "Successfully cleared the default giveaway message!", ephemeral = True)
                    
                    except asyncio.TimeoutError:
                        
                        await ctx.respond('Timeout!', ephemeral = True)
                        
            else:
                
                if type == "Giveaway Role":
                        
                        await ctx.respond(content = f"The configured giveaway role for this server is **{ctx.guild.get_role(data['giveaway_role'])}**" if data['giveaway_role'] != "none" else "This server does not have a configured giveaway role.", ephemeral = True)
                    
                        
                elif type == "Giveaway Manager":
                    
                    await ctx.respond(content = f"The configured giveaway manager role for this server is **{ctx.guild.get_role(data['giveaway_manager'])}**" if data['giveaway_manager'] != "none" else "This server does not have a configured giveaway manager role.", ephemeral = True)
                        
                else:
                    
                    await ctx.respond(content = f"The default giveaway message for this server is **{data['default_msg']}**" if data['default_msg'] != "none" else "This server does not have a default giveaway message", ephemeral = True)'''
                    
    
    @gaw.command(name = "role", description = "Configure your server's giveaways role")
    @commands.check(perm_check)
    async def _role(
            self,
            ctx: ApplicationContext,
            role: Option(discord.Role, "Leave empty to see the current giveaway role", required = False)
        ):
        os.chdir(server_configs)
        
        with open(f'{ctx.guild.id}.json', 'r') as conf:
            data = json.load(conf)
            
        if role is None:
            os.chdir(giveaway_configs)
            return await ctx.respond(content = f"The configured giveaway role for this server is **{ctx.guild.get_role(data['giveaway_role'])}**." if data['giveaway_role'] != "none" else "This server does not have a configured giveaway role.", ephemeral = True)
            
        #role = await findrole(ctx, role) if role != "none" else "none"
            
        data['giveaway_role'] = role.id #if role != "none" else "none"
        
        f = open(f'{ctx.guild.id}.json', 'w')
        
        f.write(json.dumps(data))
        
        f.close()
        
        await ctx.respond(content = f"Successfully changed the giveaway role to **{role.name}**.", ephemeral = True)
        
        os.chdir(giveaway_configs)
    
    @gaw.command(name = "manager", description = "Configure your server's giveaway manager role")
    @commands.check(perm_check)
    async def _mgr(
            self,
            ctx: ApplicationContext,
            role: Option(discord.Role, "Leave empty to see the current giveaway manager role", required = False)
        ):
        
        os.chdir(server_configs)
        
        with open(f'{ctx.guild.id}.json', 'r') as conf:
            data = json.load(conf)
            
            
        if role is None:
            os.chdir(giveaway_configs)
            return await ctx.respond(content = f"The configured giveaway manager role for this server is **{ctx.guild.get_role(data['giveaway_manager'])}**." if data['giveaway_manager'] != "none" else "This server does not have a configured giveaway role.", ephemeral = True)
            
        #role = await findrole(ctx, role) if role != "none" else "none"
            
        data['giveaway_manager'] = role.id #if role != "none" else "none"
        
        f = open(f'{ctx.guild.id}.json', 'w')
        
        f.write(json.dumps(data))
        
        f.close()
        
        await ctx.respond(content = f"Successfully changed the giveaway manager role to **{role.name}**", ephemeral = True)
        
        os.chdir(giveaway_configs)
        
        
    @gaw.command(name = "message", description = "Configure your server's default giveaway message")
    @commands.check(perm_check)
    async def _msg(
            self,
            ctx: ApplicationContext,
            message: Option(str, "Leave empty to see the current default message. Enter \"none\" to remove the message.", required = False)
        ):
        
        os.chdir(server_configs)
        
        with open(f'{ctx.guild.id}.json', 'r') as conf:
            data = json.load(conf)
            
        if message is None:
            os.chdir(giveaway_configs)
            return await ctx.respond(content = f"The default giveaway message for this server is **{data['default_msg']}**" if data['default_msg'] != "none" else "This server does not have a default giveaway message", ephemeral = True)
            
        data['default_msg'] = message
        
        f = open(f'{ctx.guild.id}.json', 'w')
        
        f.write(json.dumps(data))
        
        f.close()
        
        await ctx.respond(content = f"Successfully changed the default giveaway message to **{message}.**" if message != "none" else "Successfully cleared the default giveaway message!", ephemeral = True)
        
        os.chdir(giveaway_configs)
        
    
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: ApplicationContext, error):
        print(error)
        if ctx.command.full_parent_name.startswith('g') or ctx.command.qualified_name.startswith('config'):
            await ctx.respond("You need either **Manage Guild** permissions or your server's configured Giveaway Manager role to use that command.", ephemeral = True)
            
    @gaw.command(name = "embed", description = "Configure your server's giveaway embed.")
    @commands.check(perm_check)
    async def gaw_embed(self, 
                        ctx: ApplicationContext, 
                        title: Option(
                            str, 
                            "Title of the giveaway embed (Max 50 characters long). Enter \"none\" to remove the title.", 
                            default = "none", 
                            required = False,
                            max_values = 50
                            ),
                        description: Option(
                            str,
                            "Description of the giveaway embed (Max 70 characters long). Enter \"none\" to remove the description.",
                            default = "none",
                            required = False,
                            max_values = 70
                            )
                        ):
        try:
            
            os.chdir(server_configs)
            
            if not os.path.exists(f'{ctx.guild.id}.json'):
                with open(f'{ctx.guild.id}.json', 'w') as conf:
                    conf.write(default)
                    
            with open(f'{ctx.guild.id}.json', 'r') as conf:
                data = json.load(conf)
                
            em = data['gaw_embed']
            
            if title != "none":
            
                em['title'] = title
                
            if description != "none":
            
                em['description'] = description
                
            with open(f'{ctx.guild.id}.json', 'w') as conf:
                conf.write(json.dumps(data))
                
            await ctx.respond('Successfully changed the default giveaway embed!', ephemeral = True)
            
        except Exception as e:
            print(e)
            await ctx.respond('Uh-oh there seems to be an error with the **giveaway embed** command.. Don\'t worry, it will be fixed ASAP!', ephemeral = True)

    @gaw.command(
        name = "reroll",
        description = "Used to reroll a giveaway."
    )
    async def _reroll(
        self,
        ctx: ApplicationContext,
        message: Option(str, "Message ID of the giveaway message.")
    ):
        await ctx.defer(ephemeral = True)
        if not os.path.exists(f'{ended_giveaways}/{message}.json'):
            return ctx.respond("Giveaway not found.", ephemeral = True)
        
        with open(f'{server_configs}/{ctx.guild.id}.json', 'r') as conf:
            data = json.load(conf) 

        r = ctx.guild.get_role(data['giveaway_manager']) if data['giveaway_manager'] != "none" else "none"
        
        if r != "none":
            if not ctx.user.guild_permissions.manage_guild:
                return await ctx.respond('You do not have the required permission to perform this action', ephemeral = True)

        else:
            if not ctx.user.guild_permissions.manage_guild or r not in ctx.user.roles:
                return await ctx.respond('You do not have the required permission to perform this action', ephemeral = True)
            
        jump_to_giveaway_view = View()

        jump_to_giveaway_view.add_item(Button(label = "Jump to giveaway", url = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{message}"))

        gaw_message: discord.Message = await ctx.channel.fetch_message(message)
        
        f = open(f'{ended_giveaways}/{message}.json')

        data = json.load(f)

        f.close()
        
        users = [await self.bot.fetch_user(x) for x in data['entries']]

        winners = int(gaw_message.embeds[0].footer.text[9:][0])
        
        if winners == 1:
            winner = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{gaw_message.guild.name} Giveaway ended', icon_url = gaw_message.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await winner.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway was rerolled!', description = f'The winners are **{winner}**', color = 0xe67e22)
            
            em.set_footer(text = f'{gaw_message.guild.name} Giveaway ended', icon_url = gaw_message.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try: 
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await gaw_message.channel.send(f"Congratulations {winner.mention}! You won the reroll for the giveaway!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {winner.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed)
            
        elif winners == 2:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{gaw_message.guild.name} Giveaway ended', icon_url = gaw_message.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway was rerolled!', description = f'The winners are **{w1}, {w2}**', color = 0xe67e22)
            
            em.set_footer(text = f'{gaw_message.guild.name} Giveaway ended', icon_url = gaw_message.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await gaw_message.channel.send(f"Congratulations {w1.mention} {w2.mention}! You won the reroll for the giveaway!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed)
            
        else:
            w1 = random.choice(users)
            users.remove(w1)
            
            w2 = random.choice(users)
            users.remove(w2)
            
            w3 = random.choice(users)
            
            em = discord.Embed(title = "You won a giveaway!", description = "Please wait patiently to receive your prize!", color = default_colour)
            
            em.set_footer(text = f'{gaw_message.guild.name} Giveaway ended', icon_url = gaw_message.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await w1.send(embed = em, view = jump_to_giveaway_view)
            
            except:
                pass
            
            try:
                await w2.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            try:
                await w3.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            em = discord.Embed(title = 'Your giveaway was rerolled!', description = f'The winners are **{w1}, {w2}, {w3}**', color = 0xe67e22)
            
            em.set_footer(text = f'{gaw_message.guild.name} Giveaway ended', icon_url = gaw_message.guild.icon.url)
            
            em.timestamp = datetime.datetime.now()
            
            try:
                await ctx.author.send(embed = em, view = jump_to_giveaway_view)
                
            except:
                pass
            
            await gaw_message.channel.send(f"Congratulations {w1.mention} {w2.mention} {w3.mention}! You won the reroll for the giveaway!", view = jump_to_giveaway_view)
            
            gaw_embed = discord.Embed(title = "Giveaway ended!", description = f"**Winners:** {w1.mention}, {w2.mention}, {w3.mention}", timestamp = datetime.datetime.now())
            
            gaw_embed.set_footer(text = f"Winners: {winners} | Ended at")
            
            await gaw_message.edit(embed = gaw_embed)

        await ctx.respond("The giveaway was rerolled!", ephemeral = True)

        
def setup(
        bot: Union[
            commands.Bot, 
            discord.Bot
        ]
    ):
    bot.add_cog(giveaway(bot))
        