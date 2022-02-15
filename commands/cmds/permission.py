import json
import discord
from discord.ext import commands
from commands.bin.embed import getembed
from commands.config.config import *
from core.aliese import *
from core.classes import Cog_Extension

def getP():
    with open("./commands/config/cmdconfig/permission.json",'r',encoding='utf8') as jfile:
        data = json.load(jfile)
    return data
def writeP(data):
    with open("./commands/config/cmdconfig/permission.json",'w',encoding='utf8') as jfile:
        json.dump(data,jfile,indent=4)

def setlevel(level):
    if level == "4" or level == "devoloper":
        return 4
    elif level == "3" or level == "admin":
        return 3
    elif level == "2" or level == "high":
        return 2
    else:
        return "Err"
def getlevel(member:int,guild:int):
    k=0
    data = getP()
    if member in data["devoloper"]:
            return 4
    if str(guild) in data["admin"]:
        if member in data["admin"]["{}".format(guild)]:
            return 3
    else:
        k=1
    if str(guild) in data["high"]:
        if member in data["high"]["{}".format(guild)]:
            return 2
    else:
        if k==1:return 3
        else:return 1
    return 1
    
def givelevel(i):
    if i==4:
        return "devoloper"
    elif i==3:
        return "admin"
    elif i==2:
        return "high"
    else:
        return "normal"

def HavePermission(memberId:int,guild:int,level:int):
    if getlevel(memberId,guild)>=level:
        return True
    else:
        return False


class Permission(Cog_Extension):
    @commands.command(name="permission",aliases=ALIESE_permission)
    async def _Permission(self,ctx,modify:str,member:discord.User,level:str):
        data = getP()
        L = setlevel(level)
        if isinstance(L,str):
            embed = getembed("",PERMISSION_KEY_ERROR.format(PRE),RED)
            await ctx.channel.send(embed=embed)
        tag = member.id
        if L==4:
            embed = getembed("",PERMISSION_DEVOLOPER_ERROR,RED)
            await ctx.channel.send(embed=embed)
            return
        if (modify=="add"):
            if getlevel(ctx.author.id,ctx.guild.id)<L:
                embed = getembed("",PERMISSION_LOWER,RED)
                await ctx.channel.send(embed=embed)
                return
            elif getlevel(tag,ctx.guild.id)>L:
                embed = getembed("",PERMISSION_HAVE_HIGHER.format(member.name,level),RED)
                await ctx.channel.send(embed=embed)
            elif getlevel(tag,ctx.guild.id)==L:
                embed = getembed("",PERMISSION_HAVED.format(member.name,level),RED)
                await ctx.channel.send(embed=embed)
            else:
                try:
                    data["{}".format(level)]["{}".format(ctx.guild.id)].append(tag)
                    writeP(data)
                except KeyError:
                    data["{}".format(level)]["{}".format(ctx.guild.id)] = [tag]
                    writeP(data)
                embed = getembed("",PERMISSION_EDIT_SUCCESS.format("新增",member.name,level),GREEN)
                await ctx.channel.send(embed=embed)
        elif (modify == "remove"):
            pass
        else:
            embed = getembed("",PERMISSION_KEY_ERROR.format(PRE),RED)
            await ctx.channel.send(embed=embed)
    @commands.command(name = "sendpermission", aliases=ALIESE_get_permission)
    async def _send_permission(self,ctx,member:discord.User):
        embed = getembed("",PERMISSION_GET.format(member.name,givelevel(getlevel(member.id,ctx.guild.id))),LIGHT_BLUE)
        await ctx.channel.send(embed=embed)
def setup(bot):
    bot.add_cog(Permission(bot))