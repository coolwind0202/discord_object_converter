from typing import Dict, Optional

import discord
from discord import ChannelType

from .channel import (
    AbstractGuildChannelConverter,
    TextChannelConverter,
    VoiceChannelConverter,
    StoreChannelConverter,
    StageChannelConverter,
    CategoryChannelConverter,
    ConverterGetter
)

class ChannelConverterGetter(ConverterGetter):
    _channel_types: Dict[ChannelType, AbstractGuildChannelConverter] = {
        ChannelType.text: TextChannelConverter,
        ChannelType.voice: VoiceChannelConverter,
        ChannelType.store: StoreChannelConverter,
        ChannelType.stage_voice: StageChannelConverter,
        ChannelType.category: CategoryChannelConverter
    }