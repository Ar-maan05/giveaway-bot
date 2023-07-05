import discord
from discord.ext import commands

async def findrole(ctx: commands.Context, args) -> discord.Role:

    role=""
    
    try:
        args = args.replace('<', '')
        args = args.replace('@', '')
        args = args.replace('>', '')
        args = args.replace('!', '')
        args = args.replace('&', '')
        
        role = ctx.guild.get_role(int(args))
        return role
        
    except:
        
        pass
    
    try:
        r = list(await ctx.guild.fetch_roles) 
        role = r[r.index(role)] 
        '''ctx.guild.get_role(int(args))''' 
    except:
            
                for r in ctx.guild.roles:
                    if r.name.lower() == args.lower():
                        role=r
                        break
                        
                    
                    a_string = r.name.lower()
                    a_string=a_string.strip()
                    a = ""
                    for character in a_string:
                        if character in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
                            a += character
                    b_string = args.lower()
                    b_string=b_string.strip()
                    b = ""
                    for character in b_string:
                        if character in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
                            b += character
                    if a==b:
                        role=r
                if role == "":
                    args = args.replace('<', '')
                    args = args.replace('@', '')
                    args = args.replace('>', '')
                    args = args.replace('!', '')
                    args = args.replace('&', '')
                    try:
                        role = ctx.guild.get_role(int(args))
                    except:
                        role = ""

    return role if role != "" else None