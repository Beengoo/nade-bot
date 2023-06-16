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
        await interaction.response.defer(thinking=True)
        
        req = requests.get("https://alerts.com.ua/map.png")
        if req.ok:
            
            with open("assets/cache/apis/alertmap.png", "wb") as f:
                f.write(req.content)
    
            await interaction.followup.send(
                file=File(fp="assets/cache/apis/alertmap.png", filename="pespatron.png"))
            return 
        else:
            await interaction.followup.send(f"Сервіс `https://alerts.com.ua` не відповідає: {req.status_code}")


async def setup(bot: Bot):
    await bot.add_cog(APIs(bot))
