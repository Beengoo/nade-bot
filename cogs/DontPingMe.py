import json
import random
from datetime import datetime, timedelta

from discord import Message, app_commands, Interaction, Embed
from discord.app_commands import Choice
from discord.ext.commands import Cog, Bot, cooldowns

import utils


class DontPingMe(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        self.cooldowns = {}

    @Cog.listener("on_message")
    async def ping_detected(self, message: Message):
        # Перевіряємо, чи повідомлення не від бота і не є командою
        if not message.author.bot and not message.content.startswith(self.bot.command_prefix):
            if message.content.startswith(f"<@{self.bot.user.id}>"):
                last_call = self.cooldowns.get(message.author.id)

                # Перевіряємо, чи існує кулдаун для користувача і чи пройшов достатній час
                if last_call is None or datetime.now() - last_call > timedelta(seconds=30):

                    await message.reply(random.choice(utils.synchron_read_json("assets/configs/memes.json")['list']))

                    self.cooldowns[message.author.id] = datetime.now()
                else:
                    pass

            if message.reference:
                sel_message = await message.channel.fetch_message(message.reference.message_id)
                if sel_message is not None and sel_message.author.id == self.bot.user.id\
                        and sel_message.content in utils.synchron_read_json("assets/configs/memes.json")['list']:
                    await message.reply(random.choice(utils.synchron_read_json("assets/configs/memes.json")['list']))

    @app_commands.command(
        name="dontpingme",
        description="dontPingMe configuration command"
    )
    @app_commands.describe(
        action="Setect action",
        text="Add a text or url",
        index="Select a index (for remove)"
    )
    @app_commands.choices(
        action=[
            Choice(name="Add", value="add"),
            Choice(name="Remove", value="remove"),
            Choice(name="List", value="list")
        ]
    )
    async def onDontPingMeExec(self, interaction: Interaction, action: str, text: str = None, index: int = None):
        if not utils.isDM(interaction):
            return

        await interaction.response.defer(thinking=True)
        if action == "list":
            list = utils.synchron_read_json("assets/configs/memes.json")['list']
            new_list = []
            embed = Embed(title="Список мемів, якими бот відовідає на пінг")
            iteration = 1
            for text in list:
                new_list.append(f'> {iteration}. {text}')
                iteration += 1

            embeds = []
            current_description = ''
            for item in new_list:
                if len(current_description) + len(item) > 3048:  # Перевірка, чи перевищено ліміт 2048 символів
                    new_embed = Embed(title="Не влізло:)")
                    new_embed.description = current_description
                    embeds.append(new_embed)
                    current_description = ''
                current_description += '\n\n' + item

            if current_description:  # Додати останній Embed, якщо залишилось ще щось у current_description
                new_embed = Embed(title="Список мемів, якими бот відовідає на пінг")
                new_embed.description = current_description
                embeds.append(new_embed)

            await interaction.followup.send(embeds=embeds)

        elif action == "add":
            if text is None:
                await interaction.followup.send("`text` є обов'язковим!")
            else:
                memes = utils.synchron_read_json("assets/configs/memes.json")
                memes['list'].append(text)
                with open("assets/configs/memes.json", "w", encoding='utf-8') as f:
                    json.dump(memes, f, indent=4, ensure_ascii=False)
                await interaction.followup.send("Додано ще один мем!")

        elif action == "remove":
            if index is None:
                await interaction.followup.send("`index` є обов'язковим!")
            else:
                memes = utils.synchron_read_json("assets/configs/memes.json")
                memes['list'].pop(index - 1)
                with open("assets/configs/memes.json", "w", encoding='utf-8') as f:
                    json.dump(memes, f, indent=4, ensure_ascii=False)
                await interaction.followup.send(f"Мем по індексу **{index}** було видалено!")


async def setup(bot: Bot):
    await bot.add_cog(DontPingMe(bot))
