import os
import asyncio
import asyncpg

from discord.ext.commands import HelpFormatter
from data import Bot
from utils import permissions, default

config = default.get("config.json")
description = """
A bot for the Bui's Art Society!
"""


class HelpFormat(HelpFormatter):
    async def format_help_for(self, context, command_or_bot):
        await context.message.delete()

        return await super().format_help_for(context, command_or_bot)


async def run():
    help_attrs = dict(hidden=True)
    credentials = {
        "user": config.dbname,
        "password": config.dbpass,
        "database": config.database,
        "host": "127.0.0.1",
    }
    db = await asyncpg.create_pool(**credentials)

    await db.execute(
        "CREATE TABLE IF NOT EXISTS warnings(userid bigint, warnings int);"
    )
    await db.execute("CREATE TABLE IF NOT EXISTS artstats(userid bigint, upvotes int);")
    await db.execute(
        "CREATE TABLE IF NOT EXISTS sketchdaily(code int, artist varchar, idea varchar);"
    )

    bot = Bot(
        command_prefix=config.prefix,
        prefix=config.prefix,
        pm_help=True,
        help_attrs=help_attrs,
        formatter=HelpFormat(),
        db=db,
    )
    try:
        print("Logging in...")
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                bot.load_extension(f"cogs.{name}")
        await bot.start(config.token)
    except KeyboardInterrupt:
        await db.close()
        await bot.logout()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
