from discord import ChannelType, TextChannel, VoiceChannel, CategoryChannel
import discord

async def modify_channel(cache: discord.abc.GuildChannel, current: discord.abc.GuildChannel):
    """テンプレート上のチャンネル情報と現在のチャンネル情報を比較し、異なる部分に対しては修正を行う。
    cache と current の name　属性は一致している必要がある。

    Args:
        cache (discord.abc.GuildChannel): テンプレート上のチャンネル情報。
        current (discord.abc.GuildChannel): 現在のDiscordサーバーにおけるチャンネル情報
    """

    pass