from pathlib import Path
from typing import Any, Dict
import os
import asyncio

import jinja2
from aiohttp import web
from aiohttp_jinja2 import setup as jinja2_setup, template
from aiohttp_session import SimpleCookieStorage, get_session, new_session, setup as session_setup
from aiohttp_remotes import XForwardedRelaxed, setup as forward_setup

#from aiohttp_oauth2.client.contrib import github
from aioauth_client import GithubClient, DiscordClient


@template("index.html")
async def index(request: web.Request) -> Dict[str, Any]:
    session = await get_session(request)
    return {"user": session.get("user")}
    #return { "user": None } 

@template("github_oauth.html")
async def github(request):
    github = GithubClient(
        client_id='4f92b96e7fd001b6f957',
        client_secret='bccaf8f76fb8e4fd1c6d0ebfb1e0348a6a3d8674',
    )
    if 'code' not in request.url.query:
        return web.HTTPTemporaryRedirect(github.get_authorize_url(scope='user:email'))

    # Get access token
    code = request.url.query['code']
    token, _ = await github.get_access_token(code)
    assert token

    # Get a resource `https://api.github.com/user`
    response = await github.request('GET', 'user')
    print(response)
    session = await new_session(request)
    session['username'] = response
    return {}

async def logout(request: web.Request):
    session = await get_session(request)
    session.invalidate()
    return web.HTTPTemporaryRedirect(location="/")


async def on_github_login(request: web.Request, github_token):
    session = await get_session(request)

    async with request.app["session"].get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {github_token['access_token']}"},
    ) as r:
        session["user"] = await r.json()

    return web.HTTPTemporaryRedirect(location="/")


def app_factory() -> web.Application:
    app = web.Application()

    jinja2_setup(
        app, loader=jinja2.FileSystemLoader([Path(__file__).parent / "web/templates"])
    )
    session_setup(app, SimpleCookieStorage())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(forward_setup(app, XForwardedRelaxed()))

    app.add_routes([web.get("/", index), web.get("/github/", github), web.get("/auth/logout", logout)])

    return app


if __name__ == "__main__":
    web.run_app(app_factory(), host="0.0.0.0", port=int(os.getenv('PORT')))
    #web.run_app(app_factory(), host="127.0.0.1", port=3000)