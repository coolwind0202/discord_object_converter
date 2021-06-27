import pytest
import discord

from src.discord_template_manage.converters.voice_region import VoiceRegionConverter

@pytest.mark.asyncio
@pytest.mark.parametrize(('region', 'japanese_name'),[
    (discord.VoiceRegion.amsterdam, 'アムステルダム'),
    (discord.VoiceRegion.hongkong, '香港'),
    (discord.VoiceRegion.singapore, 'シンガポール')
])
async def test_voice_region_default_converter(region, japanese_name):
    assert japanese_name == VoiceRegionConverter.convert(region)