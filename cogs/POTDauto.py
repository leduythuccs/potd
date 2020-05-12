# type: ignore
from discord.ext import commands
import discord
import asyncio
import os
import random
import json
import re
from datetime import date
from datetime import datetime
from datetime import timedelta
from helper import config
from helper import discord_common
from helper import potd_database

_POTD_DISCUSSION_CHANNEL = config.config.get("_POTD_DISCUSSION_CHANNEL")
_POTD_SUGGESTION = config.config.get("_POTD_SUGGESTION")
_POTD_POST = config.config.get("_POTD_POST")
_SOLVER_OF_THE_DAY = "Solver of the day"

class POTDauto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.POTD_dis = self.bot.get_channel(int(_POTD_DISCUSSION_CHANNEL))
        self.POTD_post = self.bot.get_channel(int(_POTD_POST))
        self.POTD_sug = self.bot.get_channel(int(_POTD_SUGGESTION))
    
    async def clear_role(self, message):
        sotd = None
        for role in message.guild.roles:
            if(role.name == _SOLVER_OF_THE_DAY):
                sotd = role
        if(sotd is None):
            return
        
        cnt_AC = 0
        for member in sotd.members:
            await member.remove_roles(sotd)
            cnt_AC += 1

        current_potd = potd_database.PotdDB.today_potd()
        link, note, author = current_potd
        potd_database.PotdDB.move_problem('potd_using', 'potd_used', link, note, author)

        await self.POTD_dis.send("{} fellas have completed their missions!!".format(cnt_AC))
    
    async def post_new_problem(self, message):
        potd = potd_database.PotdDB.get_potd()
        if potd is None:
            await message.channe.send("No POTD ready to reserve.")
            return
        
        link = potd[0]
        note = potd[1]
        author = potd[2]
        author = message.guild.get_member(int(author))

        if author is None:
            author = message.author

        color = discord_common._SUCCESS_BLUE_
        today = datetime.today().strftime('%d-%m-%Y')
        embed = discord.Embed(title=f"Problem of the day {today}", description= note, url=link, color=color)
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/669671624793915402/8c8e467d1ce25a0474279d076a33529a.jpg?size=1024")
        # await message.channel.send(embed=embed)

        # await message.channel.send(potd[2])   
        potd_database.PotdDB.move_problem('potd_queue', 'potd_using', link, note, potd[2])
        await self.POTD_post.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if(message.author.bot):
            return
        
        oldMessage = (await self.POTD_post.history(limit=1).flatten())[0]
        lastDate = oldMessage.created_at
        curDate = message.created_at
        diff = curDate - lastDate
        if(diff.days == 0):
            return


        await self.clear_role(message)
        await self.post_new_problem(message)
        await self.POTD_dis.send("Last POTD was posted {} days ago. Probably time for a new one?!?".format(diff.days))


def setup(bot):
    bot.add_cog(POTDauto(bot))