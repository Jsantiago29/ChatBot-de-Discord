import datetime
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def sum(ctx, num1: int, num2:int):
    await ctx.send(num1+num2)

@bot.command()
async def info(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name}", description="Puros corridos tumbados", timestamp=datetime.datetime.utcnow())
    await ctx.send(embed=embed)

#Events
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="Ser ingeniero", url="http://www.twitch.tv/accountname"))
    print('My bot is ready')

bot.run('MTExNzMxNTc5MjUxODc4NzEzMw.GTM110.AtPmk7j-0E25Fd385yOPBK4l1AO-VUSug4CESI')