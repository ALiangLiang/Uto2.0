import asyncio
import discord
from commands.bin.FacebookRequest import *
from commands.bin.WHSHannounce import announce, openAnnounce
from commands.bin.time import dateCalculate, getTempNowTime
from commands.cmds.date import openDate, writeDate
from core.classes import Cog_Extension

class DateListener(Cog_Extension):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        async def time_task():
            now_time = getTempNowTime("%d")
            await self.bot.wait_until_ready()
            while not self.bot.is_closed():
                if now_time != getTempNowTime("%d"):
                    #倒數日
                    data = openDate()
                    for i in data:
                        c = data[i]
                        try:
                            channel = self.bot.get_channel(c["id"])
                        except:
                            del data[i]
                            writeDate(data)
                            continue
                        date = dateCalculate(c["year"],c["month"],c["day"])
                        await channel.edit(name = c["name"].format(date))
                    
                    #文華日報
                    data = openAnnounce()
                    embed = announce()
                    if len(data["WHSHannounce"])!=0:
                        for i in data["WHSHannounce"]:
                            channel = self.bot.get_channel(i)
                            await channel.send(embed=embed)
                    now_time = getTempNowTime("%d")
                await asyncio.sleep(1000)
        self.bg_task = self.bot.loop.create_task(time_task())
def setup(bot):
    bot.add_cog(DateListener(bot))