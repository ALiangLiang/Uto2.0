import discord
from discord.ext import commands
import os
from discord_components import *
from commands.config.commands import getHelpcommands
from commands.config.config import *
from commands.bin.embed import *

class CustonmHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
    
    async def send_bot_help(self, mapping):
        
        embed= getembed(Helpcommand.TITLE,Helpcommand.DESCRIPTION,Helpcommand.color)
        embed.set_author(name="Uto",icon_url= bot.user.avatar_url) 
        embed.set_footer(text=HELPFOOTER)
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        await self.get_destination().send(f'{cog.qualified_name}:{[command.name for command in cog.get_commands()]}')
    async def send_group_help(self, group):
        await self.get_destination().send(f'{group.name}:{[command.name for index, command in enumerate(group,commands)]}')
    async def send_command_help(self, command):
        name = command.name
        await self.get_destination().send(embed = getembed(HELP_COMMAND_TITLE.format(name),getHelpcommands(name),WHITE))




intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PRE,intents=intents,help_command=CustonmHelpCommand())


@bot.event
async def on_ready():
    print(BOT_ONLINE_INF)
    game = discord.Game(BOT_ONLINE_SET)
    DiscordComponents(bot)
    await bot.change_presence(status=discord.Status.idle, activity=game)




for filename in os.listdir('./commands/cmds'):
    if filename.endswith('.py'):
        bot.load_extension(f'commands.cmds.{filename[:-3]}')


if __name__ == "__main__":
    bot.run(TOKEN)