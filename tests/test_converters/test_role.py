from typing import List
from discord import mentions
import pytest
import discord.ext.test as dpytest
import discord

from src.discord_object_converter.abstract import AbstractRoleConverter
from src.discord_object_converter.role import RoleConverter

class _TestRoleConfig(AbstractRoleConverter):
    @classmethod
    def convert(cls, target: discord.Role):
        return {
            '[Role Name]': target.name,
            '[Role Hoist]': target.hoist
        }

class _TestFakeConfig:
    def __init__(self, x, y):
        self.sum = x + y

@pytest.mark.asyncio
async def test_role_default_converter(bot: discord.Client):
    test_guild: discord.Guild = bot.guilds[0]
    await test_guild.create_role(name='Other')
    role: discord.Role = await test_guild.create_role(name='Role newer', permissions=discord.Permissions(8), mentionable=True)

    convert_result = RoleConverter.convert(role)
    assert convert_result['ロール名'] == 'Role newer'
    assert convert_result['@mention を許可する'] == 'はい'

@pytest.mark.asyncio
async def test_role_custom_converter(bot: discord.Client):
    test_guild: discord.Guild = bot.guilds[0]
    role: discord.Role = await test_guild.create_role(name='Role newer', hoist=True)
    convert_result = _TestRoleConfig.convert(role)
    assert convert_result == { '[Role Name]': 'Role newer', '[Role Hoist]': True }
