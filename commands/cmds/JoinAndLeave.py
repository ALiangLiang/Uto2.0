import json
import discord
from discord.ext import commands
from commands.bin.embed import getembed
from commands.cmds.permission import HavePermission
from commands.config.color import *
from commands.config.config import *
from core.classes import Cog_Extension
from core.aliese import *

class JoinAndLeave(Cog_Extension):
    @commands.command(name = 'joinconnect',aliases=ALIESE_joinmessage)
    async def joinconnect_(self,ctx,*,msg):
        if not HavePermission(ctx.author.id,ctx.guild.id,3):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        with open("./commands/config/cmdconfig/JoinAndLeave.json",'r',encoding='utf8') as jfile:
            Js = json.load(jfile)
        channels = self.bot.get_channel(ctx.channel.id)
        data = {"channel":int(ctx.channel.id),"txt":msg}
        Js['{}.join'.format(ctx.guild.id)] = data
        with open('./commands/config/cmdconfig/JoinAndLeave.json','w') as jfile:
            json.dump(Js,jfile,indent=4)
        await ctx.send(JOIN_CONNECT.format(channels))


    @commands.command(name = 'leaveconnect',aliases=ALIESE_leavemessage)
    async def leaveconnect_(self,ctx,*,msg):
        if not HavePermission(ctx.author.id,ctx.guild.id,3):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        with open("./commands/config/cmdconfig/JoinAndLeave.json",'r',encoding='utf8') as jfile:
            Js = json.load(jfile)
        channels = self.bot.get_channel(ctx.channel.id)
        data = {"channel":int(ctx.channel.id),"txt":msg}
        Js['{}.leave'.format(ctx.guild.id)] = data
        with open('./commands/config/cmdconfig/JoinAndLeave.json','w') as jfile:
            json.dump(Js,jfile,indent=4)
        await ctx.send(LEAVE_CONNECT.format(channels))
    


    @commands.Cog.listener()
    async def on_member_join(self,member):
        try:
            with open('./commands/config/cmdconfig/JoinAndLeave.json','r',encoding='utf8') as jfile:
                jwelcome = json.load(jfile)
            guild = self.bot.get_guild(member.guild.id)
            channel = self.bot.get_channel(int(jwelcome['{}.join'.format(member.guild.id)]["channel"]))
            text = str(jwelcome['{}.join'.format(member.guild.id)]['txt'])
            if "{member}" in text:
                pos=text.find('{member}')
                tmp = text[(pos+8):]
                text = text[:(pos)] + f'{member}' + tmp
            if "{guild}" in text:
                pos=text.find('{guild}')
                tmp = text[(pos+7):]
                text = text[:(pos)] + f'{guild}' + tmp
            embed=getembed("",text,PURPLE)
            await channel.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        try:
            with open('./commands/config/cmdconfig/JoinAndLeave.json','r',encoding='utf8') as jfile:
                jwelcome = json.load(jfile)
            guild = self.bot.get_guild(member.guild.id)
            channel = self.bot.get_channel(int(jwelcome['{}.leave'.format(member.guild.id)]["channel"]))
            text = str(jwelcome['{}.leave'.format(member.guild.id)]['txt'])
            if "{member}" in text:
                pos=text.find('{member}')
                tmp = text[(pos+8):]
                text = text[:(pos)] + f'{member}' + tmp
            if "{guild}" in text:
                pos=text.find('{guild}')
                tmp = text[(pos+7):]
                text = text[:(pos)] + f'{guild}' + tmp
            embed=getembed("",text,BLACK)
            await channel.send(embed=embed)
        except:
            pass

def setup(bot):
    bot.add_cog(JoinAndLeave(bot))