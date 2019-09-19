# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import time
import asyncio
from contextlib import suppress


class Periodic:
    """
    Class for periodic work in asyncio
    """
    def __init__(self, func: callable, interval: int):
        self.func = func
        self.interval = interval
        self.is_started = False
        self._task = None

    async def start(self):
        """
        Start the periodic work
        :return:
        """
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        """
        Stop the periodic work
        :return:
        """
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        """
        Do the work
        :return:
        """
        next_time = time.time() + self.interval
        while True:
            # get time to sleep
            remain_time = next_time - time.time()
            if remain_time > 0:
                await asyncio.sleep(remain_time)

            # set next working time
            next_time = time.time() + self.interval

            # do work
            await self.func()


class Immediate:
    """
    Class for immediate work in asyncio
    """
    def __init__(self):
        self.funcs: list = []
        self.is_started = False
        self._task = None

    async def start(self):
        """
        Start the immediate work
        :return:
        """
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        """
        Stop the immediate work
        :return:
        """
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    def add_func(self, func: callable):
        self.funcs.append(func)

    async def _run(self):
        """
        Do the work
        :return:
        """
        while True:
            if self.funcs:
                func: callable = self.funcs.pop()
                await func()
            else:
                await asyncio.sleep(0)
