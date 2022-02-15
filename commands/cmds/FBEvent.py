import datetime,json,asyncio
from commands.bin.embed import getembed
import discord
from commands.bin.FacebookRequest import *
from commands.bin.time import RewriteTime, TimeZoneChange
from commands.config.TimeConfig import WHSH_FUCK_TIME, WHSH_FUCK_TO_TIME
from commands.config.config import WHSHembed
from core.classes import Cog_Extension 
import requests
import facebook
import urllib3




class FBpost(Cog_Extension):
    #a = datetime.datetime.now().strftime('%Y %m %d %H %M')
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        async def time_task():
            await self.bot.wait_until_ready()
            Id = "whsh"
            data = getFbPost(Id)
            updateNowId(Id,data)
            while not self.bot.is_closed():
                await asyncio.sleep(50)
                now_time = datetime.datetime.now().strftime('%M')
                if (int(now_time)%15==0):
                    data = getFbPost(Id)
                    count = getCount(Id,data)

                    def sendmessage(i):
                        usedata = data['posts']['data'][i]
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
                        return embed

                    if count==-1:
                        for i in range(100):
                            embed = sendmessage(99-i)
                            for k in openFB()["sendchannel"]["whsh"]:
                                try:
                                    channel = self.bot.get_channel(k)
                                except:
                                    pass
                                await channel.send(embed=embed)
                    elif(count==0):
                        pass
                    else:
                        for i in range(count):
                            embed = sendmessage(count-i-1)
                            for k in openFB()["sendchannel"]["whsh"]:
                                channel = self.bot.get_channel(k)
                                await channel.send(embed=embed)
                        await asyncio.sleep(100)
                    updateNowId(Id,data)
        self.bg_task = self.bot.loop.create_task(time_task())
def setup(bot):
    bot.add_cog(FBpost(bot))