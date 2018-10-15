
from discord.ext import commands
from utils import default


class Fun_Commands:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command()
    async def echo(self, ctx, *, text: str):
        """
        Whatever you say!
        """
        t_echo = text.replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"{t_echo}")

    @commands.command(hidden=True)
    async def cinder(self, ctx, msg):
        """
        xd
        """
        await ctx.message.delete()
        await ctx.send("Cinder is gay. That's why he's called daddy.")

def setup(bot):
    bot.add_cog(Fun_Commands(bot))