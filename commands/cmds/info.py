import discord
from discord.ext import commands
from commands.bin.embed import getembed
from commands.config.color import ORANGE, Face
from core.aliese import *
from core.classes import Cog_Extension

class Info(Cog_Extension):
    @commands.command(name="bot",aliases=ALIESE_bot)
    async def _information(self,ctx):
        embed = getembed(
            "關 於 Uto 2.0",
            "\n".join([
                "我的生日是 `2021/8/4`{}，已改名數次".format(Face("happy")),
                "經過的風風雨雨堪比一位高中生💦",
                "最愛吃麻婆豆腐🍣，差點吃到中風",
                "在校喜歡唱歌🎵，總遠離 **男友** 以外的男生",
                "對主人 PoChieh 採絕對服從",

                "\n 想知道更多?來看[網頁](https://utoclass.000webhostapp.com/)吧~"
            ]),
            ORANGE
        )
        await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))