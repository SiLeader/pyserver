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
from concurrent.futures import ThreadPoolExecutor
import argparse

import settings
import core


def args_parser():
    parser = argparse.ArgumentParser(
        prog="webserver",
        usage="PROGRAM [setting file location]...",
        description="web server",
        epilog="Published under the Apache License 2.0"
    )
    parser.add_argument("--setting", "-s", action="store", nargs="+", type=str)
    return parser.parse_args()


def main():
    args = args_parser()
    sets = settings.load(args.setting)
    if len(sets) == 0:
        print("No servers found.")
        exit(1)

    loop = asyncio.get_event_loop()
    loop.set_default_executor(ThreadPoolExecutor())

    servers = [s.build(loop) for s in sets]
    servers.append(core.idle(loop))
    try:
        loop.run_until_complete(asyncio.gather(*servers))
    except KeyboardInterrupt:
        pass

    loop.close()


if __name__ == '__main__':
    main()
