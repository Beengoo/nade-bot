import os
import traceback
from typing import List

from discord import app_commands, Interaction
from discord.app_commands import Choice
from discord.ext.commands import Cog, Bot

import utils


class CogManagerCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(
        name="ctxmmgr",
        description="Manage bot context menu"
    )
    @app_commands.describe(
        name="Name of context menu",
        action="What i need todo?"
    )
    @app_commands.choices(
        action=[
            Choice(name="Add", value="add"),
            Choice(name="Remove", value="remove")
        ]
    )
    async def onCTXMMGRExec(self, interaction: Interaction, name: str, action: str):
        await interaction.response.defer(thinking=True)
        if utils.checkDev(interaction.user.id, utils.synchron_read_json("config.json")['devIds']):
            await interaction.edit_original_response(content="Coming soon.")

    @app_commands.command(
        name="cmgr",
        description="Cog management command",
    )
    @app_commands.describe(
        action="What i need todo?",
        cog_file="Cog .py file"
    )
    @app_commands.choices(
        action=[
            Choice(name="Disable", value="disable"),
            Choice(name="Enable", value="enable"),
            Choice(name="Reload", value="reload")
        ]
    )
    async def onCMGRExec(self, interaction: Interaction, action: str, cog_file: str):
        await interaction.response.defer(thinking=True)
        if utils.checkDev(interaction.user.id, utils.synchron_read_json("config.json")['devIds']):
            if action == "disable":
                try:
                    if action == "all":
                        for cog_file in os.listdir("./cogs"):
                            await self.bot.unload_extension(name="cogs." + cog_file[:-3])
                        await self.bot.tree.sync()
                        await interaction.edit_original_response(content="All cogs disabled!")
                    else:
                        await self.bot.unload_extension(name=f"cogs." + cog_file[:-3])
                        await self.bot.tree.sync()
                        await interaction.edit_original_response(content=f"Cog **{cog_file}** disabled")
                except:
                    await interaction.edit_original_response(
                        content=f"```{traceback.format_exc()}```"
                    )
            elif action == "enable":
                try:
                    if action == "all":
                        for cog_file in os.listdir("./cogs"):
                            await self.bot.load_extension(name="cogs." + cog_file[:-3])
                        await self.bot.tree.sync()
                        await interaction.edit_original_response(content="All cogs enabled!")
                    else:
                        await self.bot.load_extension(name=f"cogs." + cog_file[:-3])
                        await self.bot.tree.sync()
                        await interaction.edit_original_response(content=f"Cog **{cog_file}** enabled")
                except:
                    await interaction.edit_original_response(
                        content=f"```{traceback.format_exc()}```"
                    )

            elif action == "reload":
                try:
                    if action == "all":
                        for cog_file in os.listdir("./cogs"):
                            await self.bot.reload_extension(name="cogs." + cog_file[:-3])
                        await self.bot.tree.sync()
                        await interaction.edit_original_response(content="All cogs reloaded!")
                    else:
                        await self.bot.reload_extension(name=f"cogs." + cog_file[:-3])
                        await self.bot.tree.sync()
                        await interaction.edit_original_response(content=f"Cog **{cog_file}** reloaded")
                except:
                    await interaction.edit_original_response(
                        content=f"```{traceback.format_exc()}```"
                    )

        else:
            await interaction.edit_original_response(content="This command allowed only for developers.")

    @onCMGRExec.autocomplete('cog_file')
    async def on_resync_autocomplete(self,
                                     interaction: Interaction,
                                     current: str) -> List[app_commands.Choice[str]]:
        if utils.checkDev(interaction.user.id, utils.synchron_read_json("config.json")['devIds']):
            cogs = [
                app_commands.Choice(name=cog, value=cog)
                for cog in os.listdir("./cogs") if current.lower() in cog.lower() and cog.endswith(".py")
            ]
            cogs.append(app_commands.Choice(name="*", value="all"))

            return cogs
        else:
            return [Choice(name="What are you doing here?", value="permdeined")]


async def setup(bot: Bot):
    print("cogmanager.py")
    await bot.add_cog(CogManagerCog(bot))
