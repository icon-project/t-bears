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
        if os.path.exists(f'{parent_directory}/{file_name}'):
            raise TBearsWriteFileException
        with open(f'{parent_directory}/{file_name}', mode='w') as file:
            file.write(contents)
    except PermissionError:
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
    except requests.exceptions.Timeout:
        raise RuntimeError("Timeout happened. Check your internet connection status.")
    else:
        return r


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


def get_sample_crowd_sale_contents():
    """

    :return:
    """
    contents = """from iconservice import *


class SampleCrowdSale(IconScoreBase):
    _ADDR_BENEFICIARY = 'addr_beneficiary'
    _FUNDING_GOAL = 'funding_goal'
    _AMOUNT_RAISE = 'amount_raise'
    _DEAD_LINE = 'dead_line'
    _PRICE = 'price'
    _BALANCES = 'balances'
    _ADDR_TOKEN_SCORE = 'addr_token_score'
    _FUNDING_GOAL_REACHED = 'funding_goal_reached'
    _CROWD_SALE_CLOSED = 'crowd_sale_closed'
    _JOINER_LIST = 'joiner_list'

    def __init__(self, db: IconScoreDatabase, owner: Address) -> None:
        super().__init__(db, owner)

        self._addr_beneficiary = VarDB(self._ADDR_BENEFICIARY, db, value_type=Address)
        self._addr_token_score = VarDB(self._ADDR_TOKEN_SCORE, db, value_type=Address)
        self._funding_goal = VarDB(self._FUNDING_GOAL, db, value_type=int)
        self._amount_raise = VarDB(self._AMOUNT_RAISE, db, value_type=int)
        self._dead_line = VarDB(self._DEAD_LINE, db, value_type=int)
        self._price = VarDB(self._PRICE, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)
        self._joiner_list = ArrayDB(self._JOINER_LIST, db, value_type=Address)
        self._funding_goal_reached = VarDB(self._FUNDING_GOAL_REACHED, db, value_type=bool)
        self._crowd_sale_closed = VarDB(self._CROWD_SALE_CLOSED, db, value_type=bool)

    def genesis_init(self, *args, **kwargs) -> None:
        super().genesis_init(*args, **kwargs)

        one_icx = 1 * 10 ** 18
        one_minute_to_sec = 1 * 60
        one_second_to_microsec = 1 * 10 ** 6
        now_seconds = self.now()

        # genesis params
        if_successful_send_to = self.msg.sender
        addr_token_score = Address.from_string('cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c')

        funding_goal_in_icx = 100
        duration_in_minutes = 1
        icx_cost_of_each_token = 1

        self._addr_beneficiary.set(if_successful_send_to)
        self._addr_token_score.set(addr_token_score)
        self._funding_goal.set(funding_goal_in_icx * one_icx)
        self._dead_line.set(now_seconds + duration_in_minutes * one_minute_to_sec * one_second_to_microsec)
        price = int(icx_cost_of_each_token * one_icx)
        self._price.set(price)

    @external(readonly=True)
    def total_joiner_count(self):
        return len(self._joiner_list)

    @payable
    def fallback(self) -> None:
        # if self._crowd_sale_closed.get():
        #     raise IconScoreException('sampleCrowdSale sale is closed')

        amount = self.msg.value
        self._balances[self.msg.sender] = self._balances[self.msg.sender] + amount
        self._amount_raise.set(self._amount_raise.get() + amount)
        value = int(amount / self._price.get())
        self.call(self._addr_token_score.get(), 'transfer', {'addr_to': self.msg.sender, 'value': value})

        if self.msg.sender not in self._joiner_list:
            self._joiner_list.put(self.msg.sender)

        # event FundTransfer(msg.sender, amount, True)

    @external
    def check_goal_reached(self):
        # if not self.__after_dead_line():
        #     raise IconScoreException('before deadline')

        if self._amount_raise.get() >= self._funding_goal.get():
            self._funding_goal_reached.set(True)
            # event GoalReached(beneficiary, amountRaised)
        self._crowd_sale_closed.set(True)

    def __after_dead_line(self):
        return self.now() >= self._dead_line.get()

    @external
    def safe_withdrawal(self):
        # if not self.__after_dead_line():
        #     raise IconScoreException('before deadline')

        if not self._funding_goal_reached.get():
            amount = self._balances[self.msg.sender]
            if amount > 0:
                if self.send(self.msg.sender, amount):
                    # event FundTransfer(msg.sender, amount, False)
                    pass
                else:
                    self._balances[self.msg.sender] = amount

        if self._funding_goal_reached.get() and self._addr_beneficiary.get() == self.msg.sender:
            if self.send(self._addr_beneficiary.get(), self._amount_raise.get()):
                # event FundTransfer(beneficiary, amountRaised, False)
                pass
            else:
                self._funding_goal_reached.set(False)

"""
    return contents
