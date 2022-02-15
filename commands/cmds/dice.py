from distutils import command
from email import message
from commands.bin.embed import getembed
from commands.config.color import *
from commands.config.config import *
from core.aliese import ALIESE_Random_number
from core.classes import Cog_Extension
from discord.ext import commands


def dicenumber(count:int,min:int,max:int,*mod):
    list = []
    if count == 1:
        list = [random.randint(min,max)]
    # elif len(mod)==1 and mod[0] == "norepeat":
    #     i = 0
    #     while(i<count):
    #         a = random.randint(min,max)
    #         if a not in list:
    #             list.append(a)
    #             i+=1
    else:
        for i in range(count):
            a = random.randint(min,max)
            list.append(a)
    mesge = ""
    for i in list:
        mesge += DICE_NUMBER_SUCCESS.description.format(i)
    return mesge

class dice(Cog_Extension):
    @commands.command(name = "randomnumber",aliases = ALIESE_Random_number)
    async def _random_Number(self,ctx,*modify:int):
        if len(modify)==0 or len(modify)>=4:
            return await ctx.channel.send(embed = getembed("",DICE_NUMBER_KEY_ERROR.format(PRE),RED))
        elif len(modify)==1:
            if modify[0]<1:
                return await ctx.channel.send(embed = getembed("",DICE_NUMBER_MAX_ERROR.format(1),RED))
            else:
                return await ctx.channel.send(embed = getembed(DICE_NUMBER_SUCCESS.title,dicenumber(1,1,modify[0]),DICE_NUMBER_SUCCESS.color))
        elif len(modify)==2:
            if modify[1]<modify[0]:
                return await ctx.channel.send(embed = getembed("",DICE_NUMBER_MAX_ERROR.format(modify[0]),RED))
            else:
                return await ctx.channel.send(embed = getembed(DICE_NUMBER_SUCCESS.title,dicenumber(1,modify[0],modify[1]),DICE_NUMBER_SUCCESS.color))
        elif len(modify)==3:
            if modify[2]<modify[1]:
                return await ctx.channel.send(embed = getembed("",DICE_NUMBER_MAX_ERROR.format(modify[1]),RED))
            elif modify[2]-modify[1]+1<modify[0]:
                return await ctx.channel.send(embed = getembed("",DICE_COUUNT_ERROR,RED))
            else:
                return await ctx.channel.send(embed = getembed(DICE_NUMBER_SUCCESS.title,dicenumber(modify[0],modify[1],modify[2]),DICE_NUMBER_SUCCESS.color))
        else:
            pass
def setup(bot):
    bot.add_cog(dice(bot))