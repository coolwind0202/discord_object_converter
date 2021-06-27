from typing import Dict, Optional
from dataclasses import dataclass

import discord

from .abstract import AbstractRoleConverter, PartialDiscordModel
from .permission import PermissionConverter
from .color import ColorConverter

@dataclass
class PartialRoleModel(PartialDiscordModel):
    id_: int
    name: Optional[str]
    permissions: Optional[discord.Permissions]
    colour: Optional[discord.Colour]
    hoist: Optional[bool]
    mentionable: Optional[bool]

class RoleConverter(AbstractRoleConverter):
    is_hoist = is_mentionable = 'はい'
    is_not_hoist = is_not_mentionable = 'いいえ'

    key_id = 'ID'
    key_name = 'ロール名'
    key_colour = 'カラー'
    key_hoist = 'ロールメンバーを表示する'
    key_mentionable = '@mention を許可する'
    key_permissions = '権限'

    permission_converter = PermissionConverter
    color_converter = ColorConverter

    @classmethod
    def convert(cls, target: discord.Role):
        result = {
            cls.key_id: str(target.id),
            cls.key_name: target.name,
            cls.key_colour: cls.color_converter.convert(target.colour),
            cls.key_hoist: cls.is_hoist if target.hoist else cls.is_not_hoist,
            cls.key_mentionable: cls.is_mentionable if target.mentionable else cls.is_not_mentionable,
            cls.key_permissions: cls.permission_converter.convert(target.permissions)
        }
        return result

    @classmethod
    def parse(cls, target: Dict) -> PartialRoleModel:
        id_ = int(target[cls.key_id])
        name: str = target[cls.key_name]
        colour = cls.color_converter.parse(target[cls.key_colour])
        permissions = cls.permission_converter.parse(target[cls.key_permissions])
        hoist: bool = target[cls.key_hoist] == cls.is_hoist
        mentionable: bool = target[cls.key_mentionable] == cls.is_mentionable

        return PartialRoleModel(id_=id_, name=name, colour=colour, permissions=permissions, hoist=hoist, mentionable=mentionable)