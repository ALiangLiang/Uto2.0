import psutil,os
import discord
from discord.ext import commands
from commands.bin.embed import getembed
from commands.cmds.permission import HavePermission
from commands.config.color import *
from commands.config.config import NO_PERMISSION, RAM_EMBED
from core.aliese import ALIESE_ram
from core.classes import Cog_Extension

class Ram(Cog_Extension):
    @commands.command(aliases=ALIESE_ram)
    async def ram(self,ctx):
        if not HavePermission(ctx.author.id,ctx.guild.id,4):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        def my_ram():
            process = psutil.Process(os.getpid())
            return (psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
        memoryEmbed = getembed(RAM_EMBED.TITLE,RAM_EMBED.DESCRIPTION.format(my_ram()),RAM_EMBED.color)
        await ctx.send(embed=memoryEmbed)
    @commands.command()
    async def load(self,ctx,extension):
        if not HavePermission(ctx.author.id,ctx.guild.id,4):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        self.bot.load_extension(f'commands.cmds.{extension}')
        await ctx.channel.send(f'Load commands.cmds.{extension} Done')
    @commands.command()
    async def reload(self,ctx,extension):
        if not HavePermission(ctx.author.id,ctx.guild.id,4):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        self.bot.reload_extension(f'{extension}')
        await ctx.channel.send(f'reLoad {extension} Done')
    @commands.command()
    async def unload(self,ctx,extension):
        if not HavePermission(ctx.author.id,ctx.guild.id,4):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        self.bot.unload_extension(f'commands.cmds.{extension}')
        await ctx.channel.send(f'unLoad commands.cmds.{extension} Done')
def setup(bot):
    bot.add_cog(Ram(bot))
