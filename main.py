import discord
from discord.ext import commands
import os
import asyncio
import secrets
from typing import Dict, Any, Optional
from pathlib import Path
import time

from aiohttp import web, ClientSession
from aiohttp_oauth2 import oauth2_app
from aiohttp_oauth2.client.contrib import github
from aiohttp_session import SimpleCookieStorage, get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_remotes import XForwardedRelaxed, setup as forward_setup

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
bot = commands.Bot(command_prefix=os.getenv('DISCORD_BOT_PREFIX', 'template-'), loop=loop)

import jinja2
from aiohttp_jinja2 import setup as jinja2_setup, template
from aiohttp_session import SimpleCookieStorage, get_session, setup as session_setup


from aiohttp_oauth2.client.contrib import github

class RedirectableStorage(EncryptedCookieStorage):
    def save_cookie(
        self,
        response: web.StreamResponse,
        cookie_data: str, *,
        max_age: Optional[int] = None
    ) -> None:
        params = self._cookie_params.copy()
        params['secure'] = True
        params['samesite'] = 'None'
        if max_age is not None:
            params['max_age'] = max_age
            t = time.gmtime(time.time() + max_age)
            params["expires"] = time.strftime("%a, %d-%b-%Y %T GMT", t)
        if not cookie_data:
            response.del_cookie(self._cookie_name, domain=params["domain"],
                                path=params["path"])
        else:
            # Ignoring type for params until aiohttp#4238 is released
            response.set_cookie(self._cookie_name, cookie_data, **params)  # type: ignore

@template("github_oauth.html")
async def index(request: web.Request) -> Dict[str, Any]:
    return {}

async def app_factory():
    app = web.Application()

    app = web.Application()
    jinja2_setup(app, loader=jinja2.FileSystemLoader(Path(__file__).parent / 'web/templates'))
    setup(app, RedirectableStorage(max_age=600))

    app['sessions'] = {}
    app['github_tokens'] = {}

    await forward_setup(app, XForwardedRelaxed())

    def get_session_id():
        return secrets.token_hex()

    async def on_discord_login(request: web.Request, discord_token: str):
        session = await get_session(request)
        print(session)
        session_id = get_session_id()
        app['sessions'][session_id] = discord_token
        session['session_id'] = session_id

        #print(app['sessions'])
        print(session)

        return web.HTTPTemporaryRedirect(location="/github/auth")

    async def on_github_login(request: web.Request, github_token: str):
        session = await get_session(request)
        print(session)
        session_id = session.get('session_id')
        if session_id is None:
            return web.HTTPTemporaryRedirect(location="/discord/auth")

        discord_token = app['sessions'][session_id]  #  Discord　トークンを利用する
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + discord_token['access_token']
        }
        async with ClientSession(headers=headers) as session:
            async with session.get('https://discord.com/api/v8/users/@me/') as resp:
                discord_id = int(resp['id'])
                app['github_tokens'][discord_id] = github_token

        print(app['github_tokens'])

        return web.HTTPTemporaryRedirect(location="/")

    app.add_subapp(
        '/discord/',
        oauth2_app(
            client_id=os.getenv('DISCORD_CLIENT_ID'),
            client_secret=os.getenv('DISCORD_CLIENT_SECRET'),
            authorize_url='https://discord.com/api/oauth2/authorize',
            token_url='https://discord.com/api/oauth2/token',
            scopes=["identify"],
            on_login=on_discord_login,
            json_data=False
        )
    )
    app.add_subapp(
        '/github/',
        github(
            os.getenv('GITHUB_CLIENT_ID'),
            os.getenv('GITHUB_CLIENT_SECRET'),
            scopes=['admin:repo_hook'],
            on_login=on_github_login
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
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 3000)))
    await site.start()

loop.create_task(app_start())
loop.create_task(bot.start(
    os.getenv('DISCORD_BOT_TOKEN')
))
asyncio.get_event_loop().run_forever()