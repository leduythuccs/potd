# type: ignore
from discord.ext import commands
import discord
import asyncio
import os
import time
import subprocess
import textwrap
import sys
# Adapted from TLE sources.
# https://github.com/cheran-senthil/TLE/blob/master/tle/cogs/meta.py#L15


class BotControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     pass

    # from TLE bot.
    @commands.command(brief="Check if bot is still alive.")
    async def ping(self, ctx):
        """Replies to a ping."""
        start = time.perf_counter()
        message = await ctx.send('<:pingreee:665243570655199246>')
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(content=f'<:pingreee:665243570655199246>\nREST API latency: {int(duration)}ms\n'
                                    f'Gateway API latency: {int(self.bot.latency * 1000)}ms')

    @commands.command(brief="Kill bot. ")
    @commands.check_any(commands.is_owner(), commands.has_any_role('Admin', 'Mod VNOI'))
    async def kill(self, ctx):
        """Kill bot"""
        await ctx.send("Dying")
        exit(0)

    @commands.command(brief='Restart bot')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Admin', 'Mod VNOI'))
    async def restart(self, ctx):
        await ctx.send('Restarting...')
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @commands.command(brief='Get database')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Admin', 'Mod VNOI'))
    async def db(self, ctx):
        await ctx.send(file=discord.File('database/potd.db', filename='potd.db'))
def setup(bot):
    bot.add_cog(BotControl(bot))
