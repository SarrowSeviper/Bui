import time
import aiohttp
import traceback
import discord
import textwrap
import io
import datetime
import random
import json
import shlex
import gc
import os

from subprocess import Popen, PIPE
from dhooks import Webhook
from contextlib import redirect_stdout
from copy import copy
from typing import Union
from utils import repo, default, http, dataIO
from discord.ext import commands
from utils.formats import TabularData, Plural


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

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
    async def setupvotes(self, ctx, member: discord.Member, votestoset: int = 0):
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
        webhook = Webhook(url=f'{self.config.webhookurl}', content=f"<@&509164409604669450>\n\nThe prompt for {dayandmonth.day}/{dayandmonth.month}/{dayandmonth.year} is:\n\n**{row['idea']}**\n\nIt was suggested by **{row['artist']}**\n\nPlease post your submission below this line!\n\n===================")
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

    @commands.command(pass_context=True, name='eval')
    @commands.check(repo.is_owner)
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        if ctx.author.id != 127452209070735361:
            return
                          
        if "bot.http.token" in body:
            return await ctx.send(f"You can't take my token {ctx.author.name}")
        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            reactiontosend = self.bot.get_emoji(508388437661843483)
            await ctx.message.add_reaction(reactiontosend)

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                if self.config.token in ret:
                    ret = self.config.realtoken
                self._last_result = ret
                await ctx.send(f'Inputted code:\n```py\n{body}\n```\n\nOutputted Code:\n```py\n{value}{ret}\n```')

    @commands.group(aliases=["as"])
    @commands.check(repo.is_owner)
    async def sudo(self, ctx):
        """Run a cmd under an altered context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("...")

    @sudo.command(aliases=["u", "--u", "--user", "user"])
    @commands.check(repo.is_owner)
    async def sudo_user(self, ctx, who: Union[discord.Member, discord.User], *, command: str):
        """Run a cmd under someone else's name
        """
        msg = copy(ctx.message)
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg)
        await self.bot.invoke(new_ctx)

    @sudo.command(aliases=["c", "--c", "--channel", "channel"])
    @commands.check(repo.is_owner)
    async def sudo_channel(self, ctx, chid: int, *, command: str):
        """Run a command as another user."""
        cmd = copy(ctx.message)
        cmd.channel = self.bot.get_channel(chid)
        cmd.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(cmd)
        await self.bot.invoke(new_ctx)

    @commands.command()
    @commands.check(repo.is_owner)
    async def blacklist(self, ctx, uid: int):
        with open("blacklist.json", "r+") as file:
            content = json.load(file)
            content["blacklist"].append(uid)
            file.seek(0)
            json.dump(content, file)
            file.truncate()
        await ctx.send(f"I have successfully blacklisted the id **{uid}**")

    @commands.command()
    @commands.check(repo.is_owner)
    async def cogs(self, ctx):
        """ Gives all loaded cogs """
        mod = ", ".join(list(self.bot.cogs))
        await ctx.send(f"The current modules are:\n```\n{mod}\n```")
    
    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def sql(self, ctx, *, query: str):
        """Run some SQL."""
        if ctx.author.id != 127452209070735361:
            return

        query = self.cleanup_code(query)

        is_multistatement = query.count(";") > 1
        if is_multistatement:
            strategy = self.bot.db.execute
        else:
            strategy = self.bot.db.fetch

        try:
            start = time.perf_counter()
            results = await strategy(query)
            dt = (time.perf_counter() - start) * 1000.0
        except Exception:
            return await ctx.send(f"```py\n{traceback.format_exc()}\n```")

        rows = len(results)
        if is_multistatement or rows == 0:
            return await ctx.send(f"`{dt:.2f}ms: {results}`")

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()

        fmt = f"```\n{render}\n```\n*Returned {Plural(row=rows)} in {dt:.2f}ms*"
        if len(fmt) > 2000:
            fp = io.BytesIO(fmt.encode("utf-8"))
            await ctx.send("Too many results...", file=discord.File(fp, "results.txt"))
        else:
            await ctx.send(fmt)

    @commands.command()
    @commands.check(repo.is_owner)
    async def shell(self, ctx: commands.Context, *, command: str) -> None:
        """ Run a shell command. """
        if ctx.author.id != 127452209070735361:
            return
        def run_shell(command):
            with Popen(command, stdout=PIPE, stderr=PIPE, shell=True) as proc:
                return [std.decode("utf-8") for std in proc.communicate()]

        command = self.cleanup_code(command)
        argv = shlex.split(command)
        stdout, stderr = await self.bot.loop.run_in_executor(None, run_shell, argv)
        if stdout:
            if len(stdout) >= 1500:
                print(stdout)
                return await ctx.send("Too big I'll print it instead")
            await ctx.send(f"```\n{stdout}\n```")
        if stderr:
            if len(stderr) >= 1500:
                print(stderr)
                return await ctx.send("Too big I'll print it instead")
            await ctx.send(f"```\n{stderr}\n```")

    @commands.command()
    @commands.guild_only()
    @commands.check(repo.is_owner)
    async def speedup(self, ctx):
        await ctx.message.add_reaction("a:loading:528744937794043934")
        gc.collect()
        del gc.garbage[:]
        await ctx.message.remove_reaction("a:loading:528744937794043934", member=ctx.me)
        await ctx.message.add_reaction(":done:513831607262511124")

    @commands.command(hidden=True, aliases=["pull"])
    @commands.check(repo.is_owner)
    async def update(self, ctx, silently: bool = False):
        """ Gets latest commits and applies them from git """

        def run_shell(command):
            with Popen(command, stdout=PIPE, stderr=PIPE, shell=True) as proc:
                return [std.decode("utf-8") for std in proc.communicate()]

        pull = await self.bot.loop.run_in_executor(
            None, run_shell, "git pull origin master"
        )
        msg = await ctx.send(f"```css\n{pull}\n```")
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                self.bot.unload_extension(f"cogs.{name}")
                self.bot.load_extension(f"cogs.{name}")


def setup(bot):
    bot.add_cog(Admin(bot))
