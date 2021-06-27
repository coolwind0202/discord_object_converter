import discord
from typing import Optional

from .abstract import AbstractVoiceRegionConverter

class VoiceRegionConverter(AbstractVoiceRegionConverter):
    no_region = '自動'
    undefined_region = '不明'

    amsterdam = 'アムステルダム'
    brazil = 'ブラジル'
    dubai = 'ドバイ'
    eu_central = '中央ヨーロッパ'
    eu_west = '西ヨーロッパ'
    europe = 'ヨーロッパ'
    frankfurt = 'フランクフルト'
    hongkong = '香港'
    india = 'インド'
    japan = '日本'
    london = 'ロンドン'
    russia = 'ロシア'
    singapore = 'シンガポール'
    south_korea = '韓国'
    southafrica = '南アフリカ'
    sydney = 'シドニー'
    us_central = 'アメリカ中部'
    us_east = 'アメリカ東部'
    us_south = 'アメリカ南部'
    us_west = 'アメリカ西部'
    vip_amsterdam = 'VIPアムステルダム'
    vip_us_east = 'VIPアメリカ東部'
    vip_us_west = 'VIPアメリカ西部'

    @classmethod
    def convert(cls, target: Optional[discord.VoiceRegion]) -> str:
        if target is None:
            return cls.no_region

        for region in discord.VoiceRegion:
            if target is region:
                region_japanese_name: Optional[str] = getattr(cls, region.name, None)
                if region_japanese_name is None:
                    continue

                return region_japanese_name
        else:
            return cls.undefined_region

    @classmethod
    def parse(cls, target: str) -> str:
        for region_name in dir(cls):
            if region_name.startswith('_'):
                continue

            region_japanese_name = getattr(cls, region_name, None)
            if region_japanese_name == target:
                return region_name
        return cls.undefined_region