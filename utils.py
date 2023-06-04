import json
import aiofiles
from discord import Interaction


async def read_json(file: str):
    async with aiofiles.open(file, "r", encoding='utf-8') as f:
        content = await f.read()
        return json.loads(content)


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
