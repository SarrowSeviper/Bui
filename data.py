from utils import permissions, default
import discord

config = default.get("config.json")

from discord.ext.commands import AutoShardedBot


class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = kwargs.pop("db")

    async def on_message(self, msg):
        blacklist = default.get("blacklist.json")
        
        if not self.is_ready() or msg.author.bot or not permissions.can_send(msg) or msg.guild is None or msg.author.id in blacklist:
            return
        if (msg.channel.id == 445658065933434892 or msg.channel.id == 510141164179947574 or msg.channel.id == 445659536016277514) and (msg.attachments or "http" in msg.content) and not msg.author.bot:
            upvote = self.get_emoji(507362047059689472)
            await msg.add_reaction(upvote)
            await self.process_commands(msg)
        else:
            await self.process_commands(msg)
