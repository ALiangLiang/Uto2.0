from discord.ext import commands
from discord.ext.commands import errors
from commands.config.config import *
from core.classes import Cog_Extension

class error(Cog_Extension):
    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if hasattr(ctx.command,'on_error'):
            return
        if isinstance(error,commands.errors.MissingRequiredArgument):
            await ctx.send(ERROR_KEY_NOT_FOUND.format(PRE))
        elif isinstance(error,commands.errors.CommandInvokeError):
            await ctx.send(ERROR_CHANNEL_LIMIT)
        elif isinstance(error,commands.errors.CommandOnCooldown):
            await ctx.send(ERROR_TIME_TICK)
        else:
            pass
    pass

def setup(bot):
    bot.add_cog(error(bot))