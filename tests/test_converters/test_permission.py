import pytest
import discord
from src.discord_object_converter.converters.abstract import AbstractPermissionConverter
from src.discord_object_converter.converters.permission import PermissionConverter

@pytest.mark.asyncio
@pytest.mark.parametrize(('key', 'value'), [
    ('リアクションの追加', 'OK'),
    ('管理者', 'NG'),
    ('埋め込みリンク', 'OK')
])
async def test_permission_converter(key, value):
    perm = discord.Permissions(permissions=1275879617)
    convert_result = PermissionConverter.convert(perm)
    assert convert_result[key] == value