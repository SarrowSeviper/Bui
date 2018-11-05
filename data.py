from utils import permissions, default
import discord

config = default.get("config.json")

from discord.ext.commands import AutoShardedBot


class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = kwargs.pop("db")

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not permissions.can_send(msg) or msg.guild is None:
            return
        else:
            if (msg.channel.id == 423890150876250122 or msg.channel.id == 444787343593832448) and (msg.attachments or "http" in msg.content) and not msg.author.bot:
                upvote = self.get_emoji(507362047059689472)
                await msg.add_reaction(upvote)
                await self.process_commands(msg)
            else:
                await self.process_commands(msg)
