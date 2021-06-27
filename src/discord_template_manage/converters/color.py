import discord

from .abstract import BaseConverter

class ColorConverter(BaseConverter):
    @classmethod
    def convert(cls, colour: discord.Colour):
        return '#{value:06x}'.format(value=colour.value)

    @classmethod
    def parse(cls, target: str) -> discord.Color:
        return discord.Color(int(target[1:], 16))