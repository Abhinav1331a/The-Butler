import discord
import asyncio
import os
import youtube_dl
import urllib.parse, urllib.request, re
import requests
from discord.ext import commands
from discord import Embed, FFmpegPCMAudio
from discord.utils import get

queue = {}
servers = {}



youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream or play))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        queue = {}
        self.queue = queue
        servers = {}
        self.servers = servers
        cur_song = " "
        cur_song_id = 0
        self.cur_song = cur_song
        self.cur_song_id = cur_song_id

    @commands.command()
    async def join(self, ctx):
      self.queue = queue
      if not ctx.message.author.voice:
          await ctx.send("You are not connected to a voice channel!")
          return
      else:
          channel = ctx.message.author.voice.channel
          self.queue = {}
          await ctx.send(f'Connected to ``{channel}``')

      await channel.connect()

    @commands.command(pass_context=True, aliases = ["p"])
    async def play(self, ctx, *, url):
            server = servers[ctx.guild.id]
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                try:
                  if len(self.queue) != 0:
                    self.queue[len(self.queue)] = url
                    await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n<:youtube:763374159567781890> **Added to queue:** ``{}'.format(player.title) + "``")


                


                  else:
                    self.queue[0] = url 
                    self.cur_song = self.queue[0]
                    self.cur_song_id = 0
                    await self.start_playing(ctx, self.cur_song)
                    await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n<:youtube:763374159567781890> **Now Playing:** ``{}'.format(player.title) + "``")

                except:
                  await ctx.send("Somenthing went wrong - please try again later!")

    async def start_playing(self, ctx, url): 
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)     

    async def transformer(self,ctx, url):
      player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
      if ctx.voice_client and ctx.voice_client.is_connected():
        print('Already connected to voice')
        pass

      else: 
        await ctx.message.author.voice.channel.connect()

      ctx.voice_client.play(player)

    @commands.command(pass_context=True, aliases= ["pa","pp"], case_insensitive=True)
    async def pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        voice.pause()

        user = ctx.message.author.mention
        await ctx.send(f"Bot was paused by {user}")

    @commands.command(pass_context=True, aliases= ["r","res","rp"], case_insensitive=True)
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        voice.resume()

        user = ctx.message.author.mention
        await ctx.send(f"Bot was resumed by {user}")

    @commands.command(pass_context=True, aliases= ["qp"], case_insensitive=True)
    async def pq(self,ctx, number):
      if int(number) in self.queue:
         source = self.queue[int(number)]
         self.cur_song_id = int(number)
         await ctx.send(f"Song is {source}")
         await ctx.send(f"Song id is {self.cur_song_id}")
         await self.transformer(ctx, source)
      

    @commands.command(pass_context=True, aliases= ["aq"])
    async def add_queue(self, ctx, *, url):

        global queue

        try:
         self.queue[len(self.queue)] = url 
         user = ctx.message.author.mention
         await ctx.send(f'``{url}`` was added to the queue by {user}!')

        except:
         await ctx.send(f"Couldnt add {url} to the queue!")

    @commands.command(pass_context=True, aliases= ["rq"])
    async def remove_queue(self, ctx, number):

        global queue


        del(self.queue[int(number)])
        if len(self.queue) < 1:
            await ctx.send("Your queue is empty now!")
        else:
            await ctx.send(f'Your queue is now {self.queue}')

    @commands.command(pass_context=True, aliases= ["cq"], case_insensitive=True)
    async def clear_queue(self, ctx):

        global queue

        queue.clear()
        self.queue.clear()
        user = ctx.message.author.mention
        await ctx.send(f"The queue was cleared by {user}")

    @commands.command(pass_context=True, aliases= ["q"], case_insensitive=True)
    async def view_queue(self, ctx):
  
        if len(self.queue) < 1:
            await ctx.send("The queue is empty - nothing to see here!")
        else:
           await ctx.send(f'Your current queue is {self.queue}')

    @commands.command(pass_context=True, aliases= ["disconnect", "quit", "get out"], case_insensitive=True)
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        user = ctx.message.author
        await voice_client.disconnect()
        await ctx.send(f'Disconnected from ``{user.voice.channel}``')
        self.queue.clear()
   
    @commands.command(pass_context=True, aliases= ["s","next"], case_insensitive=True)
    async def skip(self, ctx):
      ctx.voice_client.stop()
      if self.cur_song_id == (len(self.queue)-1):
        self.cur_song_id = 0
      else:
        self.cur_song_id = self.cur_song_id + 1
      await self.transformer(ctx, self.queue[self.cur_song_id])
          
    @commands.command(pass_context=True, aliases= ["previous","back"], case_insensitive=True)
    async def prev(self, ctx):
      ctx.voice_client.stop()
      if self.cur_song_id == 0:
        self.cur_song_id = (len(self.queue)-1)
      else:
        self.cur_song_id = self.cur_song_id - 1
      await self.transformer(ctx, self.queue[self.cur_song_id])
    
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

def setup(client):
    client.add_cog(Voice(client))









''''
if voice is not playing and queue is 0{
  add song to queue and start playing()
}
if voice is not playing and queue is not 0{
  add song to queue
}
if voice is  playing and queue is not 0{
 add song to queue
}

'''