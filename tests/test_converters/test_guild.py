from discord import colour
import pytest
import discord

from src.discord_object_converter.guild import GuildConverter

@pytest.mark.asyncio
async def test_guild_default_converter(bot: discord.Client):
    test_guild: discord.Guild = bot.guilds[0]
    convert_result = GuildConverter.convert(test_guild)
    assert convert_result['サーバー名'] == 'Test Guild 0'

@pytest.mark.asyncio
async def test_guild_parser(bot: discord.Client):
    test_guild: discord.Guild = bot.guilds[0]
    convert_result_1 = GuildConverter.convert(test_guild)
    parse_result_1 = GuildConverter.parse(convert_result_1)
    assert len(parse_result_1.roles) == 1
    assert parse_result_1.name == 'Test Guild 0'

    await test_guild.create_role(name='New Role', colour=discord.Colour.red(), hoist=True)
    await test_guild.create_text_channel(name='New Channel')
    convert_result_2 = GuildConverter.convert(test_guild)
    parse_result_2 = GuildConverter.parse(convert_result_2)
    assert len(parse_result_2.roles) == 2
    assert parse_result_2.roles[1].colour.value == discord.Colour.red().value
    assert parse_result_2.roles[1].hoist is True
    print(parse_result_2)
    print(parse_result_1.get_tasks(test_guild))
    assert False


@pytest.mark.asyncio
async def test_guild_get_tasks(bot: discord.Client):
    test_guild: discord.Guild = bot.guilds[0]
    convert_result = GuildConverter.convert(test_guild)
    parse_result = GuildConverter.parse(convert_result)
    await test_guild.create_role(name='New Role', colour=discord.Colour.red(), hoist=True)

    print(parse_result.get_tasks(test_guild)[0].role)
    assert False
