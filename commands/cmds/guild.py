import imp
import discord
from discord.ext import commands
from commands.config.color import *
from commands.config.config import *
from core.aliese import *
from commands.cmds.permission import HavePermission
from core.classes import Cog_Extension
from discord_components import *
from commands.bin.embed import getembed
import json,random

class guild(Cog_Extension):
    @commands.command(name = "guild",aliases=ALIESE_guild)
    async def guildid(self,ctx):
        guild = ctx.guild
        embed = getembed(
            "",
            GUILD_DESCRPTION.format(
                guild.id,
                guild.member_count,
                guild.max_members,
                guild.preferred_locale,
                guild.premium_tier
                ),
            color=BLUE)
        embed.set_author(name=f"{guild.name}",icon_url=guild.icon_url)
        await ctx.send(embed=embed)
        
    @commands.command(name = "purge",aliases = ALIESE_purge)
    async def _clean_message(self,ctx,num:int):
        if not HavePermission(ctx.author.id,ctx.guild.id,3):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        await ctx.channel.purge(limit=num)
        await ctx.send(embed = getembed("",PURGE_SECCESS.format(num),GREEN))
def setup(bot):
    bot.add_cog(guild(bot))