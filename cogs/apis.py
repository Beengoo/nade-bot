import requests
from discord import app_commands, Interaction, File
from discord.ext.commands import Cog, Bot


class APIs(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(
        name="alert",
        description="Карта тривог України"
    )
    async def onAlertExec(self, interaction: Interaction):
        req = requests.get("https://alerts.com.ua/map.png")
        with open("assets/cache/apis/alertmap.png", "wb") as f:
            f.write(req.content)

        await interaction.response.send_message(
            file=File(fp="assets/cache/apis/alertmap.png", filename="pespatron.png"))


async def setup(bot: Bot):
    await bot.add_cog(APIs(bot))
