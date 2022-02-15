import discord
from discord.ext import commands
import random
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from commands.bin.embed import getembed
from commands.cmds.permission import HavePermission
from commands.config.config import *
from core.aliese import *
import youtube_dl
from youtube_dl import YoutubeDL

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-http_persistent 0',
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """❌| 連接語音頻道時發生錯誤"""


class InvalidVoiceChannel(VoiceConnectionError):
    """❌| 無法進入語音頻道，請確定您在語音頻道裡"""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.duration = data.get('duration')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """僅在您不下載時允許我們使用 dict 屬性。"""
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        embed = getembed("",MUSIC_ADD_LIST.format(data['title'],data['webpage_url'],ctx.author.mention),LIGHT_GREEN)
        await ctx.send(embed=embed)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source, **ffmpegopts), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Youtube Streaming 連結過期"""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpegopts), data=data, requester=requester)


class MusicPlayer:

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .2
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            
            print("{}即將播放-1".format(self._guild.name))


            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            print("{}即將播放-2".format(self._guild.name))


            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(MUSIC_SONG_ADD_ERROR.format(e))
                    continue

            print("{}即將播放-3".format(self._guild.name))

            source.volume = self.volume
            self.current = source


            print("{}即將播放-4".format(self._guild.name))

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            embed = getembed(MUSIC_NOW_PLAYING.TITLE, MUSIC_NOW_PLAYING.DESCRIPTION.format(source.title,source.web_url,source.requester.mention), MUSIC_NOW_PLAYING.color)
            self.np = await self._channel.send(embed=embed)
            await self.next.wait()


            print("{}即將播放-5".format(self._guild.name))

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()

            print("{}即將播放-6".format(self._guild.name))
            self.current = None

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(MUSIC_NOPRIVATE_ERROR)
            except discord.HTTPException:
                pass
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='join', aliases=ALIESE_join, description="connects to voice")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = getembed("",MUSIC_MEMBER_NOT_JOIN,RED)
                await ctx.channel.send(embed=embed)
                raise InvalidVoiceChannel(MUSIC_MEMBER_HAVENT_JOIN)

        vc = ctx.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(MUSIC_MOVE_CHANNEL_TICK.format(channel))
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(MUSIC_ADD_CHANNEL_TICK.format(channel))
        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction(MUSIC_JOIN_REACTION)
        await ctx.send(MUSIC_JOIN_SUCCESS.format(channel))

    @commands.command(name='play', aliases=ALIESE_play, description="streams music")
    async def play_(self, ctx, *, search: str):
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)

    @commands.command(name='pause', aliases=ALIESE_pause, description="暫停播放音樂")
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            embed = getembed("",MUSIC_NO_PLAYING,RED)
            return await ctx.send(embed=embed)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(MUSIC_PAUSE)

    @commands.command(name='resume', aliases=ALIESE_resume, description="繼續播放音樂")
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = getembed("",MUSIC_BOT_NOT_JOINED,RED)
            return await ctx.send(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send("繼續播放音樂 ⏯️")

    @commands.command(name='skip',aliases= ALIESE_skip, description="跳過歌曲")
    async def skip_(self, ctx):
        if not HavePermission(ctx.author.id,ctx.guild.id,2):
            await ctx.channel.send(embed=getembed("",NO_PERMISSION,RED))
            return
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = getembed("",MUSIC_BOT_NOT_JOINED,RED)
            return await ctx.send(embed=embed)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            embed = getembed("",MUSIC_NO_PLAYING,RED)
            return await ctx.send(embed=embed)

        vc.stop()
        embed = getembed("",MUSIC_SKIP,PURPLE)
        return await ctx.send(embed=embed)
    
    @commands.command(name='remove', aliases=ALIESE_remove, description="從清單中移除歌曲")
    async def remove_(self, ctx, pos : int=None):
        """Removes specified song from queue"""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = getembed("",MUSIC_BOT_NOT_JOINED,RED)
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if pos == None:
            player.queue._queue.pop()
        else:
            try:
                s = player.queue._queue[pos-1]
                del player.queue._queue[pos-1]
                embed = getembed("",MUSIC_REMOVED.format(s['title'],s['webpage_url'],s['requester'].mention),GREEN)
                await ctx.send(embed=embed)
            except:
                embed = getembed("",MUSIC_SONG_NOT_FOUND.format(pos),RED)
                await ctx.send(embed=embed)
    
    @commands.command(name='stop', aliases=ALIESE_stop, description="移除播放清單")
    async def clear_(self, ctx):
        """Deletes entire queue of upcoming songs."""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = getembed("",MUSIC_BOT_NOT_JOINED,RED)
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        player.queue._queue.clear()
        await ctx.send(MUSIC_QUERE_CLEAN)

    @commands.command(name='queue', aliases=AlIESE_queue, description="顯示播放清單")
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = getembed("",MUSIC_BOT_NOT_JOINED,RED)
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if player.queue.empty():
            embed = getembed("",MUSIC_QUERE_EMPTY,BLACK)
            return await ctx.send(embed=embed)

        seconds = vc.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        # Grabs the songs in the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))
        fmt = '\n'.join(f"`{(upcoming.index(_)) + 1}.` [{_['title']}]({_['webpage_url']}) \n ` {duration} 由 {_['requester']} 加入`\n" for _ in upcoming)
        fmt = f"\n__正在撥放__:\n[{vc.source.title}]({vc.source.web_url}) \n ` {duration} 由 {vc.source.requester} 加入`\n\n__即將撥放:__\n" + fmt + f"\n**{len(upcoming)} 首歌在清單中**"
        embed = getembed(MUSIC_QUERE_TITLE.format(ctx.guild.name),fmt,GREEN)
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name='nowplaying', aliases=ALIESE_nowplaying, description="顯示正在撥放")
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = getembed("",MUSIC_BOT_NOT_JOINED,RED)
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if not player.current:
            embed = getembed("",MUSIC_NO_PLAYING,RED)
            return await ctx.send(embed=embed)
        
        seconds = vc.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        embed = getembed("",MUSIC_NOW_IS_PLAYING.format(vc.source.title,vc.source.web_url,vc.source.requester.mention,duration),GREEN)
        embed.set_author(icon_url=self.bot.user.avatar_url, name=MUSIC_NOW_PLAYING_CONFIG)
        await ctx.send(embed=embed)

    @commands.command(name='volume', aliases=ALIESE_volume, description="更改音量")
    async def change_volume(self, ctx, *, vol: float=None):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = getembed("",MUSIC_BOT_NOT_JOINED,RED)
            return await ctx.send(embed=embed)
        
        if not vol:
            embed = getembed("",MUSIC_VOLUME.format((vc.source.volume)*100),GREEN)
            return await ctx.send(embed=embed)

        if not 0 < vol < 101:
            embed = getembed("",MUSIC_VOL_VOL_ERROR,RED)
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        embed = getembed("",MUSIC_VOLUME_CHANGE.format(ctx.author,vol),GREEN)
        await ctx.send(embed=embed)

    @commands.command(name='leave', aliases=ALIESE_disconnect, description="離開語音頻道")
    async def leave_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = getembed("",MUSIC_BOT_NOT_JOINED,RED)
            return await ctx.send(embed=embed)

        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction(MUSIC_DISCONNECT_EMOJI)
        await ctx.send(MUSIC_DISCONNECT)

        await self.cleanup(ctx.guild)

    @commands.command(name='reset', aliases=ALIESE_reset,description="重新載入")
    async def reset_(self,ctx,*,channel:discord.VoiceChannel=None):
        await ctx.send(MUSIC_RESTARTING)
        try:
            await self.cleanup(ctx.guild)
        except:
            pass
        await asyncio.sleep(2)
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = getembed("",MUSIC_MEMBER_NOT_JOIN,RED)
                await ctx.send(embed=embed)
                raise InvalidVoiceChannel(MUSIC_MEMBER_HAVENT_JOIN)

        vc = ctx.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(MUSIC_MOVE_CHANNEL_TICK.format(channel))
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(MUSIC_ADD_CHANNEL_TICK.format(channel))
        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction(MUSIC_JOIN_REACTION)
        await ctx.send(MUSIC_RESTART_SUCCESS.format(channel))

def setup(bot):
    bot.add_cog(Music(bot))
    pass