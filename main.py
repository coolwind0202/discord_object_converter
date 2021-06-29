import aiohttp_jinja2
import discord
from discord.ext import commands
import os
import asyncio
import secrets
from typing import Dict, Any, Optional, Union
from pathlib import Path
import time
import base64

from aiohttp import web, ClientSession
from aiohttp_oauth2 import oauth2_app
from aiohttp_oauth2.client.contrib import github
from aiohttp_session import SimpleCookieStorage, get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_remotes import XForwardedRelaxed, setup as forward_setup
from cryptography import fernet

loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
bot = commands.Bot(command_prefix=os.getenv('DISCORD_BOT_PREFIX', 'template-'), loop=loop)

import jinja2
from aiohttp_jinja2 import setup as jinja2_setup, template
from aiohttp_session import SimpleCookieStorage, AbstractStorage, get_session, new_session, setup as session_setup
from aiohttp.web_middlewares import _Handler, _Middleware

from aiohttp_oauth2.client.contrib import github

def session_middleware(storage: 'AbstractStorage') -> _Middleware:
    if not isinstance(storage, AbstractStorage):
        raise RuntimeError("Expected AbstractStorage got {}".format(storage))

    @web.middleware
    async def factory(
        request: web.Request,
        handler: _Handler
    ) -> web.StreamResponse:
        SESSION_KEY = 'aiohttp_session'
        STORAGE_KEY = 'aiohttp_session_storage'
        request[STORAGE_KEY] = storage
        raise_response = False
        # TODO aiohttp 4: Remove Union from response, and drop the raise_response variable
        response: Union[web.StreamResponse, web.HTTPException]
        try:
            print('call handler')
            response = await handler(request)
            print('called handler', response)
        except web.HTTPException as exc:
            response = exc
            raise_response = True
        if not isinstance(response, (web.StreamResponse, web.HTTPException)):
            raise RuntimeError(
                "Expect response, not {!r}".format(type(response)))
        if not isinstance(response, (web.Response, web.HTTPException)):
            # likely got websocket or streaming
            return response
        if response.prepared:
            raise RuntimeError(
                "Cannot save session data into prepared response")
        session = request.get(SESSION_KEY)
        print(session)
        if session is not None:
            if session._changed:
                await storage.save_session(request, response, session)
        if raise_response:
            #raise cast(web.HTTPException, response)
            pass
        return response

    return factory

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
            
            #response.cookies[self._cookie_name] = cookie_data
        #print(response.cookies)

@template("github_oauth.html")
async def index(request: web.Request) -> Dict[str, Any]:
    return {}

async def app_factory():
    app = web.Application()

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    jinja2_setup(app, loader=jinja2.FileSystemLoader(Path(__file__).parent / 'web/templates'))
    storage = RedirectableStorage(secret_key, max_age=600)
    # setup(app, storage)
    app.middlewares.append(session_middleware(storage))

    app['sessions'] = {}
    app['github_tokens'] = {}

    await forward_setup(app, XForwardedRelaxed())

    def get_session_id():
        return secrets.token_hex()

    async def on_discord_login(request: web.Request, discord_token: str):
        #session = await get_session(request)
        session = await new_session(request)
        print("before:",session)
        session_id = get_session_id()
        print(request.app['session'])
        #request.app['session'][session_id] = discord_token
        app['sessions'][session_id] = discord_token

        session['session_id'] = session_id
        

        #print(app['sessions'])
        print("after:",session)

        return aiohttp_jinja2.render_template('github_oauth.html', request, None)

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