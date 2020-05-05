import os

current_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_path)

from discord.ext import commands
from helper import discord_common
from helper import config as config

token = config.config.get("DISCORD_TOKEN")
_POTD_DISCUSSION_CHANNEL = config.config.get("_POTD_DISCUSSION_CHANNEL")
def setup():
    if os.path.exists('database') is False:
        os.mkdir('database')
setup()
# bot
bot = commands.Bot(command_prefix='potd ')
print(bot.command_prefix)
bot.load_extension("cogs.BotControl")
bot.load_extension("cogs.POTD")

def no_dm_check(ctx):
    if ctx.guild is None:
        raise commands.NoPrivateMessage('Private messages not permitted.')
    return True

def check_bot_channel(ctx):
    if (ctx.guild is None):
        raise commands.NoPrivateMessage('Private messages not permitted.')
    if str(ctx.channel.id) != str(_POTD_DISCUSSION_CHANNEL):
        raise Exception('!!!! This is not the #potd, bot will do nothing')
    return True

# Restrict bot usage to inside guild channels only.
# bot.add_check(no_dm_check)

# Restrict bot usage to inside a specific channel only.
bot.add_check(check_bot_channel)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')



@bot.event
async def on_command_error(ctx, error):
    print(error)
    if ctx.guild is not None and str(ctx.channel.id) != str(_POTD_DISCUSSION_CHANNEL):
        # raise Exception('!!!! This is not the #bot channel, bot will do nothing')
        return
    await ctx.send(embed=discord_common.embed_alert(error))

@bot.event
async def on_error(event, *args, **kwargs):
    # print(event)
    pass
bot.run(token)
