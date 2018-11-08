import time
import aiohttp
import asyncpg
import asyncio
import discord
import random
import datetime

from discord_webhook import DiscordWebhook
from utils import repo, default, http, dataIO
from discord.ext import commands


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None

    @staticmethod
    def generatecode():
        code = random.randint(11111, 99999)
        return f"{code}"

    @commands.command()
    @commands.check(repo.is_owner)
    async def reload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```\n{e}```")
            return
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command()
    @commands.check(repo.is_owner)
    async def reboot(self, ctx):
        """ Reboot the bot """
        await ctx.send('Rebooting now...')
        time.sleep(1)
        await self.bot.db.close()
        await self.bot.logout()

    @commands.command()
    @commands.check(repo.is_owner)
    async def load(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```diff\n- {e}```")
            return
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(repo.is_owner)
    async def unload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            await ctx.send(f"```diff\n- {e}```")
            return
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.group()
    @commands.check(repo.is_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @change.command(name="playing")
    @commands.check(repo.is_owner)
    async def change_playing(self, ctx, *, playing: str):
        """ Change playing status. """
        try:
            await self.bot.change_presence(
                activity=discord.Game(type=0, name=playing),
                status=discord.Status.online
            )
            dataIO.change_value("config.json", "playing", playing)
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(name="username")
    @commands.check(repo.is_owner)
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname")
    @commands.check(repo.is_owner)
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar")
    @commands.check(repo.is_owner)
    async def change_avatar(self, ctx, url: str = None):
        """ Change avatar. """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip('<>')

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await ctx.send(err)

    @commands.command()
    @commands.check(repo.is_owner)
    async def args(self, ctx, *args):
        """Returns the number of args"""
        await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

    @commands.command()
    async def amiadmin(self, ctx):
        """ Are you admin? """
        if ctx.author.id in self.config.owners:
            return await ctx.send(f"Yes **{ctx.author.name}** you are admin! ✅")
        await ctx.send(f"no, heck off {ctx.author.name}")

    @commands.command()
    @commands.guild_only()
    @commands.check(repo.is_owner)
    async def resetwarns(self, ctx, member: discord.Member):
        """ Resets user warnings """
        query = "SELECT warnings FROM warnings WHERE userid = $1;"
        row = await self.bot.db.fetchrow(query, member.id)
        if row is None:
            await ctx.send("They are not registered in the database! I'll add them now!")
            query = "INSERT INTO warnings VALUES ($1, 0);"
            await self.bot.db.execute(query, member.id)
        else:
            query = "UPDATE warnings SET warnings = 0 WHERE userid = $1;"
            await self.bot.db.execute(query, member.id)
            logchannel = self.bot.get_channel(499327315088769025)
            await ctx.send(f"I reset {member.mention}'s warns!")
            await logchannel.send(f"I reset {member.mention}'s warns!")

    @commands.command()
    @commands.guild_only()
    @commands.check(repo.is_owner)
    async def setupvotes(self, ctx, member: discord.Member, votestoset):
        """Does what it says on the tin"""
        query = "SELECT * FROM artstats WHERE userid=$1"
        row = await self.bot.db.fetchrow(query, member.id)
        if row is None:
            query = "INSERT INTO artstats VALUES ($1, $2);"
            await self.bot.db.execute(query, member.id, votestoset)
            return await ctx.send(f"**{member.name}** has been set with **{votestoset}** upvotes.")
        else:
            query = "UPDATE artstats SET upvotes=$2 WHERE userid=$1"
            await self.bot.db.execute(query, member.id, votestoset)
            await ctx.send(f"**{member.name}** has been set with **{votestoset}** upvotes.")

    @commands.command()
    @commands.guild_only()
    @commands.check(repo.is_owner)
    async def manualsketchdaily(self, ctx):
        """
        Manually send off a daily sketch
        """
        dayandmonth = datetime.date.today()
        row = await self.bot.db.fetchrow("SELECT * FROM sketchdaily ORDER BY RANDOM() LIMIT 1;")
        if row is None:
            return print("There are no suggestions...")
        print('True, sending webhook message')
        webhook = DiscordWebhook(url=f'{self.bot.config.webhookurl}', content=f"<@&509164409604669450>\n\nThe prompt for {dayandmonth.day}/{dayandmonth.month}/{dayandmonth.year} is:\n\n**{row['idea']}**\n\nIt was suggested by **{row['artist']}**\n\nPlease post your submission below this line!\n\n===================")
        webhook.execute()
        sketchcode = row['code']
        query = "DELETE FROM sketchdaily WHERE code=$1;"
        await self.bot.db.execute(query, sketchcode)

    @commands.command()
    @commands.guild_only()
    @commands.check(repo.is_owner)
    async def registersketch(self, ctx, artist: str = None, *, sketch: str = None):
        """
        Adds a database entry for sketchdaily
        """
        if artist is None:
            return await ctx.send("Please include a user!")
        if sketch is None:
            return await ctx.send("Please include an idea!")
        code = self.generatecode()
        query = "INSERT INTO sketchdaily VALUES ($1, $2, $3);"
        await self.bot.db.execute(query, int(code), artist, sketch)
        await ctx.send(f"I have successfully added the idea \"{sketch}\" by \"{artist}\" with the tag {code} to the database!")


def setup(bot):
    bot.add_cog(Admin(bot))
