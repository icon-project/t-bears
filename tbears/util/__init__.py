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
import shutil
import time

import requests
from ..tbears_exception import TBearsWriteFileException, TBearsDeleteTreeException


def write_file(parent_directory: str, file_name: str, contents: str) -> None:
    try:
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)
        with open(f'./{parent_directory}/{file_name}', mode='w') as file:
            file.write(contents)
    except PermissionError:
        raise TBearsWriteFileException
    except FileExistsError:
        raise TBearsWriteFileException
    except IsADirectoryError:
        raise TBearsWriteFileException


def get_init_template(project: str, score_class: str) -> str:
    return f"from .{project} import {score_class}\n"


def get_score_main_template(score_class: str) -> str:
    """
    :param score_class: Your score class name.
    :return:
    """
    template = """from iconservice import *

class SampleToken(IconScoreBase):

    _BALANCES = 'balances'
    _TOTAL_SUPPLY = 'total_supply'

    def __init__(self, db: IconScoreDatabase, addr_owner: Address) -> None:
        super().__init__(db, addr_owner)
        self._total_supply = VarDB(self._TOTAL_SUPPLY, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)

    def genesis_init(self, *args, **kwargs) -> None:
        super().genesis_init(*args, **kwargs)

        init_supply = 1000
        decimal = 18
        total_supply = init_supply * 10 ** decimal

        self._total_supply.set(total_supply)
        self._balances[self.msg.sender] = total_supply

    @external(readonly=True)
    def total_supply(self) -> int:
        return self._total_supply.get()

    @external(readonly=True)
    def balance_of(self, addr_from: Address) -> int:
        return self._balances[addr_from]

    def _transfer(self, _addr_from: Address, _addr_to: Address, _value: int) -> bool:

        if self.balance_of(_addr_from) < _value:
            raise IconScoreException(f"{_addr_from}'s balance < {_value}")

        self._balances[_addr_from] = self._balances[_addr_from] - _value
        self._balances[_addr_to] = self._balances[_addr_to] + _value
        return True

    @external
    def transfer(self, addr_to: Address, value: int) -> bool:
        return self._transfer(self.msg.sender, addr_to, value)

    def fallback(self) -> None:
        pass
"""
    return template.replace("SampleToken", score_class)


def get_package_json_dict(project: str, score_class: str) -> dict:
    package_json_dict = {
        "version": "0.0.1",
        "main_file": f"{project}",
        "main_score": f"{score_class}"
    }
    return package_json_dict


def make_install_json_payload(project: str) -> dict:
    path = os.path.abspath(f'./{project}')
    payload = {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 111,
        "params": {
            "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "to":   "cxbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "fee": "0x2386f26fc10000",
            "timestamp": str(int(time.time() * 10 ** 6)),
            "nonce": "0x7362",
            "txHash": "4bf74e6aeeb43bde5dc8d5b62537a33ac8eb7605ebbdb51b015c1881b45b3aed",
            "dataType": "install",
            "data": {
                "contentType": "application/tbears",
                "content": path
            }
        }
    }
    return payload


def make_exit_json_payload() -> dict:
    payload = {"jsonrpc": "2.0", "method": "server_exit", "id": 99999}
    return payload


def post(url: str, payload: dict):
    try:
        r = requests.post(url, json=payload, verify=False)
        return r
    except requests.exceptions.Timeout:
        raise RuntimeError("Timeout happened. Check your internet connection status.")


def delete_score_info():
    """ Delete .score directory and db directory.

    :return:
    """
    try:
        if os.path.exists('./.score'):
            shutil.rmtree('./.score')
        if os.path.exists('./.db'):
            shutil.rmtree('./.db')
    except PermissionError:
        raise TBearsDeleteTreeException
    except NotADirectoryError:
        raise TBearsDeleteTreeException
