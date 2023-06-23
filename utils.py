import json
import aiofiles
from discord import Interaction, Member


async def read_json(file: str):
    async with aiofiles.open(file, "r", encoding='utf-8') as f:
        content = await f.read()
        return json.loads(content)


async def check_blocked_role(author: Member):
    data = synchron_read_json("assets/configs/rank.json")["roleIdsBlackList"]
    user_roles = []
    for roleObj in author.roles:
        user_roles.append(roleObj.id)
    for id_ in data:
        if id_ in user_roles:
            return True
    return False


async def check_blocked_channel(channel):
    data = synchron_read_json("assets/configs/rank.json")["roleIdsBlackList"]
    for id_ in data:
        if channel.id == id_:
            return True
    return False


def synchron_read_json(file: str):
    with open(file, "r", encoding='utf-8') as f:
        return json.load(f)


def checkDev(userId, devsId):
    for devId in devsId:
        if devId == userId:
            return devId
    return None


def isDM(interaction: Interaction):
    if interaction.guild is None:
        return False
    else:
        return True
