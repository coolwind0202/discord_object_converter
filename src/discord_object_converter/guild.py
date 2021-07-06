from dataclasses import dataclass
from typing import Dict, Optional, List

import discord

from .abstract import AbstractGuildConverter, PartialDiscordModel
from .role import PartialRoleModel, RoleConverter
from .channels.channel import PartialCategoryChannelModel, PartialGuildChannelModel
from .channels.getter import ChannelConverterGetter
from . import task

@dataclass
class PartialGuildModel(PartialDiscordModel):
    name: Optional[str]
    channels: List[PartialGuildChannelModel]
    roles: List[PartialRoleModel]

    def get_tasks(self, real_guild: discord.Guild) -> List[task.BaseTask]:
        tasks = []
        if real_guild.name != self.name:
            tasks.append(task.GuildEditTask(real_guild, self.name))  #  現在のチャンネル名と異なるのでチャンネル名編集のタスクを追加する

        for role_data in self.roles:
            role: discord.Role = real_guild.get_role(role_data.id_)
            
            if role is None:
                tasks.append(task.RoleAddTask(
                    real_guild, 
                    name=role_data.name,
                    permissions=role_data.permissions,
                    colour=role_data.colour,
                    hoist=role_data.hoist,
                    mentionable=role_data.mentionable,
                ))  #  現在のギルドに同一IDのロールが存在しないので、追加する
                continue

            real_role_data = RoleConverter.parse(RoleConverter.convert(role))
            if real_role_data == role_data:
                continue  #  同一なので、編集する必要がない

            def get_data(data, real_data):
                return data if data is not None else real_data

            name: str = get_data(role_data.name, role.name)  #  ロール名は指定されていないければ現在の名前を使用する
            permissions: discord.Permissions = get_data(role_data.permissions, role.permissions)
            colour: discord.Colour = get_data(role_data.colour, role.colour)
            hoist: bool = get_data(role_data.hoist, role.hoist)
            mentionable: bool = get_data(role_data.mentionable, role.mentionable)
            
            tasks.append(task.RoleEditTask(
                role,
                name=name,
                permissions=permissions,
                colour=colour,
                hoist=hoist,
                mentionable=mentionable
            ))  #  現在のギルドに同一IDのロールが存在するので、編集する

        for role in real_guild.roles:
            role_data: Optional[PartialRoleModel] = discord.utils.get(self.roles, id_=role.id)
            if role_data is None:
                tasks.append(task.RoleRemoveTask(role))  #  設定ファイルに同一IDのロールが存在しないので、削除する

        for channel_data in self.channels:
            channel: Optional[discord.abc.GuildChannel] = real_guild.get_channel(channel_data.id_)
            if channel is None:
                pass  #  現在のギルドに同一IDのチャンネルが存在しないので、追加する
        
        for channel in real_guild.channels:
            channel_data: Optional[PartialGuildChannelModel] = discord.utils.get(self._flatted_channels, id_=channel.id)
            if channel_data is None:
                tasks.append(task.ChannelRemoveTask(channel))  #  設定ファイルに同一IDのチャンネルが存在しないので、削除する

        return tasks

    @property
    def _flatted_channels(self) -> List[PartialGuildChannelModel]:
        flatted = []
        for channel in self.channels:
            if channel.type_ == discord.ChannelType.category:
                category: PartialCategoryChannelModel = channel
                flatted.append(category)
                flatted += category.channels
            else:
                flatted.append(channel)
        return flatted


class GuildConverter(AbstractGuildConverter):
    key_id = 'ID'
    key_name = 'サーバー名'
    key_channels = 'チャンネル'
    key_roles = 'ロール'

    @classmethod
    def convert(cls, target: discord.Guild):
        channels = []
        for channel in target.channels:
            if channel.category_id is not None:
                continue  #  親が存在するので無視
            
            channels.append(ChannelConverterGetter.get_converter(channel).convert(channel))
        
        roles = []
        for role in target.roles:
            roles.append(RoleConverter.convert(role))

        return {
            cls.key_id: str(target.id),
            cls.key_name: target.name,
            cls.key_channels: channels,
            cls.key_roles: roles
        }

    @classmethod
    def parse(cls, target: Dict) -> PartialGuildModel:
        name = target[cls.key_name]
        roles_data: List[PartialRoleModel] = list(map(lambda role: RoleConverter.parse(role), target[cls.key_roles]))
        channels = list(map(lambda channel: ChannelConverterGetter.get_parser(channel).parse(channel), target[cls.key_channels]))

        return PartialGuildModel(name=name, roles=roles_data, channels=channels)