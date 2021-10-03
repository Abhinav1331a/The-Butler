import discord
import datetime
from discord.ext import commands

currentTime = datetime.datetime.now()
currentTime.hour


class reply(commands.Cog):
  
  def __init__(self,client):
    self.client = client

  @commands.command()
  async def ping(self,ctx):
    await ctx.send(f'Pong {round(self.client.latency * 1000)} ms')

  @commands.command(pass_context = True , aliases=["hello", "alfred", "namaste", "good morning", "greetings", "good evening"] , case_insensitive=True)
  async def hi(self, ctx):
     await ctx.send('How can I be of service today, Master?')

  @commands.command(pass_context = True , aliases=["buhbye", "tata", "good night"] , case_insensitive=True)
  async def bye(self, ctx):
    if currentTime.hour < 18:
      await ctx.send('Very well! See you later Master!')
        
    if currentTime.hour > 18 :
      await ctx.send('Good Night Master!')

def setup(client):
  client.add_cog(reply(client))  