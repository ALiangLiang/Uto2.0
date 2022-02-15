import discord,json,random
from discord.ext import commands
from commands.cmds.permission import HavePermission
from commands.config.config import *
from core.aliese import ALIESE_nick, ALIESE_nickchannel, ALIESE_nickname
from core.classes import Cog_Extension
from commands.bin.embed import getembed


def openNick():
    with open('./commands/config/cmdconfig/nick.json','r',encoding='utf8') as jfile:
        data = json.load(jfile)
    return data
def writeNick(data):
    with open('./commands/config/cmdconfig/nick.json','w',encoding='utf8') as jfile:
        json.dump(data,jfile,indent=4)
    return
def getNickname(id:int):
    data = openNick()
    try:
        return data["nickname"]["{}".format(id)]
    except KeyError:
        data["nickname"]["{}".format(id)]=int(100000*random.random())
        writeNick(data)
        return data["nickname"]["{}".format(id)]
def setnickname(id,name):
    data = openNick()
    data["nickname"]["{}".format(id)]=name
    writeNick(data)


class nickchannel(Cog_Extension):
    @commands.command(name = "nick",aliases = ALIESE_nick)
    async def _nick_say(self,ctx,msg):
        data = openNick()
        member = ctx.author.id
        nickname = getNickname(member)
        for i in data["nickchannel"]:
            channel = self.bot.get_channel(i)
            await channel.send("`{}`：{}".format(nickname,msg))
        await ctx.message.add_reaction(NICK_SEND_SUCCESS_REACTION)
    @commands.command(name = "setnick",aliases = ALIESE_nickname)
    async def _nickname_set(self,ctx,*name):
        if len(name)==0:
            msg = int(100000*random.random())            
        else:
            msg = " ".join(name)
        setnickname(ctx.author.id,msg)
        await ctx.channel.send(embed=getembed("",NICKNAME_SET_SUCCESS.format(msg),GREEN))
        return
    @commands.command(name = "nickchannel",aliases = ALIESE_nickchannel)
    async def _set_nick_channel(self,ctx,modify):
        if not HavePermission(ctx.author.id,ctx.guild.id,3):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        if modify in ['add','set']:
            data = openNick()
            if ctx.channel.id in data['nickchannel']:
                await ctx.channel.send(embed=getembed("",NICK_CHANNEL_HAD_SET,RED))
                return
            else:
                data['nickchannel'].append(ctx.channel.id)
                writeNick(data)
                await ctx.channel.send(embed=getembed("",NICK_CHANNEL_SET_SUCCESS.format(ctx.channel.name),GREEN))
        elif modify in ['remove','delete']:
            data = openNick()
            if not ctx.channel.id in data['nickchannel']:
                await ctx.channel.send(embed=getembed("",NICK_CHANNEL_HADDNT_SET,RED))
                return
            else:
                data['nickchannel'].remove(ctx.channel.id)
                writeNick(data)
                await ctx.channel.send(embed=getembed("",NICK_CHANNEL_DELETE_SUCCESS.format(ctx.channel.name),GREEN))
                return
    @commands.Cog.listener()
    async def on_message(self,message):
        content = message.content
        data = openNick()
        if message.channel.id in data['nickchannel'] and message.author != self.bot.user and not content.startswith("*nick"):
            await message.delete()
            name = getNickname(message.author.id)
            for id in data['nickchannel']:
                channel = self.bot.get_channel(id)
                await channel.send("`{}`：{}".format(name,content))
        return

def setup(bot):
    bot.add_cog(nickchannel(bot))