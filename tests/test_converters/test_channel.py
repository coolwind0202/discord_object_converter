import pytest
import discord

from src.discord_object_converter.channels.channel import TextChannelConverter, CategoryChannelConverter

@pytest.mark.asyncio
async def test_text_channel_default_converter(bot: discord.Client):
    test_guild: discord.Guild = bot.guilds[0]
    channel: discord.TextChannel = await test_guild.create_text_channel(name='New Text')
    convert_result = TextChannelConverter.convert(channel)
    assert convert_result['ID'] == channel.id
    assert convert_result['チャンネル名'] == 'New Text'

@pytest.mark.asyncio
async def test_category_channel_default_converter(bot: discord.Client):
    test_guild: discord.Guild = bot.guilds[0]
    await test_guild.create_category(name='New Category')
    convert_result = CategoryChannelConverter.convert(test_guild.categories[0])

    assert len(convert_result['カテゴリ内チャンネル']) == 0
    assert convert_result['NSFW設定'] == 'いいえ'

@pytest.mark.asyncio
async def test_text_channel_parser(bot: discord.Client):
    test_guild: discord.Guild = bot.guilds[0]
    convert_result = TextChannelConverter.convert(test_guild.text_channels[0])
    print(convert_result)
    assert False