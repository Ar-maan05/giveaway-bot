import discord
from discord.ext import commands

async def finduser(ctx: commands.Context, args) -> discord.Member:
    try:
        member = ctx.message.mentions[0]
        return member
    except:
        pass
    try:
        args, temp=args.split('#')
    except:
        args=args
    member=""
    try:
        member = await ctx.bot.fetch_user(int(args))
    except:
            
                for m in ctx.guild.members:
                    if m.display_name.lower() == args.lower():
                        member=m
                        break
                        
                    
                    a_string = m.display_name.lower()
                    a_string=a_string.replace(" ", "")
                    a = ""
                    for character in a_string:
                        if character in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
                            a += character
                    b_string = args.lower()
                    b_string=b_string.replace(" ", "")
                    b = ""
                    for character in b_string:
                        if character in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
                            b += character
                    if a==b:
                        member=m
                if member == "":
                  try:
                    args = args.replace('<', '')
                    args = args.replace('@', '')
                    args = args.replace('>', '')
                    args = args.replace('!', '')
                    member = ctx.guild.get_member(int(args))
                  except:
                    for m in ctx.guild.members:
                      if m.name.lower() == args.lower():
                          member=m
                          break
                      
                      a_string = m.name.lower()
                      a_string=a_string.strip()
                      a = ""
                      for character in a_string:
                          if character.isalnum():
                              a += character
                      b_string = args.lower()
                      b_string=b_string.strip()
                      b = ""
                      for character in b_string:
                          if character.isalnum():
                              b += character
                      if a==b:
                          member=m

    return member if member != "" else None