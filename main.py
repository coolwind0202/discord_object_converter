import discord
from discord.ext import commands
import os
import asyncio

from aiohttp import web
from aiohttp_oauth2.client.contrib import github

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
bot = commands.Bot(command_prefix=os.getenv('DISCORD_BOT_PREFIX', 'template-'), loop=loop)

async def login_handler(r, code):
    print(r,code)

async def app_factory():
    app = web.Application()
    app.add_subapp(
        '/github/',
        github(
            os.getenv('GITHUB_CLIENT_ID'),
            os.getenv('GITHUB_CLIENT_SECRET'),
            scopes=['admin:repo_hook'],
            on_login=login_handler
        ),
    )

    return app

@bot.event
async def on_ready():
    data = await bot.http.get_template('smpCDBRk5nqk')

    data['serialized_source_guild']['id'] = data['source_guild_id']
    guild = discord.Guild(data=data['serialized_source_guild'], state=bot._connection)

    
    print(guild.text_channels)

async def app_start():
    app = await app_factory()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 3000)))
    await site.start()

loop.create_task(app_start())
loop.create_task(bot.start(
    os.getenv('DISCORD_BOT_TOKEN')
))
asyncio.get_event_loop().run_forever()