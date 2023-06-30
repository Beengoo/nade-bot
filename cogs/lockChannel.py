import discord
from discord import Interaction, app_commands
from discord.ext.commands import Bot, Cog


class LockChannel(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(
        name="lock_channel",
        description="Just a command"
    )
    @app_commands.describe(
        channel="Select channel",
        target="Target"
    )
    async def onLockChannelExec(self, interaction: Interaction,
                                channel: discord.VoiceChannel | discord.TextChannel | discord.StageChannel,
                                target: discord.Role | discord.Member):
        await interaction.response.defer(thinking=True, ephemeral=True)

        await channel.set_permissions(target=target,
                                      overwrite=discord.PermissionOverwrite(connect=False, read_message_history=False,
                                                                            send_messages=False))
        await interaction.followup.send(f"Канал успішно заблоковано для {target.mention}")


    @app_commands.command(
        name="unlock_channel",
        description="Just a command"
    )
    @app_commands.describe(
        channel="Select channel",
        target="Target"
    )
    async def onUnlockChannelExec(self, interaction: Interaction,
                                  channel: discord.VoiceChannel | discord.TextChannel | discord.StageChannel,
                                  target: discord.Role | discord.Member):

        await interaction.response.defer(ephemeral=True, thinking=True)

        await channel.set_permissions(target=target,
                                      overwrite=discord.PermissionOverwrite(connect=None, read_message_history=None,
                                                                            send_messages=None))
        await interaction.followup.send(f"Канал успішно розблоковано для {target.mention}")


async def setup(bot: Bot):
    await bot.add_cog(LockChannel(bot))
