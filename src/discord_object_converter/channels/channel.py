from typing import Dict, List, Union, NewType, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

import discord
from discord import ChannelType
from discord import channel
from discord.channel import VoiceChannel

from ..abstract import (
    AbstractGuildChannelConverter, 
    AbstractTextChannelConverter, 
    AbstractStoreChannelConverter, 
    AbstractStageChannelConverter, 
    AbstractVoiceChannelConverter,
    AbstractCategoryChannelConverter,
    PartialDiscordModel,
    AbstractChannelConverterGetter
)

from ..voice_region import VoiceRegionConverter

class ConverterGetter(AbstractChannelConverterGetter):
    _channel_types: Dict[ChannelType, AbstractGuildChannelConverter] = {
    }
    @classmethod
    def get_converter(cls, channel: discord.abc.GuildChannel) -> Optional[AbstractGuildChannelConverter]:
        converter = cls._channel_types.get(channel.type)
        return converter

    @classmethod
    def get_parser(cls, channel_data: Dict) -> Optional[AbstractGuildChannelConverter]:
        for channel_type in cls._channel_types:
            converter = cls._channel_types[channel_type]
            if converter.channel_type == channel_data[converter.key_type]:
                return converter
        return None

AllChannelType = Union[discord.TextChannel, discord.VoiceChannel, discord.StoreChannel, discord.StageChannel]

@dataclass
class PartialGuildChannelModel(PartialDiscordModel):
    id_: int
    name: str
    position: int
    overwrites: discord.PermissionOverwrite
    type_: discord.ChannelType

class _GuildChannelSnowFlake(discord.abc.Snowflake, discord.abc.GuildChannel):
    pass

class _BaseChannelConverter(AbstractGuildChannelConverter):
    key_id = 'ID'
    key_name = 'チャンネル名'
    key_position = '位置'
    key_overwrites = '権限上書き'
    key_type = 'タイプ'

    channel_type = ''

    @classmethod
    def convert(cls, target: _GuildChannelSnowFlake):
        return {
            cls.key_id: str(target.id),
            cls.key_name: target.name,
            cls.key_position: target.position,
            cls.key_overwrites: target.overwrites,
            cls.key_type: cls.channel_type
        }

    @classmethod
    def parse(cls, target: Dict) -> PartialGuildChannelModel:
        raise NotImplementedError()

@dataclass
class PartialTextChannelModel(PartialGuildChannelModel):
    topic: Optional[str]
    nsfw: bool
    news: bool

class TextChannelConverter(AbstractTextChannelConverter, _BaseChannelConverter):
    key_topic = 'トピック'
    key_nsfw = 'NSFW設定'
    key_news = 'ニュースチャンネル設定'

    is_nsfw = is_news = 'はい'
    is_not_nsfw = is_not_news = 'いいえ'
    no_topic = 'なし'

    channel_type = 'テキストチャンネル'

    @classmethod
    def convert(cls, target: discord.TextChannel):
        common_data = super().convert(target)
        text_channel_data = {
            cls.key_topic: target.topic or cls.no_topic,
            cls.key_nsfw: cls.is_nsfw if target.is_nsfw() else cls.is_not_nsfw,
            cls.key_news: cls.is_not_news if target.is_news() else cls.is_not_news
        }
        common_data.update(text_channel_data)
        return common_data

    @classmethod
    def parse(cls, target: Dict) -> PartialTextChannelModel:
        id_ = int(target[cls.key_id])
        name: str = target[cls.key_name]
        position = int(target[cls.key_position])
        type_ = discord.ChannelType.text
        topic = target[cls.key_topic] if target[cls.key_topic] != cls.no_topic else None
        nsfw = target[cls.key_nsfw] == cls.is_nsfw
        news = target[cls.key_news] == cls.is_news

        return PartialTextChannelModel(id_, name, position, None, type_, topic, nsfw, news)

@dataclass
class PartialVoiceChannelModel(PartialGuildChannelModel):
    bitrate: int
    user_limit: Optional[int]
    rtc_region: Optional[discord.VoiceRegion]

class VoiceChannelConverter(AbstractVoiceChannelConverter, _BaseChannelConverter):
    key_bitrate = 'ビットレート'
    key_user_limit = 'ユーザー人数制限'
    key_rtc_region = '地域の上書き'

    channel_type = 'ボイスチャンネル'

    @classmethod
    def convert(cls, target: discord.VoiceChannel):
        common_data = super().convert(target)
        voice_channel_data = {
            cls.key_bitrate: target.bitrate,
            cls.key_user_limit: target.user_limit,
            cls.key_rtc_region: VoiceRegionConverter.convert(target.rtc_region)
        }
        common_data.update(voice_channel_data)
        return common_data

    @classmethod
    def parse(cls, target: Dict) -> PartialVoiceChannelModel:
        id_ = int(target[cls.key_id])
        name: str = target[cls.key_name]
        position = int(target[cls.key_position])
        type_ = discord.ChannelType.text
        bitrate = int(target[cls.key_bitrate])
        user_limit = int(target[cls.key_user_limit])
        rtc_region = VoiceRegionConverter.parse(target[cls.key_rtc_region])

        return PartialVoiceChannelModel(id_, name, position, None, type_, bitrate, user_limit, rtc_region)

@dataclass
class PartialStoreChannelModel(PartialGuildChannelModel):
    nsfw: bool

class StoreChannelConverter(AbstractStoreChannelConverter, _BaseChannelConverter):
    key_nsfw = 'NSFW設定'
    is_nsfw = 'はい'
    is_not_nsfw = 'いいえ'

    channel_type = 'ストアチャンネル'

    @classmethod
    def convert(cls, target: discord.StoreChannel):
        common_data = super().convert(target)
        store_channel_data = {
            cls.key_nsfw: cls.is_nsfw if target.is_nsfw() else cls.is_not_nsfw
        }
        common_data.update(store_channel_data)
        return common_data

    @classmethod
    def parse(cls, target: Dict) -> PartialVoiceChannelModel:
        id_ = int(target[cls.key_id])
        name: str = target[cls.key_name]
        position = int(target[cls.key_position])
        type_ = discord.ChannelType.text
        nsfw = target[cls.key_nsfw] == cls.is_nsfw
        return PartialVoiceChannelModel(id_, name, position, None, type_, nsfw)

@dataclass
class PartialStageChannelModel(PartialGuildChannelModel):
    topic: Optional[str]

class StageChannelConverter(AbstractStageChannelConverter, _BaseChannelConverter):
    key_topic = 'トピック'
    no_topic = 'なし'

    channel_type = 'ステージチャンネル'

    @classmethod
    def convert(cls, target: discord.StageChannel):
        common_data = super().convert(target)
        store_channel_data = {
            cls.key_topic: target.topic or cls.no_topic
        }
        common_data.update(store_channel_data)
        return common_data

    @classmethod
    def parse(cls, target: Dict) -> PartialStageChannelModel:
        id_ = int(target[cls.key_id])
        name: str = target[cls.key_name]
        position = int(target[cls.key_position])
        type_ = discord.ChannelType.text
        topic = target[cls.key_topic] if target[cls.key_topic] != cls.no_topic else None

        return PartialStageChannelModel(id_, name, position, None, type_, topic)

class ChildConverterGetter(ConverterGetter):
    _channel_types: Dict[ChannelType, AbstractGuildChannelConverter] = {
        ChannelType.text: TextChannelConverter,
        ChannelType.voice: VoiceChannelConverter,
        ChannelType.store: StoreChannelConverter,
        ChannelType.stage_voice: StageChannelConverter,
    }

@dataclass
class PartialCategoryChannelModel(PartialGuildChannelModel):
    nsfw: bool
    channels: List[PartialGuildChannelModel]

class CategoryChannelConverter(AbstractCategoryChannelConverter, _BaseChannelConverter):
    key_nsfw = 'NSFW設定'
    is_nsfw = 'はい'
    is_not_nsfw = 'いいえ'
    key_channels = 'カテゴリ内チャンネル'

    channel_type = 'カテゴリチャンネル'
    converter_getter = ChildConverterGetter

    @classmethod
    def convert(cls, target: discord.CategoryChannel):
        common_data = super().convert(target)
        
        child_data = list(map(lambda channel: cls.converter_getter.get_converter(channel).convert(channel), target.channels))

        category_channel_data = {
            cls.key_nsfw: cls.is_nsfw if target.is_nsfw() else cls.is_not_nsfw,
            cls.key_channels: child_data
        }

        common_data.update(category_channel_data)
        return common_data

    @classmethod
    def parse(cls, target: Dict) -> PartialCategoryChannelModel:
        id_ = int(target[cls.key_id])
        name: str = target[cls.key_name]
        position = int(target[cls.key_position])
        type_ = discord.ChannelType.text
        nsfw = target[cls.key_nsfw] == cls.is_nsfw
        channels = []

        for child in target[cls.key_channels]:
            parser: AbstractGuildChannelConverter = cls.converter_getter.get_parser(child)
            parse_result = parser.parse(child)
            channels.append(parse_result)

        return PartialCategoryChannelModel(id_, name, position, None, type_, nsfw, channels)