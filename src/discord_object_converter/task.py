import discord

from .abstract import BaseTask

class GuildEditTask(BaseTask):
    def __init__(self, guild: discord.Guild, name):
        self.guild = guild
        self.name = name

    async def execute(self):
        await self.guild.edit(name=self.name)

class RoleAddTask(BaseTask):
    def __init__(self, guild: discord.Guild, *, name: str, permissions: discord.Permissions, colour: discord.Colour, hoist: bool, mentionable: bool):
        self.guild = guild
        self.args = {
            name: name,
            permissions: permissions,
            colour: colour,
            hoist: hoist,
            mentionable: mentionable
        }

    async def execute(self):
        await self.guild.create_role(**self.args)

class RoleRemoveTask(BaseTask):
    def __init__(self, role: discord.Role):
        self.role = role

    async def execute(self):
        await self.role.delete()

class RoleEditTask(BaseTask):
    def __init__(self, role: discord.Role, *, name: str, permissions: discord.Permissions, colour: discord.Colour, hoist: bool, mentionable: bool):
        self.role = role
        self.args = {
            name: name,
            permissions: permissions,
            colour: colour,
            hoist: hoist,
            mentionable: mentionable
        }

    async def execute(self):
        await self.role.edit(*self.args)

class CategoryChannelAddTask(BaseTask):
    def __init__(self, guild: discord.Guild, *, args):
        self.guild = guild
        self.args = args

    async def execute(self):
        await self.guild.create_category_channel(*self.args)

class ChildChannelAddTask(BaseTask):
    def __init__(self, guild: discord.Guild, type: discord.ChannelType, *, args):
        self.guild = guild
        self.args = args
        self.type_ = type

    async def execute(self):
        if self.type_ is discord.ChannelType.text:
            await self.guild.create_text_channel(*self.args)
        elif self.type_ is discord.ChannelType.voice:
            await self.guild.create_voice_channel(*self.args)
        elif self.type_ is discord.ChannelType.store:
            await self.guild.create_stage_channel(*self.args)

    #  Store Channelは作成できない

class ChannelRemoveTask(BaseTask):
    def __init__(self, channel: discord.abc.GuildChannel):
        self.channel = channel

    async def execute(self):
        await self.channel.delete()