import os
import sys

from discord import Intents
from discord.ext.commands import Bot
import traceback

from discord_webhook import DiscordWebhook

import utils


def excepthook(exc_type, exc_value, exc_traceback):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    try:
        wh = DiscordWebhook(url=utils.synchron_read_json("config.json")['excepthook-webhook'],
                            content=f"""☠️ Перехоплено виняток
                            ```{''.join(traceback.format_tb(exc_traceback))}\n{str(exc_type)}:{exc_value}```
""").execute()
    except:
        pass


sys.excepthook = excepthook


class BotBase(Bot):
    def __init__(self, command_prefix=".", intents=Intents.all(), help_command=None):
        super().__init__(command_prefix=command_prefix, intents=intents, help_command=help_command)

    async def setup_hook(self) -> None:
        for cog_file in os.listdir("./cogs"):
            if cog_file.endswith('.py'):
                await self.load_extension("cogs." + cog_file[:-3])
        await self.tree.sync()


bot = BotBase()
bot.run(utils.synchron_read_json('config.json')['botToken'])
