import asyncio
import json
import random
import traceback

import aiosqlite3
from discord import Message, Member, StageChannel, VoiceChannel, VoiceState, app_commands, Interaction, Embed, Colour, \
    Role, User
from discord.app_commands import Choice
from discord.ext.commands import Cog, Bot

import utils


async def getAllDB(bot: Bot):
    async with bot.db.execute("SELECT * FROM levels ORDER BY level DESC") as cour:
        results = await cour.fetchall()

    exp_data = []
    for row in results:
        level, voice_xp, text_xp, user = row
        exp_data.append({"level": level, "voice_xp": voice_xp, "text_xp": text_xp, "user": user,
                         "totally_exp": voice_xp + text_xp})

    return exp_data


async def getRankData(bot: Bot, member: Member):
    async with bot.db.execute("SELECT level, voice_xp, text_xp FROM levels WHERE user = ?", (member.id,)) as cour:
        result = await cour.fetchone()

    if result is None:
        return {"level": 0, "voice_xp": 0, "text_xp": 0}

    level, voice_xp, text_xp = result
    if level is None:
        level = 1
    if voice_xp is None:
        voice_xp = 0
    if text_xp is None:
        text_xp = 0

    return {"level": level, "voice_xp": voice_xp, "text_xp": text_xp, "totally_exp": voice_xp + text_xp}


async def writeLevelData(bot: Bot, member: Member, level: int):
    async with bot.db.execute(f"SELECT level FROM levels WHERE user = ?", (member.id,)) as cour:
        level_ = await cour.fetchone()

    if not level_:
        await bot.db.execute(f"INSERT INTO levels (level, user) VALUES (?, ?, ?)", (1, 0, member.id))
        await bot.db.commit()

    await bot.db.execute(f"UPDATE levels SET level = ? WHERE user = ?", (level, member.id))
    await bot.db.commit()


async def addExpData(bot: Bot, member: Member, type_: str, exp: float = 0):
    async with bot.db.execute(f"SELECT {type_}_xp FROM levels WHERE user = ?", (member.id,)) as cour:
        xp_ = await cour.fetchone()

    if not xp_:
        await bot.db.execute(f"INSERT INTO levels (level, text_xp, voice_xp, user) VALUES (?, ?, ?, ?)", (1, 0, 0,
                                                                                                          member.id))
        if bot.db.in_transaction:
            await bot.db.commit()

    xp_ = xp_[0] if xp_ is not None else 0

    if xp_ is not None:
        xp_ += float(exp)

    await bot.db.execute(f"UPDATE levels SET {type_}_xp = ? WHERE user = ?", (xp_, member.id))
    await bot.db.commit()


async def setExpData(bot: Bot, member: Member, type_: str, exp: float = 0):
    async with bot.db.execute(f"SELECT {type_}_xp FROM levels WHERE user = ?", (member.id,)) as cour:
        xp_ = await cour.fetchone()

    if not xp_:
        await bot.db.execute(f"INSERT INTO levels (level, text_xp, voice_xp, user) VALUES (?, ?, ?, ?)", (1, 0, 0,
                                                                                                          member.id))
        await bot.db.commit()

    await bot.db.execute(f"UPDATE levels SET {type_}_xp = ? WHERE user = ?", (exp, member.id))
    await bot.db.commit()


async def checkLevel(bot: Bot, member: Member):
    data = await getRankData(bot, member)
    config = await utils.read_json("assets/configs/rank.json")
    lang = await utils.read_json("assets/messages/rank.json")
    level_before = data['level']
    level_after = int(data['totally_exp'] ** (1 / 2.92))

    if level_before != level_after:
        await writeLevelData(bot, member, level_after)
        if level_before < level_after:
            try:
                await bot.get_channel(config['botLvlUpAlertChannel']).send(lang['lvlUp'].format(member, level_after))
            except AttributeError:
                pass


def exp_to_next_level(exp):
    current_level = int(exp ** (1 / 2.92))
    next_level = current_level + 1
    next_level_exp = next_level ** 2.92
    exp_needed = next_level_exp - exp
    progress_percentage = (exp / next_level_exp) * 100
    return [exp_needed, progress_percentage]


def level_to_exp(level):
    return int(level ** 2.92)


async def checkRoles(bot: Bot, member: Member):
    config = await utils.read_json("assets/configs/rank.json")
    user_rank = await getRankData(bot, member)
    user_rank_lvl = user_rank['level']
    lvlRoles = config['lvlRoles']
    roles = dict(sorted(lvlRoles.items(), key=lambda x: int(x[0])))

    user_have_roles = []
    reward_roles = []
    need_reward = None
    for lvl, role_id in roles.items():
        for role in member.guild.roles:
            if role is not None and role.name != "@everyone":
                if role.id == role_id:
                    reward_roles.append([role, lvl])
                    if role in member.roles:
                        user_have_roles.append(role)

    for role, role_lvl in reward_roles:
        if user_rank_lvl >= int(role_lvl):
            need_reward = role

    need_remove = user_have_roles

    if len(need_remove) > 0:
        index = 0
        for i in need_remove:
            if i == need_reward:
                need_remove.pop(index)
                need_reward = None
                break
            index += 1

    if need_remove:
        await member.remove_roles(*need_remove)
    if need_reward:
        await member.add_roles(need_reward)


class Rank2RankLoop(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.temp_voice_info = {}

    @Cog.listener(name="on_ready")
    async def ready(self):
        self.bot.db = await aiosqlite3.connect('assets/databases/rank/users.db')
        async with self.bot.db.execute(
                "CREATE TABLE IF NOT EXISTS levels (level INTEGER, voice_xp INTEGER, text_xp REAL, user INTEGER"
                " PRIMARY KEY)"):
            pass

    @Cog.listener(name="on_message")
    async def message_listener(self, message: Message):
        if message.author.bot:
            return
        if isinstance(message.author, User):
            return
        author = message.author
        await addExpData(self.bot, author, "text", random.randint(1, 5))
        await checkLevel(self.bot, author)
        await checkRoles(self.bot, author)

    async def control_shot(self):
        guild = self.bot.get_guild(utils.synchron_read_json("config.json")["targetGuildId"])
        for memberId in dict(self.temp_voice_info):
            targeMember = guild.get_member(int(memberId))
            if targeMember is None:
                pass
            elif targeMember.voice is None \
                    or await utils.check_blocked_channel(
                guild.get_channel(self.temp_voice_info[memberId]['channel_id'])) \
                    or await utils.check_blocked_role(targeMember):
                self.temp_voice_info.pop(memberId)
            else:
                channelID = targeMember.voice.channel.id
                channelType = "voice" if isinstance(targeMember.voice.channel, VoiceChannel) else "stage" if isinstance(
                    targeMember.voice.channel, StageChannel) else "UNKNOWN"
                channelMember = len(targeMember.voice.channel.members)
                isSpeaker = None
                if isinstance(targeMember.voice.channel, StageChannel):
                    isSpeaker = False
                    if targeMember in targeMember.voice.channel.speakers:
                        isSpeaker = True
                isMuted = targeMember.voice.mute
                isSelfMuted = targeMember.voice.self_mute
                isDeaf = targeMember.voice.deaf
                isSelfDeaf = targeMember.voice.self_deaf
                isStreaming = targeMember.voice.self_stream
                isTurnCamera = targeMember.voice.self_video

                # Я заєбався поки це писав блять :D
                if channelType != self.temp_voice_info[memberId]["channel_type"] \
                        or channelMember != self.temp_voice_info[memberId]["channel_members"] \
                        or isSpeaker != self.temp_voice_info[memberId]["is_speaker"] \
                        or isMuted != self.temp_voice_info[memberId]["is_muted"] \
                        or isSelfMuted != self.temp_voice_info[memberId]["is_self_muted"] \
                        or isDeaf != self.temp_voice_info[memberId]["is_deaf"] \
                        or isSelfDeaf != self.temp_voice_info[memberId]["is_self_deaf"] \
                        or isStreaming != self.temp_voice_info[memberId]["is_streaming"] \
                        or isTurnCamera != self.temp_voice_info[memberId]["is_turn_camera"]:
                    self.temp_voice_info[str(targeMember.id)] = {
                        "channel_id": channelID,
                        "channel_type": channelType,
                        "channel_members": channelMember,
                        "is_speaker": isSpeaker,
                        "is_muted": isMuted,
                        "is_self_muted": isSelfMuted,
                        "is_deaf": isDeaf,
                        "is_self_deaf": isSelfDeaf,
                        "is_streaming": isStreaming,
                        "is_turn_camera": isTurnCamera,
                    }

    @Cog.listener("on_ready")
    async def check_voices(self):
        guild = self.bot.get_guild(utils.synchron_read_json("config.json")["targetGuildId"])
        for member in guild.members:
            if member.voice is None:
                pass
            else:
                isSpeaker = None
                if isinstance(member.voice.channel, StageChannel):
                    isSpeaker = False
                    if member in member.voice.channel.speakers:
                        isSpeaker = True

                self.temp_voice_info[str(member.id)] = {
                    "channel_id": member.voice.channel.id,
                    "channel_type": "voice" if isinstance(member.voice.channel, VoiceChannel) else "stage"
                    if isinstance(member.voice.channel, StageChannel) else "UNKNOWN",
                    "channel_members": len(member.voice.channel.members),
                    "is_speaker": isSpeaker,
                    "is_muted": member.voice.mute,
                    "is_self_muted": member.voice.self_mute,
                    "is_deaf": member.voice.deaf,
                    "is_self_deaf": member.voice.self_deaf,
                    "is_streaming": member.voice.self_stream,
                    "is_turn_camera": member.voice.self_video,
                }

    async def add_voice_exp(self):
        try:
            guild = self.bot.get_guild(utils.synchron_read_json("config.json")["targetGuildId"])
            await self.control_shot()
            for memberId in dict(self.temp_voice_info):
                target_member = guild.get_member(int(memberId))

                exp = 0
                try:
                    if self.temp_voice_info[memberId]['is_muted'] or self.temp_voice_info[memberId]['is_self_muted'] \
                            or self.temp_voice_info[memberId]['is_deaf'] \
                            or self.temp_voice_info[memberId]['is_self_deaf']:
                        pass
                    else:
                        if self.temp_voice_info[memberId]['channel_members'] > 1:
                            exp += self.temp_voice_info[memberId]['channel_members'] / 4 + 2
                            if self.temp_voice_info[memberId]["is_speaker"]:
                                exp += 3.75
                            if self.temp_voice_info[memberId]['is_streaming']:
                                exp += 0.75
                            if self.temp_voice_info[memberId]['is_turn_camera']:
                                exp += 1.25

                            await addExpData(self.bot, target_member, "voice", exp)
                            await checkLevel(self.bot, target_member)
                            await checkRoles(self.bot, target_member)
                except KeyError:
                    if target_member.voice is not None:
                        if target_member.voice.mute or target_member.voice.self_mute or target_member.voice.deaf \
                                or target_member.voice.self_deaf:
                            pass
                        else:
                            if len(target_member.voice.channel.members) > 1:
                                exp += len(target_member.voice.channel.members) / 4 + 2
                            if isinstance(target_member.voice.channel, StageChannel) and \
                                    target_member in target_member.voice.channel.speakers:
                                exp += 3.75
                            if target_member.voice.self_stream:
                                exp += 0.75
                            if target_member.voice.self_video:
                                exp += 1.25

                            await addExpData(self.bot, target_member, "voice", exp)
                            await checkLevel(self.bot, target_member)
                            await checkRoles(self.bot, target_member)

        except Exception as e:
            print(f"{e}: {traceback.format_exc()}")

    @Cog.listener()
    async def on_ready(self) -> None:
        await self.ranking_loop()

    async def ranking_loop(self):
        while utils.synchron_read_json("assets/configs/rank.json")['useRankLeveling']:
            await self.add_voice_exp()
            await asyncio.sleep(utils.synchron_read_json("assets/configs/rank.json")['XPPerSeconds'])

    @Cog.listener("on_voice_state_update")
    async def get_current_voice_info(self, member: Member, before: VoiceState, after: VoiceState):
        if after.channel is not None:
            self.temp_voice_info.clear()
            for member in after.channel.members:
                if not member.bot and not after.afk:
                    if after.channel is None:
                        pass
                    else:
                        speaker = None
                        if isinstance(after.channel, StageChannel):
                            speaker = False
                            if member in after.channel.speakers:
                                speaker = True
                        self.temp_voice_info[str(member.id)] = {
                            "channel_id": after.channel.id,
                            "channel_type": "voice" if isinstance(after.channel,
                                                                  VoiceChannel) else "stage" if isinstance(
                                after.channel, StageChannel) else "UNKNOWN",
                            "channel_members": len(after.channel.members),
                            "is_speaker": speaker,
                            "is_muted": member.voice.mute,
                            "is_self_muted": member.voice.self_mute,
                            "is_deaf": member.voice.deaf,
                            "is_self_deaf": member.voice.self_deaf,
                            "is_streaming": member.voice.self_stream,
                            "is_turn_camera": member.voice.self_video,
                        }


class Rank2Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(
        name="rank",
        description=utils.synchron_read_json("assets/messages/rank.json")['rankDescription']
    )
    @app_commands.describe(
        member=utils.synchron_read_json("assets/messages/rank.json")['userArg']
    )
    async def onRankExec(self, interaction: Interaction, member: Member = None):
        await interaction.response.defer(thinking=True)
        lang = utils.synchron_read_json("assets/messages/rank.json")
        if member is None:
            member = interaction.user
        if not member.bot:
            data = await getRankData(self.bot, member)
            await addExpData(self.bot, member, "text", exp=0)

            embed = Embed(color=Colour.from_rgb(lang['color'][0], lang['color'][1], lang['color'][2]),
                          title=lang['title'].format(member, data['level']),
                          description=lang['description'].format(data, data['level'] + 1,
                                                                 int(exp_to_next_level(data['totally_exp'])[0])))

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Ботам не дозволено робити це")

    @app_commands.command(
        name="exp"
    )
    @app_commands.describe(
        action="Дія",
        c_type_="Тип exp",
        member="Учасник",
        exp="Кількість exp",
        lvl="Рівень"
    )
    @app_commands.choices(
        action=[
            Choice(name="Додати", value="add"),
            Choice(name="Забрати", value="take"),
            Choice(name="Вказати", value="set"),
            Choice(name="Очистити", value="clear")
        ],
        c_type_=[
            Choice(name="Голосові", value="voice"),
            Choice(name="Текстові", value="text")
        ]
    )
    async def onExpExec(self, interaction: Interaction, action: str, c_type_: str, member: Member = None,
                        exp: float = 0.0, lvl: int = None):
        if not utils.isDM(interaction):
            return
        lang = utils.synchron_read_json("assets/messages/rank.json")
        if member is None:
            member = interaction.user

        user_data = await getRankData(self.bot, member)
        type_ = "text" if c_type_ == "text" else "voice"
        if lvl is None:
            if action == "add":
                await addExpData(self.bot, member, type_, user_data[type_ + "_xp"] + exp)
            elif action == "take":
                await setExpData(self.bot, member, exp=user_data[type_ + "_xp"] - exp, type_=c_type_)
            elif action == "set":
                await setExpData(self.bot, member, exp=exp, type_=c_type_)
            elif action == "clear":
                await setExpData(self.bot, member, exp=0, type_=c_type_)
        else:
            if action == "add":
                await addExpData(self.bot, member, type_, user_data[type_ + "_xp"] + level_to_exp(lvl))
            elif action == "take":
                await setExpData(self.bot, member, exp=user_data[type_ + "_xp"] - level_to_exp(lvl), type_=c_type_)
            elif action == "set":
                await setExpData(self.bot, member, exp=level_to_exp(lvl), type_=c_type_)
            elif action == "clear":
                await setExpData(self.bot, member, exp=0, type_=c_type_)

        await checkLevel(self.bot, member)
        await interaction.response.send_message(content=lang['expEdited'].format(member))

    @app_commands.command(
        name="levelrole",
        description="Nope."
    )
    @app_commands.describe(
        action="Дія",
        lvl="Рівень",
        role="Роль"
    )
    @app_commands.choices(
        action=[
            Choice(name="Замінити/Додати", value="edit"),
            Choice(name="Видалити", value="remove"),
            Choice(name="Список", value="list")
        ]
    )
    async def onLvlRoleExec(self, interaction: Interaction, action: str, lvl: int = 1, role: Role = None):
        if not utils.isDM(interaction):
            return
        edit_state = "normal"
        data = utils.synchron_read_json("assets/configs/rank.json")
        lang = utils.synchron_read_json("assets/messages/rank.json")
        if action == "edit":
            if role is not None:
                if data['lvlRoles'].get(str(lvl), False):
                    data['lvlRoles'][str(lvl)] = role.id
                else:
                    edit_state = "added"
                    data['lvlRoles'][str(lvl)] = role.id

                with open("assets/configs/rank.json", "w", encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                if edit_state == "normal":
                    await interaction.response.send_message(f"Роль для **{lvl}** рівня змінено")
                elif edit_state == "added":
                    await interaction.response.send_message(
                        f"Роль для **{lvl}** рівня змінено\n *Значення було додано.*")

        elif action == "remove":
            if str(lvl) in data['lvlRoles'].keys():
                data['lvlRoles'].pop(str(lvl))
                with open("assets/configs/rank.json", "w", encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                await interaction.response.send_message(f"Роль для **{lvl}** рівня видалено.")
            else:
                await interaction.response.send_message(f"На рівні **{lvl}** немає ролей.")

        elif action == "list":
            eb = Embed(color=Colour.from_rgb(lang['color'][0], lang['color'][1], lang['color'][2]),
                       title="Список ролей за рівні")
            text = []
            for lvl, role_id in data['lvlRoles'].items():
                text.append(f"<@&{role_id}> - {lvl} рівень")

            eb.description = '\n'.join(text)

            await interaction.response.send_message(embed=eb)

    @app_commands.command(
        name="top",
        description="See top 50 renk leaders"
    )
    async def onTopExec(self, interaction: Interaction):
        global_ranks = await getAllDB(self.bot)
        lang = utils.synchron_read_json("assets/messages/rank.json")
        eb = Embed(color=Colour.from_rgb(lang['color'][0], lang['color'][1], lang['color'][2]))
        eb.title = lang['topTitle']
        sorted_top = sorted(global_ranks, key=lambda x: x["totally_exp"], reverse=True)
        texts = []
        limit = 50
        for counter, user_object in enumerate(sorted_top):
            if counter >= limit:
                break
            texts.append(
                f"> {counter + 1}. <@{user_object['user']}> Ранг: {user_object['level']} *({user_object['text_xp']}/"
                f"{user_object['voice_xp']}/{user_object['totally_exp']})*")
        eb.description = '\n'.join(texts)
        await interaction.response.send_message(embed=eb)


async def setup(bot: Bot):
    await bot.add_cog(Rank2RankLoop(bot))
    await bot.add_cog(Rank2Commands(bot))
