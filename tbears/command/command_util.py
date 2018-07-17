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
import json
import os

from tbears.command import Command, ExitCode
from tbears.util.keystore_manager import make_key_store_content


class CommandUtil(Command):

    @staticmethod
    def make_keystore(path: str, password: str) -> int:
        """Make keystore file with passed path and password.

        :param path: Determine where to save the keystore file.
        :param password: password
        :return: Exitcode
        """
        key_store_content = make_key_store_content(password)

        if os.path.exists(path):
            print(f'{path} is not empty.')
            return ExitCode.NOT_EMPTY_PATH
        with open(path, mode='wb') as ks:
            ks.write(json.dumps(key_store_content).encode())
        return ExitCode.SUCCEEDED
