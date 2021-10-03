import json
import discord
import os
from discord.ext import commands 
from keep_alive import keep_alive

def get_prefix(client,message):
  with open('prefixes.json', 'r')as f:
     prefixes = json.load(f)
  return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix = get_prefix)

@client.event
async def on_guild_join(guild):
   with open('prefixes.json', 'r')as f:
     prefixes = json.load(f)
   prefixes[str(guild.id)] = '-'

   with open('prefixes.json', 'w')as f:
     json.dump(prefixes, f, indent=4)

@client.event
async def on_guild_remove(guild):
   with open('prefixes.json', 'r')as f:
     prefixes = json.load(f)
   prefixes.pop[str(guild.id)]

   with open('prefixes.json', 'w')as f:
     json.dump(prefixes, f, indent=4)   

@client.command()
async def changeprefix(ctx, prefix):
  with open('prefixes.json', 'r')as f:
   prefixes = json.load(f)
   prefixes[str(ctx.guild.id)] = prefix

  with open('prefixes.json', 'w')as f:
   json.dump(prefixes, f, indent=4) 

  await ctx.send(f'Prefix has been changed to {prefix}')

@client.command()
async def load(ctx, extension):
  client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
  client.unload_extension(f'cogs.{extension}')

@client.command()
async def reload(ctx, extension):
  client.unload_extension(f'cogs.{extension}')
  client.load_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    client.load_extension(f'cogs.{filename[:-3]}')

@commands.Cog.listener()
async def on_ready(self):
    print(f'Logged in as {self.client.name}'.format(self.client.name))

keep_alive()
client.run(os.getenv('token'))
