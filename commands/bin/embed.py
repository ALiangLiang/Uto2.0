import discord
from commands.config.color import *

def getembed(title,description,color):
    embed = discord.Embed(
        title = title,
        description = description,
        color = color
    )
    embed.set_footer(text="Code by Po-Chieh")
    return embed