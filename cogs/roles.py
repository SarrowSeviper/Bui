from discord.ext import commands
from utils import default

import asyncio
import discord


class Role_Distribution:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.group()
    async def iam(self, ctx):
        """
        Used for assigning roles to yourself!
        """
        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @iam.command(name="nsfw")
    async def iam_nsfw(self, ctx):
        """
        - Gives the NSFW role
        """

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '👍'

        await ctx.message.delete()
        msg = await ctx.author.send(f"**{ctx.author.name}**, by requesting this role, you are agreeing to our terms and conditions, Discord's Terms of Service, and Community Guideline. We are not liable if you are found that you are not within legal age to view NSFW content within your country.\n\nOur Terms of Service : <https://goo.gl/Mi4yEj>\nDiscord's Terms of Service: <https://discordapp.com/terms>\nDiscord's Community Guidelines: <https://discordapp.com/guidelines>\n\nIf you agree by all of the above, then please react with :thumbsup: below.")
        await msg.add_reaction('👍')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send('Timed out..')
            await msg.delete()
        else:
            dmmsg = await ctx.author.send('You should have the NSFW role now! If not, contact a staff member.')
            await msg.delete()
            message = []
            for role in ctx.guild.roles:
                if role.name == "testing":
                    message.append(role.id)
            try:
                therole = discord.Object(id=message[0])
            except:
                return

            await ctx.author.add_roles(therole)
            await asyncio.sleep(5)
            await dmmsg.delete()

    @iam.command(name="advertising")
    async def iam_advertising(self, ctx):
        """
        - Gives the Advertising role
        """

        message = []
        for role in ctx.guild.roles:
            if role.name == "testing":
                message.append(role.id)
        try:
            therole = discord.Object(id=message[0])
        except:
            return

        await ctx.author.add_roles(therole)
        await ctx.message.delete()
        msg = await ctx.send(f"**{ctx.author.name}**, I have given you the **Advertising** role!")
        await asyncio.sleep(5)
        await msg.delete()


def setup(bot):
    bot.add_cog(Role_Distribution(bot))