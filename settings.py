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

import typing
import enum
import asyncio
import abc
import re
import sys
import ssl

import toml
import json


VERSION = "0.2.2"
SERVER_NAME = "WebServer"


class ServerType(enum.Enum):
    STATIC = "static"
    WSGI = "wsgi"
    CGI = "cgi"
    FAST_CGI = "fast-cgi"


class TlsSetting:
    def __init__(self, data: typing.Dict[str, typing.Any]):
        self.__port = data["port"]
        self.__chain = data["chain"]
        self.__key = data["key"]
        self.__redirect = data["redirect"]

    @property
    def port(self):
        return self.__port

    @property
    def chain(self):
        return self.__chain

    @property
    def key(self):
        return self.__key

    @property
    def context(self):
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(self.chain, keyfile=self.key)

        return ctx


class ServerSetting(abc.ABC):
    def __init__(self, data: typing.Dict[str, typing.Any]):
        self.__host = data["host"]
        self.__port = int(data["port"])
        self.__type = ServerType(data["type"])

        if "tls" in data:
            self.__tls = TlsSetting(data["tls"])
            self.__context = self.__tls.context
        else:
            self.__tls = None
            self.__context = None

        hide_version = True
        if "options" in data:
            options = data["options"]
            if "version" in options:
                hide_version = options["version"]

        self.__headers = {"server": "{}{}".format(SERVER_NAME, " " + VERSION if hide_version else "")}
        if "headers" in data:
            headers = data["headers"]
            if isinstance(headers, list):
                self.__headers.update(
                    {h[0].lower().strip(): h[1].strip() for h in [h.split(":") for h in headers]}
                )

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def type(self) -> ServerType:
        return self.__type

    @abc.abstractmethod
    async def build(self, loop: asyncio.AbstractEventLoop):
        pass

    @property
    def headers(self) -> typing.Dict[str, str]:
        return self.__headers

    @property
    def context(self):
        return self.__context

    @property
    def tls(self):
        return self.__tls


class WsgiServerSetting(ServerSetting):
    def __init__(self, data: typing.Dict[str, typing.Any]):
        super(WsgiServerSetting, self).__init__(data)
        self.__script = data["script"]
        self.__script = re.sub("(\.py|\.pyc)$", "", self.__script)

        if "object" in data:
            self.__object = data["object"]
        elif "app" in data:
            self.__object = data["app"]
        else:
            raise RuntimeError("WSGI object (app) not specified in setting file.")
        self.__package = data["package"]

    @property
    def script(self) -> str:
        return self.__script

    @property
    def object(self) -> str:
        return self.__object

    @property
    def package(self) -> str:
        return self.__package

    async def build(self, loop: asyncio.AbstractEventLoop):
        import core
        await core.setup_server(loop, core.wsgi_server(self),
                                self.host, self.port, self.context)


class StaticServerSetting(ServerSetting):
    def __init__(self, data: typing.Dict[str, typing.Any]):
        super(StaticServerSetting, self).__init__(data)
        self.__root = data["root"]

        self.__index = "index.html"
        if "index" in data:
            self.__index = data["index"]

        self.__completion = None
        if "completion" in data:
            self.__completion = data["completion"]
            if not self.__completion.startswith("."):
                self.__completion = "." + self.__completion

    @property
    def root(self) -> str:
        return self.__root

    @property
    def index(self):
        return self.__index

    @property
    def completion(self):
        return self.__completion

    async def build(self, loop: asyncio.AbstractEventLoop):
        import core
        await core.setup_server(loop, core.static_server(self),
                                self.host, self.port, self.context)


def __load_object(file: str) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
    with open(file) as fp:
        if file.endswith(".toml") or file.endswith(".tml"):
            return toml.load(fp)
        if file.endswith(".json"):
            return json.load(fp)
        raise RuntimeError("unsupported file type. .toml(.tml) and .json are supported")


def __load_impl(file: str) -> typing.List[ServerSetting]:
    setting = []
    try:
        objs = __load_object(file)
        for obj in objs.values():
            stype = ServerType(obj["type"])
            if stype == ServerType.WSGI:
                setting.append(WsgiServerSetting(obj))
            if stype == ServerType.STATIC:
                setting.append(StaticServerSetting(obj))
    except Exception as e:
        print("exception raised: {}".format(e), file=sys.stderr)
    return setting


def load(path: typing.Union[str, typing.List[str]]) -> typing.List[ServerSetting]:
    if isinstance(path, str):
        path = [path]

    setting = []
    [setting.extend(s) for s in [__load_impl(p) for p in path] if s is not None]
    return setting
