import traceback

import discord.ui
import pytube
from pytube import exceptions, YouTube
from discord import app_commands, Interaction, Embed
from discord.ext.commands import Cog, Bot


class QualitySelectView(discord.ui.View):
    def __init__(self, yt: YouTube):
        super().__init__()
        self.yt = yt

        options = []
        streams = self.yt.streams
        for stream in streams:
            if stream.resolution is None:
                label = f"{stream.abr} - {stream.mime_type}"
            else:
                label = f"{stream.resolution} - {stream.mime_type}"
            value = stream.itag
            option = discord.SelectOption(label=label, value=value)
            options.append(option)

        self.select = discord.ui.Select(
            placeholder="Виберіть якість джерела",
            options=options
        )
        self.add_item(self.select)

    async def interaction_check(self, interaction: discord.Interaction):
        iteg = self.select.values[0]
        await interaction.response.defer(thinking=True, ephemeral=True)
        stream = self.yt.streams.get_by_itag(int(iteg))
        eb = Embed(title="Джерело готове до завантаження!", description=f"[**Завантажити**]({stream.url})")
        await interaction.followup.send(content=f"# Назва: {self.yt.title}\n"
                                                f"### Автор: {self.yt.author} | *({int(self.yt.views):,.0f} 👀)*\n"
                                                f"[**Інфо ℹ️**] Якщо доступу немає введіть команду ще раз.", embed=eb)


class YTDL(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(
        name="ytdl",
        description="Завантаження відео з YouTube в доступній якості та форматі."
    )
    @app_commands.describe(source="Джерело (посилання на відео)", )
    async def onYTDLExec(self, interaction: Interaction, source: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            video = pytube.YouTube(source)
            video.bypass_age_gate()
            if video is None:
                await interaction.followup.send("Невдала спроба обробки. Повторіть спробу ще раз.")
                return
        except exceptions.VideoUnavailable:
            await interaction.followup.send("Недоступне або не коректне посилання на відео.")
            return
        except Exception as e:
            await interaction.followup.send(
                f"Виникла неочікувана помилка.\n```{traceback.print_tb(e.__traceback__)}```")
            return
        view = QualitySelectView(yt=video)
        await interaction.followup.send(content="# Веберіть якість джерела\n"
                                                "[**Увага ⚠️**] Відео формату `webm` не містять звуку\n"
                                                "[**Інфо ℹ️ **] Перевибір формату завжди доступний в тому самому меню,"
                                                " вводити команду повторно непотрібно. *Пожалійте наші ресурси:(*",
                                        view=view)


async def setup(bot: Bot):
    await bot.add_cog(YTDL(bot))
