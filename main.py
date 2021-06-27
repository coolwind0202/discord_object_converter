import discord
from discord.ext import commands
import os
import asyncio

from aiohttp import web
from aiohttp_oauth2 import oauth2_app


bot = commands.Bot(command_prefix=os.getenv('DISCORD_BOT_PREFIX', 'template-'))

def login_handler(r, code):
    print(r,code)

async def app_factory():
    app = web.Application()

    app.add_subapp(
        '/github/',  # any arbitrary prefix
        oauth2_app(
            client_id=os.getenv('GITHUB_CLIENT_ID'),
            client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
            authorize_url='https://github.com/login/oauth/authorize',
            token_url='https://github.com/login/oauth/access_token',
            scopes=['admin:repo_hook'],
            on_login=login_handler
        )
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
    site = web.TCPSite(runner, '0.0.0.1', 8080)
    await site.start()


asyncio.run(asyncio.gather((os.getenv('DISCORD_BOT_TOKEN')), app_start()))