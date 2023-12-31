from time import time
from discord.ext import commands
from inspect import getsource
import discord
from discord.commands import slash_command, permissions
import os, sys

class EvalCommand(commands.Cog):
    def __init__(self):
        pass
    
    def resolve_variable(self, variable):
        if hasattr(variable, "__iter__"):
            var_length = len(list(variable))
            if (var_length > 100) and (not isinstance(variable, str)):
                return f"<a {type(variable).__name__} iterable with more than 100 values ({var_length})>"
            elif (not var_length):
                return f"<an empty {type(variable).__name__} iterable>"
        
        if (not variable) and (not isinstance(variable, bool)):
            return f"<an empty {type(variable).__name__} object>"
        return (variable if (len(f"{variable}") <= 1000) else f"<a long {type(variable).__name__} object with the length of {len(f'{variable}'):,}>")
    
    def prepare(self, string):
        arr = string.strip("```").replace("py\n", "").replace("python\n", "").split("\n")
        if not arr[::-1][0].replace(" ", "").startswith("return"):
            arr[len(arr) - 1] = "return " + arr[::-1][0]
        return "".join(f"\n\t{i}" for i in arr)
    
    @slash_command(guild_ids = [832087404994101278, 829221271568908319])
    @permissions.is_owner()
    async def eval(self, ctx: discord.ApplicationContext, *, code: str):
        silent = ("-s" in code)
        
        code = self.prepare(code.replace("-s", ""))
        args = {
            "discord": discord,
            "sauce": getsource,
            "sys": sys,
            "os": os,
            "imp": __import__,
            "self": self,
            "ctx": ctx,
            "send": ctx.send,
            "src": getsource,
            "author": ctx.author,
            "guild": ctx.guild
        }
        
        a=0
        
        try:
            exec(f"async def func():{code}", args)
            a = time()
            response = await eval("func()", args)
            if silent or (response is None) or isinstance(response, discord.Message):
                del args, code
                return
            
            await ctx.respond(f"```py\n{self.resolve_variable(response)}````{type(response).__name__} | {(time() - a) / 1000} ms`")
            a+=1
        except Exception as e:
            await ctx.respond(f"Error occurred:```\n{type(e).__name__}: {str(e)}```")
            a+=1
            
        if a==0:
            
            try:
                await ctx.respond('Done', ephemeral = True)
            except:
                pass
        
        del args, code, silent
        
    @eval.error
    async def eval_error(self, ctx, error):
        await ctx.respond(error, ephemeral = True)
        
def setup(bot):
    bot.add_cog(EvalCommand())