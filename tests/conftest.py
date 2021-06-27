import pytest
import discord.ext.test as dpytest
import discord

import sys 
import os

#sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/.../src/"))

@pytest.fixture
def bot(event_loop):
    bot = discord.Client(loop=event_loop)
    dpytest.configure(bot)
    return bot
