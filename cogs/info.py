import time
import discord
import psutil
import os
import asyncio

from dhooks import Webhook, Embed
from discord.ext import commands
from datetime import datetime
from utils import repo, default


class Information:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    def get_bot_uptime(self, *, brief=False):
        now = datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = "{d} days, {h} hours, {m} minutes, and {s} seconds"
            else:
                fmt = "{h} hours, {m} minutes, and {s} seconds"
        else:
            fmt = "{h}h {m}m {s}s"
            if days:
                fmt = "{d}d " + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        message = await ctx.send("Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Pong   |   {int(ping)}ms")

    @commands.command(aliases=["info", "stats", "status"])
    @commands.guild_only()
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024 ** 2

        embed = discord.Embed(colour=0xFF8A00)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Uptime", value=self.get_bot_uptime(), inline=False)
        embed.add_field(
            name="Developer", value="Paws#0001 & SarrowSeviper#4173", inline=True
        )
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(
            name="Commands loaded",
            value=len([x.name for x in self.bot.commands]),
            inline=True,
        )
        embed.add_field(name="Servers", value=len(ctx.bot.guilds), inline=True)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)

        await ctx.send(
            content=f"ℹ About **{ctx.bot.user.name}** | **{repo.version}**", embed=embed
        )

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        if user is None:
            user = ctx.author

        embed = discord.Embed(colour=0xFF8A00)
        embed.description = (
            f"Avatar to **{user.name}**\nClick [here]({user.avatar_url}) to get image"
        )
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, user: discord.Member = None):
        """ Check when a user joined the current server """
        if user is None:
            user = ctx.author

        embed = discord.Embed(colour=0xFF8A00)
        embed.set_thumbnail(url=user.avatar_url)
        embed.description = (
            f"**{user}** joined **{ctx.guild.name}**\n{default.date(user.joined_at)}"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def server(self, ctx):
        """ Check info about current server """
        if ctx.invoked_subcommand is None:
            findbots = sum(1 for member in ctx.guild.members if member.bot)

            embed = discord.Embed(colour=0xFF8A00)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
            embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
            embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="Bots", value=findbots, inline=True)
            embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
            embed.add_field(name="Region", value=ctx.guild.region, inline=True)
            embed.add_field(
                name="Created", value=default.date(ctx.guild.created_at), inline=True
            )
            await ctx.send(
                content=f"ℹ information about **{ctx.guild.name}**", embed=embed
            )

    @commands.command()
    async def user(self, ctx, user: discord.Member = None):
        """ Get user information """
        if user is None:
            user = ctx.author

        embed = discord.Embed(colour=0xFF8A00)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="Full name", value=user, inline=True)

        if hasattr(user, "nick"):
            embed.add_field(name="Nickname", value=user.nick, inline=True)
        else:
            embed.add_field(name="Nickname", value="None", inline=True)

        embed.add_field(
            name="Account created", value=default.date(user.created_at), inline=True
        )

        if hasattr(user, "joined_at"):
            embed.add_field(
                name="Joined this server",
                value=default.date(user.joined_at),
                inline=True,
            )

        await ctx.send(content=f"ℹ About **{user.id}**", embed=embed)

    @commands.command()
    async def me(self, ctx):
        query = "SELECT * FROM artstats WHERE userid = $1;"
        row = await self.bot.db.fetchrow(query, ctx.author.id)
        if row is None:
            query = "INSERT INTO artstats VALUES ($1, 0);"
            await self.bot.db.execute(query, ctx.author.id)
            return await ctx.send(
                "I had to write you into the database! Please run this again!"
            )
        else:
            query = "SELECT * FROM artstats WHERE userid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.author.id)

            embed = discord.Embed(colour=0xFF8A00)
            embed.set_author(
                name=f"{ctx.author.name}'s Stats", icon_url=f"{ctx.author.avatar_url}"
            )
            embed.add_field(
                name="<:upvote:507362047059689472> Upvotes",
                value=f"{row['upvotes']}",
                inline=True,
            )
            embed.add_field(name="💵 Balance", value="0", inline=True)
            await ctx.send(embed=embed)

    @commands.command()
    async def you(self, ctx, member: discord.Member):
        query = "SELECT * FROM artstats WHERE userid = $1;"
        row = await self.bot.db.fetchrow(query, member.id)
        if row is None:
            query = "INSERT INTO artstats VALUES ($1, 0);"
            await self.bot.db.execute(query, member.id)
            return await ctx.send(
                "I had to write the user into the database! Please run this again!"
            )
        else:
            query = "SELECT * FROM artstats WHERE userid = $1;"
            row = await self.bot.db.fetchrow(query, member.id)

            embed = discord.Embed(colour=0xFF8A00)
            embed.set_author(
                name=f"{member.name}'s Stats", icon_url=f"{member.avatar_url}"
            )
            embed.add_field(
                name="<:upvote:507362047059689472> Upvotes",
                value=f"{row['upvotes']}",
                inline=True,
            )
            embed.add_field(name="💵 Balance", value="0", inline=True)
            await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        query = "SELECT * FROM artstats ORDER BY upvotes DESC LIMIT 3;"
        row = await self.bot.db.fetch(query)
        embed = discord.Embed(title="Leaderboard", colour=0xFF8A00)
        for user in row:
            embed.add_field(
                name=f"**{self.bot.get_user(user['userid'])}**",
                value=f"with {user['upvotes']}",
                inline=False
            )
        await ctx.send(embed=embed)

    # @commands.command()
    # async def secretsanta(self, ctx):
    #     """ Registers for the Secret Santa! """

    #     def check(reaction, user):
    #         return user == ctx.author and str(reaction.emoji) == "🎟"

    #     await ctx.message.delete()
    #     msg = await ctx.author.send(
    #         f"**{ctx.author.name}**, by entering, you are committed to drawing whatever you've been presented with. React to confirm your entry into the event."
    #     )
    #     await msg.add_reaction("🎟")
    #     try:
    #         await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
    #     except asyncio.TimeoutError:
    #         await ctx.author.send("Timed out..")
    #         await msg.delete()
    #     else:
    #         dmmsg = await ctx.author.send("You have been entered into the Secret Santa")
    #         await msg.delete()
    #         hook = Webhook(self.config.santahook, is_async=True)
    #         embed = Embed(
    #             title="Someone entered the event!",
    #             description=f"User: {ctx.author.mention}\nTag: {ctx.author.name}#{ctx.author.discriminator}\nID: {ctx.author.id}",
    #             color=0xDB1F1F,
    #             timestamp=True,
    #         )
    #         await hook.send(embeds=embed)
    #         await hook.close()
    #         await asyncio.sleep(5)
    #         await dmmsg.delete()


def setup(bot):
    bot.add_cog(Information(bot))
