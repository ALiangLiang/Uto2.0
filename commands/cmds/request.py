import imp
from commands.bin.FacebookRequest import getFbPost, openFB, writeFB
from commands.bin.WHSHannounce import openAnnounce, writeAnnounce
from commands.bin.embed import getembed
from commands.bin.time import RewriteTime, TimeZoneChange
from commands.cmds.permission import HavePermission
from commands.config.TimeConfig import WHSH_FUCK_TIME, WHSH_FUCK_TO_TIME
from commands.config.color import RED
from commands.config.config import *
from core.aliese import *
from core.classes import Cog_Extension
from discord.ext import commands


class FBrequest(Cog_Extension):
    @commands.command(name = 'fbpost',aliases=ALIESE_fbpost)
    async def sendfacebookpost(self,ctx,msg):
        if not HavePermission(ctx.author.id,ctx.guild.id,4):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        try:
            data = getFbPost(msg)
        except KeyError:
            await ctx.channel.send(embed=getembed("",WHSH_POST_GET_ERROR.format(msg),RED))
            return
        usedata = data['posts']['data'][0]
        message = usedata['message']
        Title = message.split("\n",1)
        time = RewriteTime(TimeZoneChange(usedata['created_time'],WHSH_FUCK_TIME),WHSH_FUCK_TO_TIME)
        embed = getembed(
            WHSHembed.title.format(Title[0]),
            WHSHembed.description.format(
                Title[1],
                time,
                Title[0][1:],
                usedata["id"]
            ),
            WHSHembed.color
        )
        await ctx.channel.send(embed=embed)
    @commands.command(name='post',aliases=ALIESE_connect_post)
    async def _ConnectPost(self,ctx,modify:str,data:str):
        if not HavePermission(ctx.author.id,ctx.guild.id,3):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        jdata = openFB()
        if modify in ["add","set"]:
            try:
                if ctx.channel.id in jdata["sendchannel"][data]:
                    await ctx.channel.send(embed=getembed("",POST_HAVE_CONNECT.format(data),RED))
                else:
                    jdata["sendchannel"][data].append(ctx.channel.id)
                    writeFB(jdata)
                    await ctx.channel.send(embed=getembed("",POST_CONNECT_SUCCESS.format(data,ctx.channel.name,PRE,"post",data),GREEN))
                return
            except KeyError:
                await ctx.channel.send(embed=getembed("",POST_CONNECT_KEY_ERROR.format(data,PRE),RED))
                return
        elif modify in ["remove","delete"]:
            try:
                jdata["sendchannel"][data].remove(ctx.channel.id)
                writeFB(jdata)
                await ctx.channel.send(embed=getembed("",POST_DISCONNECT_SUCCESS.format(ctx.channel.name,data),GREEN))
            except ValueError:
                await ctx.channel.send(embed=getembed("",POST_REMOVE_KEY_ERROR.format(ctx.channel.name,data),RED))
                return
            except KeyError:
                await ctx.channel.send(embed=getembed("",POST_CONNECT_KEY_ERROR.format(data,PRE),RED))
                return
    @commands.command(name='announce',aliases=ALIESE_announce)
    async def _ConnectAnnounce(self,ctx,modify:str,data:str):
        if not HavePermission(ctx.author.id,ctx.guild.id,3):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        jdata = openAnnounce()
        if modify in ["add","set"]:
            try:
                if ctx.channel.id in jdata[data]:
                    await ctx.channel.send(embed=getembed("",POST_HAVE_CONNECT.format(data),RED))
                else:
                    jdata[data].append(ctx.channel.id)
                    writeAnnounce(jdata)
                    await ctx.channel.send(embed=getembed("",POST_CONNECT_SUCCESS.format(data,ctx.channel.name,PRE,"announce",data),GREEN))
                return
            except KeyError:
                await ctx.channel.send(embed=getembed("",POST_CONNECT_KEY_ERROR.format(data,PRE),RED))
                return
        elif modify in ["remove","delete"]:
            try:
                jdata[data].remove(ctx.channel.id)
                writeAnnounce(jdata)
                await ctx.channel.send(embed=getembed("",POST_DISCONNECT_SUCCESS.format(ctx.channel.name,data),GREEN))
            except ValueError:
                await ctx.channel.send(embed=getembed("",POST_REMOVE_KEY_ERROR.format(ctx.channel.name,data),RED))
                return
            except KeyError:
                await ctx.channel.send(embed=getembed("",POST_CONNECT_KEY_ERROR.format(data,PRE),RED))
                return

def setup(bot):
    bot.add_cog(FBrequest(bot))