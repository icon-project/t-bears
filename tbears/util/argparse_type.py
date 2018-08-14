# -*- coding: utf-8 -*-
# Copyright 2017-2018 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from argparse import ArgumentTypeError

from iconservice.base.address import is_icon_address_valid

from tbears.util import is_valid_hash


class IconPath(str):
    def __init__(self, mode: str = 'r'):
        self._mode = mode

    def __call__(self, string: str) -> str:
        if self._mode == 'r' and not os.path.exists(string):
            raise ArgumentTypeError(f"There is no '{string}'")
        elif self._mode == 'w' and os.path.exists(string):
            raise ArgumentTypeError(f"'{string}' must be empty")
        elif self._mode == 'd' and not os.path.isdir(string):
            raise ArgumentTypeError(f"There is no directory '{string}'")

        return string


class IconAddress(str):
    def __init__(self, prefix: str = 'all'):
        self._prefix = prefix

    def __call__(self, string: str) -> str:
        # check prefix of given address(string). if not 'cx' or 'hx', raise error
        if not is_icon_address_valid(string):
            raise ArgumentTypeError(f"Invalid address '{string}'")

        if self._prefix != 'all':
            if self._prefix != string[:2]:
                raise ArgumentTypeError(f"Invalid address '{string}'. Address must start with '{self._prefix}'")

        return string


def hash_type(string: str) -> str:
    # check hash's length, prefix, lowcase.
    if not is_valid_hash(string):
        raise ArgumentTypeError(f"Invalid transaction hash '{string}'")

    return string


def port_type(string: str) -> str:
    port = int(string, 10)

    if port < 0 or port > 65535:
        raise ArgumentTypeError(f"Invalid port'{string}'. Port must be 0 < port < 65536")

    return string
