import asyncio
from discord_components import *
import discord
from discord.ext import commands
from commands.bin.embed import getembed
from commands.config.color import *
from commands.config.config import *
from core.aliese import *
from core.classes import Cog_Extension



FIRST_CHECK = [[
    Button(style=ButtonStyle.blue,id="ok", label="✅確定建立"),
    Button(style=ButtonStyle.red,id="no", label="❌取消操作")
]]


COMPONENT_1 = [[
    Button(style=ButtonStyle.blue,id="useList", label="📜啟用收集名單"),
    Button(style=ButtonStyle.blue,id="noList", label="💬不收集名單(匿名)"),
    Button(style=ButtonStyle.red,id="no", label="❌取消操作")
]]
COMPONENT_2 = [[
    Button(style=ButtonStyle.blue,id="public", label="👨‍👧‍👧公開名單"),
    Button(style=ButtonStyle.blue,id="private", label="🙍🏻‍♂️僅私人名單"),
    Button(style=ButtonStyle.red,id="no", label="❌取消操作")
]]
COMPONENT_END = [[
    Button(style=ButtonStyle.blue,id="pub", label="👨‍👧‍👧公開名單"),
    Button(style=ButtonStyle.blue,id="pri", label="🙍🏻‍♂️不公開結果"),
]]


class VoteConfig:
    def __init__(self,author:discord.User,List_open:bool,public:bool,title:str,sub:list):
        self.author = author
        self.List_open = List_open
        self.public = public
        self.title = title
        self.option = {}
        for i in sub:
            self.option[i]=[]


    def addvoted(self,member:discord.User,voteid:str):
        if voteid in self.option:
            for i in self.option:
                if member in self.option[i]:
                    return getembed("",VOTE_HAD.format(i),RED)
            else:
                self.option[voteid].append(member)
                return getembed("",VOTE_SUCCESS.format(voteid),GREEN)
        else:
            return ERROR
    def show_voted(self,user:discord.User):
        if self.List_open:
            if self.public or user == self.author:
                description = ""
                for i in self.option:
                    description += VOTE_DESCRIPTION.format(i,len(self.option[i]))
                    for k in self.option[i]:
                        description += "`{}` \t".format(k.name)
                if self.public:
                    description += "\n{}".format(VOTE_GET_RESPOND.ListOpenAndPublic)
                else:
                    description += "\n{}".format(VOTE_GET_RESPOND.ListOpenButPrivate)
            else:
                description = ""
                for i in self.option:
                    description += VOTE_DESCRIPTION.format(i,len(self.option[i]))
                description += "\n{}".format(VOTE_GET_RESPOND.ListOpenButPrivate)
        else:
            description = ""
            for i in self.option:
                description += VOTE_DESCRIPTION.format(i,len(self.option[i]))
            description += "\n{}".format(VOTE_GET_RESPOND.ListNotOpen)
        return getembed(VOTE_GET_RESPOND.title.format(self.title),description,VOTE_GET_RESPOND.color)


    def components(self):
        components = [[]]
        for i in self.option:
            components[0].append(Button(style=ButtonStyle.gray,id="{}".format(i), label="{}".format(i)))
        components.append([
            Button(style=ButtonStyle.blue,id="voted_number", label="數據回報"),
            Button(style=ButtonStyle.red,id="end", label="結束投票")
        ])
        return components

    def embed(self):
        description = ""
        for i in self.option:
            description += VOTE_DESCRIPTION.format(i,len(self.option[i]))
        embed = getembed(
            "🗳投票 {}".format(self.title),description,CYAN
        )
        return embed


    #投票所有流程

    async def RUN_vote(self,bot,msg:discord.Message):
        await msg.edit(embed = self.embed(),components = self.components())
        while(True):
            interaction = await bot.wait_for('button_click',check=lambda a:a.message==msg)
            if interaction.component.id in self.option:
                await interaction.respond(embed = self.addvoted(interaction.author,interaction.component.id))
                await msg.edit(embed = self.embed())
            elif interaction.component.id == "voted_number":
                await interaction.author.send(embed = self.show_voted(interaction.author))
            elif interaction.component.id == "end":
                if interaction.author == self.author:
                    self.title += "(已結束)"
                    if self.List_open:
                        if not self.public:
                            i = await interaction.respond(embed = VOTE_CONFIG_EMBED_3,components = COMPONENT_END)
                            try:
                                interaction2 = await bot.wait_for("button_click",check=lambda a:(a.channel==interaction.channel),timeout=60)
                                if interaction2.component.id == "pub":
                                    self.public = True
                                embed = self.show_voted(bot.user)
                            except asyncio.TimeoutError:
                                pass
                            i.respond(embed = getembed("",VOTE_END,GREEN))
                        embed = self.show_voted(bot.user)
                    else:
                        embed = self.embed()
                    await msg.edit(embed = embed,components = [])
                    break
                else:
                    interaction.respond(embed = getembed("",VOTE_END_PERMISS,RED))

def setoptionList(li:list):
    list = []
    for i in li:
        if i in list:pass
        else:list.append(i)
    if len(list) == 1:return None
    else:return list
      
class vote(Cog_Extension):
    @commands.command(name = "vote", aliases = ALIESE_vote)
    async def _vote(self,ctx,title:str,*sub:str):
        list = setoptionList(sub)
        if list == None: return await ctx.channel.send(embed = VOTE_ONE_OPTION)
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            msg = await ctx.channel.send(embed = VOTE_CONFIG_EMBED_1,components = FIRST_CHECK)
            try:
                interaction = await self.bot.wait_for("button_click",check=lambda a:(a.message.id == msg.id and a.author == ctx.author),timeout=60)
                if interaction.component.id == "ok":
                    await msg.edit(embed = VOTE_EDITING,components =[])
                    i = await interaction.respond(embed = VOTE_CONFIG_EMBED_2,components = COMPONENT_1)
                    interaction2 = await self.bot.wait_for("button_click",check=lambda a:(a.channel==ctx.channel),timeout=60)


                    if interaction2.component.id == "useList":
                        i = await interaction2.respond(embed = VOTE_CONFIG_EMBED_3,components = COMPONENT_2)
                        interaction2 = await self.bot.wait_for("button_click",check=lambda a:(a.channel==ctx.channel),timeout=60)


                        if interaction2.component.id == "public":
                            Config = VoteConfig(ctx.author,True,True,title,sub)
                            await interaction2.respond(embed = getembed("",VOTE_SET_SUCCESS.format(title),GREEN))
                            await Config.RUN_vote(self.bot,msg)


                        elif interaction2.component.id == "private":
                            Config = VoteConfig(ctx.author,True,False,title,sub)
                            await interaction2.respond(embed = getembed("",VOTE_SET_SUCCESS.format(title),GREEN))
                            await Config.RUN_vote(self.bot,msg)


                        else:
                            return await msg.edit(embed = ERROR,components =[])


                    elif interaction2.component.id == "noList":
                        Config = VoteConfig(ctx.author,False,False,title,sub)
                        await interaction2.respond(embed = getembed("",VOTE_SET_SUCCESS.format(title),GREEN))
                        await Config.RUN_vote(self.bot,msg)


                    else:
                        return await msg.edit(embed = ERROR,components =[])
                else:
                    return await msg.edit(embed = ERROR,components =[])
            except asyncio.TimeoutError:
                await msg.edit(embed = TIMEOUT)
def setup(bot):
    bot.add_cog(vote(bot))