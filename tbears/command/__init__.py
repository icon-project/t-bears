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
from enum import IntEnum
from typing import Optional
import json

from tbears.util import write_file
from tbears.util.keystore_manager import __make_key_store_content


class ExitCode(IntEnum):
    SUCCEEDED = 1
    COMMAND_IS_WRONG = 0
    SCORE_PATH_IS_NOT_A_DIRECTORY = 2
    PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY = 3
    WRITE_FILE_ERROR = 4
    DELETE_TREE_ERROR = 5
    SCORE_AlREADY_EXISTS = 6
    PROJECT_AND_CLASS_NAME_EQUAL = 7
    CONFIG_FILE_ERROR = 8
    KEY_STORE_ERROR = 9
    DEPLOY_ERROR = 10
    ICON_CLIENT_ERROR = 11
    SERVER_INFO_ERROR = 12
    NOT_EMPTY_PATH = 13


class Command(object):
    @staticmethod
    def write_conf(file_path: str, conf: dict) -> None:
        conf_org = Command.get_conf(file_path=file_path)
        if conf_org is None:
            conf_org = conf
        else:
            for key in conf:
                if key in conf_org:
                    conf_org[key] = conf[key]
                else:
                    conf_org[key] = conf[key]

        file_name = file_path[file_path.rfind('/') + 1:]
        parent_directory = file_path[:file_path.rfind('/')]
        try:
            write_file(parent_directory=parent_directory, file_name=file_name, contents=json.dumps(conf_org),
                       overwrite=True)
        except Exception as e:
            print(f"Can't write conf to file {e}")

    @staticmethod
    def get_conf(file_path: str) -> Optional[dict]:
        try:
            with open(f'{file_path}') as f:
                conf = json.load(f)
        except Exception as e:
            return None

        return conf

    @staticmethod
    def combine_conf(conf: dict, new_conf: dict) -> None:
        for k, v in new_conf.items():
            if v:
                conf[k] = v


def make_keystore(path: str, password: str) -> int:
    key_store_content = __make_key_store_content(password)

    if os.path.exists(path):
        print(f'{path} is not empty.')
        return ExitCode.NOT_EMPTY_PATH
    with open(path, mode='w') as ks:
        ks.write(json.dumps(key_store_content))
    return ExitCode.SUCCEEDED
