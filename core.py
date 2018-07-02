#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Copyright 2018 SiLeader and Cerussite.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import asyncio
import sys
import importlib
import re
import pathlib

from aiohttp import web

import settings


async def setup_server(loop: asyncio.AbstractEventLoop, server,
                       host: str, port: int, ssl_context):
    ws = web.Server(server)
    await loop.create_server(ws, host, port, ssl=ssl_context)


async def idle(loop: asyncio.AbstractEventLoop):
    await asyncio.sleep(100, loop=loop)


async def wsgi_core(req: web.Request, app, setting: settings.ServerSetting):
    host = req.host
    if ":" in host:
        host = [h.strip() for h in host.split(":")]
        port = int(host[1])
        host = host[0]
    else:
        port = 443 if req.secure else 80

    environ = {
        "REQUEST_METHOD": req.method,
        "SCRIPT_NAME": "",
        "PATH_INFO": req.path,
        "QUERY_STRING": req.query_string,
        "CONTENT_TYPE": req.content_type,
        "CONTENT_LENGTH": req.content_length,
        "SERVER_NAME": host,
        "SERVER_PORT": port,
        "SERVER_PROTOCOL": req.protocol,

        "wsgi.version": (1, 0),
        "wsgi.url_scheme": req.scheme,
        "wsgi.input": req.content,
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": True,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False
    }

    res = []

    def start_response(status, headers):
        reason = None
        if " " in status:
            status = status.split(" ")
            reason = status[1]
            status = int(status[0])
        else:
            status = int(status)
        headers = {k: v for k, v in headers}
        headers.update(setting.headers)
        res.append(web.StreamResponse(status=status, reason=reason, headers=headers))

    async def response_wrapper():
        output = app(environ, start_response)
        await res[0].prepare(request=req)
        [await res[0].write(w) for w in output]
        await res[0].drain()

    await response_wrapper()
    return res[0]


def static_server(setting: settings.StaticServerSetting):
    async def server(req: web.Request):
        path = req.path
        if path.endswith("/"):
            path += setting.index

        if setting.completion is not None:
            if re.match("\w+\.\w+$", path) is None:
                path += setting.completion

        path = setting.root + "/" + path
        if pathlib.Path(path).exists():
            return web.FileResponse(path, headers=setting.headers)

        return web.Response(status=404, text="404 not found", headers=setting.headers)
    return server


def wsgi_server(setting: settings.WsgiServerSetting):
    sys.path.append(setting.package)
    mod = importlib.import_module(setting.script)
    obj = getattr(mod, setting.object)

    async def server(req: web.Request):
        return await wsgi_core(req, obj, setting)
    return server


def ssl_redirect_server(setting: settings.ServerSetting):
    async def server(req: web.Request):
        headers = setting.headers
        headers["location"] = "https://{}:{}/{}".format(
            setting.host, setting.tls.port, req.raw_path
        )
        return web.Response(status=301, headers=headers)

    return server
