from commands.bin.embed import getembed
from commands.cmds.permission import HavePermission
from commands.bin.time import dateCalculate
from commands.config.config import *
from commands.config.color import *
from core.aliese import *
from core.classes import Cog_Extension
from discord.ext import commands
import json


def openDate():
    with open('./commands/config/cmdconfig/DateCalculate.json','r',encoding='utf8') as jfile:
        data = json.load(jfile)
    return data
def writeDate(data):
    with open('./commands/config/cmdconfig/DateCalculate.json','w',encoding='utf8') as jfile:
        json.dump(data,jfile,indent=4)



class DateCalculate(Cog_Extension):
    @commands.command(name = "datechannel",aliases = ALIESE_datechannel)
    async def _Set_Date_Channel(self,ctx,modify,*type):
        if not HavePermission(ctx.author.id,ctx.guild.id,3):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        if modify in ADD_LIST:
            if len(type)!=4:
                return await ctx.channel.send(embed = getembed("",DATE_KEY_ERROR.format(PRE),RED))
            else:
                await ctx.channel.edit(name = type[3].format(dateCalculate(int(type[0]),int(type[1]),int(type[2]))))
                data = openDate()
                data["{}".format(ctx.channel.id)] = {"id":ctx.channel.id,"year":int(type[0]),"month":int(type[1]),"day":int(type[2]),"name":type[3]}
                writeDate(data)
                return await ctx.channel.send(embed = getembed("",DATE_CHANNEL_EDIT_SUCCESS.format(ctx.channel.name),GREEN))
        elif modify in DELETE_LIST:
            data = openDate()
            if not str(ctx.channel.id) in data:
                await ctx.channel.send(embed = getembed("",DATE_CHANNEL_NOT_FOUND,RED))
            else:
                del data["{}".format(ctx.channel.id)]
                writeDate(data)
                return await ctx.channel.send(embed = getembed("",DATE_CHANNEL_DELETE_SUCCESS.format(ctx.channel.name),GREEN)) 
        else:
            await ctx.channel.send(embed = getembed("",DATE_KEY_ERROR.format(PRE),RED))
        return
def setup(bot):
    bot.add_cog(DateCalculate(bot))