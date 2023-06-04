from discord import Message
from discord.ext.commands import Cog, Bot

import utils


async def manage_msg(message: Message):
    data = utils.read_json("assets/configs/channelFilter.json")
    if data[str(message.channel.id)]['make_thread']:
        await message.create_thread(name=data[str(message.channel.id)]['thread_name'])
    if data[str(message.channel.id)]['add_reactions']:
        for reaction in data[str(message.channel.id)]['reactions_chars']:
            await message.add_reaction(reaction)

def messageHaveURL(content):
    if "https://" in content or "http://" in content:
        return True
    else:
        return False


class ChannelFilterCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_message")
    async def listen_target_channels(self, message: Message):
        data = utils.synchron_read_json("assets/configs/channelFilter.json")
        msg = utils.synchron_read_json("assets/messages/channelFilter.json")
        for channelId in data:
            if str(message.channel.id) == channelId:
                if len(message.attachments) > 0:
                    for allowed in data[channelId]['attachments_format_filter']:
                        if message.attachments[0].filename.endswith(allowed):
                            await manage_msg(message)
                            return
                    await message.author.send(msg['noAttachments'].format(channelId))
                    await message.delete()
                    return
                else:
                    if message.author.guild_permissions.mute_members and data[channelId]['ignore_mods']:
                        if messageHaveURL(message.content):
                            await manage_msg(message)
                            return
                        else:
                            return
                    elif messageHaveURL(message.content) and data[channelId]['ignore_links']:
                        await manage_msg(message)
                    else:
                        await message.author.send(msg['noAttachments'].format(channelId))
                        await message.delete()
                        return


async def setup(bot: Bot):
    await bot.add_cog(ChannelFilterCog(bot))
