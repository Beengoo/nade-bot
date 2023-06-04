import random

from discord import app_commands, Embed, Colour, Interaction
from discord.ext.commands import Cog, Bot

import utils


class HelpCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description=utils.synchron_read_json('./assets/messages/help.json')['command-description']
    )
    async def onHeldExec(self, interaction: Interaction):
        color = utils.synchron_read_json('./assets/messages/help.json')['embed-color']
        embed = Embed(title=utils.synchron_read_json('./assets/messages/help.json')['embed-title'], color=Colour.from_rgb(
            color[0], color[1], color[2]
        ))
        txts = utils.synchron_read_json('./assets/messages/help.json')['embed-description']
        txts.append(f"```Факт: {random.choice(utils.synchron_read_json('./assets/messages/help.json')['facts'])}```")
        embed.description = "\n".join(txts)
        await interaction.response.send_message(embed=embed)


async def setup(bot: Bot):
    print("help.py")
    await bot.add_cog(HelpCog(bot))
