import json
import os
import discord
from discord.ext import commands
import time
#from giveaway import reroll_button

default_colour = 0x87CEEB
start_time = time.time()

timer_users = 'C:\\Users\\armaa\\Desktop\\vscode\\giveaway\\timer_users'
server_configs = 'C:\\Users\\armaa\\Desktop\\vscode\\giveaway\\server_configs'
giveaway_configs = 'C:\\Users\\armaa\\Desktop\\vscode\\giveaway\\giveaway_configs'
ended_giveaways = 'C:\\Users\\armaa\\Desktop\\vscode\\giveaway\\ended_giveaways'

class Bot(commands.Bot):
    def __init__(self, prefix = "bruh "):
        super().__init__(command_prefix = prefix, intents = discord.Intents.all(), help_command = None)
        
    async def on_ready(self):
        print('Logged in as {}, {}'.format(self.user, self.user.id))
        await self.sync_commands(force = True)
        
    async def on_guild_join(self, guild: discord.Guild):
        config = {
            "giveaway_role": "none",
            "giveaway_manager": "none",
            "default_msg": "none",
            "gaw_embed": {
                "title": "none",
                "description": "none"
                }
        }
        
        os.chdir('C:/Users/armaa/Desktop/vscode/giveaway/server_configs')
        
        f = open(f'{guild.id}.json', 'w+')
        
        f.close()
        
        with open(f'{guild.id}.json', 'w') as conf:
            json_string = json.dumps(config)
            
            conf.write(json_string)
            
        os.chdir('C:/Users/armaa/Desktop/vscode/giveaway')
                

bot = Bot()

bot.load_extension('jishaku')

bot.load_extension('giveaway')

bot.load_extension('ping_cog')

bot.load_extension('google_cog')

bot.load_extension('chatchart')

bot.load_extension('calc')

bot.load_extension('tictactoe')

bot.load_extension('other_bs')

bot.load_extension('timer')

#bot.load_extension('bmi')

#bot.load_extension('slash_eval')


bot.run('token')