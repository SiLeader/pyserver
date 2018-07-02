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


def wsgi_server(environ, start_response):
    print("wsgi 1")
    start_response("200 OK", [("content-type", "application/json")])
    print("wsgi 2")
    return [b'{"abc":0}']


"""
import json
from wsgiref import simple_server


def s(environ, start_response):
    print("-------------------------------------- access ------------------------------------------")
    [print("{}: {}".format(k, environ[k])) for k in ["REQUEST_METHOD", "SCRIPT_NAME", "PATH_INFO", "QUERY_STRING", "CONTENT_TYPE", "CONTENT_LENGTH", "SERVER_NAME", "SERVER_PORT", "SERVER_PROTOCOL"]]
    [print("{}: {}".format(k, environ[k])) for k in environ.keys() if k.startswith("wsgi")]
    start_response("200 OK", [("content-type", "text/plain")])
    return [b"OK"]


simple_server.make_server("localhost", 5000, s).serve_forever()

"""
