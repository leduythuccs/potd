# type: ignore
from discord.ext import commands
import discord
import asyncio
import os
import random
import json
import re
from datetime import datetime
from helper import config
from helper import discord_common
from helper import potd_database

_POTD_DISCUSSION_CHANNEL = config.config.get("_POTD_DISCUSSION_CHANNEL")
_POTD_SUGGESTION = config.config.get("_POTD_SUGGESTION")
_POTD_POST = config.config.get("_POTD_POST")
_SOLVER_OF_THE_DAY = "Solver of the day"
class POTD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.POTD_dis = self.bot.get_channel(int(_POTD_DISCUSSION_CHANNEL))
        self.POTD_post = self.bot.get_channel(int(_POTD_POST))
        self.POTD_sug = self.bot.get_channel(int(_POTD_SUGGESTION))
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) != str(_POTD_SUGGESTION):
            return
        if message.author.bot:
            return
        note = message.content
        pattern = r"https?:\/\/\S+"
        links = re.findall(pattern, note)
        if len(links) == 0:
            return
        if len(links) > 1:
            await message.channel.send("Ít bài thôi, không prof đau ruột thừa mất.")
            return
        link = links[0]
        author = message.author.id
        if potd_database.PotdDB.add_potd(link, note, author):
            for x in message.guild.emojis:
                if x.name == 'dab':
                    await message.add_reaction(x)
        else:
            await message.channel.send('Ông đừng tưởng tôi không biết ông đạo bài nhé. Gửi bài khác đê.')

    @commands.command(brief="Lấy role SOTD sau khi hoàn thành bài")
    async def gimme(self, ctx):
        if potd_database.PotdDB.today_potd() is None:
            await ctx.send("Hôm nay làm gì có Problem of the day, ông định lừa ai?")
            return

        sotd = None
        for role in ctx.guild.roles:
            if role.name == _SOLVER_OF_THE_DAY:
                sotd = role

        if sotd is None:
            await ctx.send(f'Sever đã có role `{_SOLVER_OF_THE_DAY}` đâu mà cho')
            return

        for role in ctx.author.roles:
            if role.name == _SOLVER_OF_THE_DAY:
                await ctx.send('Xin 1 lần thôi xin gì xin lắm!!!!')
                return
    
        await ctx.author.add_roles(sotd)
        for x in ctx.guild.emojis:
            if x.name == 'dab':
                await ctx.message.add_reaction(x)

    async def clear_role(self, ctx):
        sotd = None
        for role in ctx.guild.roles:
            if role.name == _SOLVER_OF_THE_DAY:
                sotd = role
        if sotd is None:
            return
        cnt_AC = 0
        for member in sotd.members:
            await member.remove_roles(sotd)
            cnt_AC += 1
        print("Cleared role SOTD")
        return cnt_AC
    
    async def post_new_problem(self, ctx):
        potd = potd_database.PotdDB.get_potd()
        if potd is None:
            await ctx.send(f"Trong queue hết bài rồi, các bạn vào suggest đi <:sadness:662197924918329365>")
            return
        link = potd[0]
        note = potd[1]
        author = potd[2]
        author = ctx.guild.get_member(int(author))
        if author is None:
            author = ctx.author
        color = discord_common._SUCCESS_BLUE_
        today = datetime.today().strftime('%d-%m-%Y')
        embed = discord.Embed(title=f"Problem of the day {today}", description= note, url=link, color=color)
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/669671624793915402/8c8e467d1ce25a0474279d076a33529a.jpg?size=1024")
        await self.POTD_post.send(embed=embed)
        return potd

    @commands.command(brief="Renew potd")
    @commands.check_any(commands.is_owner(), commands.has_any_role('Admin', 'Mod VNOI'))
    async def renew(self, ctx):
        #clear role SOTD
        current_potd = potd_database.PotdDB.today_potd()
        if current_potd is not None:
            cnt_AC = await self.clear_role(ctx)
            await ctx.send(f"Có {cnt_AC} người đã AC potd")
            link, note, author = current_potd
            potd_database.PotdDB.move_problem('potd_using', 'potd_used', link, note, author)
        #get new problem
        new_potd = await self.post_new_problem(ctx)
        if new_potd is not None:
            link, note, author = new_potd
            potd_database.PotdDB.move_problem('potd_queue', 'potd_using', link, note, author)
    
    # @commands.command(brief="Get_old potd")
    # async def get_old(self, ctx):
    #     counter = 0
    #     channel = self.bot.get_channel(671389425862705172)
    #     used = True
    #     async for message in channel.history(limit=500, oldest_first=True):
    #         counter += 1
    #         print(counter)
    #         note = message.content
    #         pattern = r"https?:\/\/\S+"
    #         links = re.findall(pattern, note)
    #         if len(links) != 1:
    #             continue
    #         link = links[0]
    #         author = message.author.id
    #         if link == 'https://codeforces.com/contest/782/problem/E':
    #             used = False
    #         if used == False:
    #             potd_database.PotdDB.add_potd(link, note, author)
    #         else:
    #             potd_database.PotdDB.add_used_potd(link, note, author)
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     self.started_channel = self.bot.get_channel(int(START_CHANNEL))
    #     await self.get_new_message()


    # @commands.command(brief="reset info")
    # @commands.check_any(commands.is_owner(), commands.has_role('admin'))
    # async def reset(self, ctx):
    #     pass

def setup(bot):
    bot.add_cog(POTD(bot))
