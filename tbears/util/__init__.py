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
import shutil
import time

import requests
from ..tbears_exception import TBearsWriteFileException, TBearsDeleteTreeException, TbearsConfigFileException


DIR_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_PATH = os.path.abspath(os.path.join(DIR_PATH, '..', '..'))


def write_file(parent_directory: str, file_name: str, contents: str) -> None:
    try:
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)
        if os.path.exists(f'{parent_directory}/{file_name}'):
            return
        with open(f'{parent_directory}/{file_name}', mode='w') as file:
            file.write(contents)
    except PermissionError:
        raise TBearsWriteFileException
    except IsADirectoryError:
        raise TBearsWriteFileException


def get_init_template(project: str, score_class: str) -> str:
    return f'from .{project} import {score_class}\n'


def get_score_main_template(score_class: str) -> str:
    """
    :param score_class: Your score class name.
    :return:
    """
    template = """from iconservice import *


class SampleToken(IconScoreBase):

    __BALANCES = 'balances'
    __TOTAL_SUPPLY = 'total_supply'

    @eventlog(indexed=3)
    def Transfer(self, addr_from: Address, addr_to: Address, value: int): pass

    def __init__(self, db: IconScoreDatabase, addr_owner: Address) -> None:
        super().__init__(db, addr_owner)
        self.__total_supply = VarDB(self.__TOTAL_SUPPLY, db, value_type=int)
        self.__balances = DictDB(self.__BALANCES, db, value_type=int)

    def on_install(self, init_supply: int = 1000, decimal: int = 18) -> None:
        super().on_install()

        total_supply = init_supply * 10 ** decimal

        self.__total_supply.set(total_supply)
        self.__balances[self.msg.sender] = total_supply

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def total_supply(self) -> int:
        return self.__total_supply.get()

    @external(readonly=True)
    def balance_of(self, addr_from: Address) -> int:
        return self.__balances[addr_from]

    def __transfer(self, _addr_from: Address, _addr_to: Address, _value: int) -> bool:

        if self.balance_of(_addr_from) < _value:
            self.revert(f"{_addr_from}'s balance < {_value}")

        self.__balances[_addr_from] = self.__balances[_addr_from] - _value
        self.__balances[_addr_to] = self.__balances[_addr_to] + _value

        self.Transfer(_addr_from, _addr_to, _value)
        return True

    @external
    def transfer(self, addr_to: Address, value: int) -> bool:
        return self.__transfer(self.msg.sender, addr_to, value)

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
            "version": "0x3",
            "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "to": f'cx{"0"*40}',
            "stepLimit": "0x12345",
            "fee": "0x2386f26fc10000",
            "timestamp": str(int(time.time() * 10 ** 6)),
            "nonce": "0x7362",
            "txHash": "0x4bf74e6aeeb43bde5dc8d5b62537a33ac8eb7605ebbdb51b015c1881b45b3aed",
            "dataType": "deploy",
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


class SampleTokenInterface(InterfaceScore):
    @interface
    def transfer(self, addr_to: Address, value: int) -> bool: pass


class SampleCrowdSale(IconScoreBase):
    __ADDR_BENEFICIARY = 'addr_beneficiary'
    __FUNDING_GOAL = 'funding_goal'
    __AMOUNT_RAISE = 'amount_raise'
    __DEAD_LINE = 'dead_line'
    __PRICE = 'price'
    __BALANCES = 'balances'
    __ADDR_TOKEN_SCORE = 'addr_token_score'
    __FUNDING_GOAL_REACHED = 'funding_goal_reached'
    __CROWD_SALE_CLOSED = 'crowd_sale_closed'
    __JOINER_LIST = 'joiner_list'

    @eventlog(indexed=3)
    def FundTransfer(self, backer: Address, amount: int, is_contribution: bool):
        pass

    @eventlog(indexed=2)
    def GoalReached(self, recipient: Address, total_amount_raised: int):
        pass

    def __init__(self, db: IconScoreDatabase, owner: Address) -> None:
        super().__init__(db, owner)

        self.__addr_beneficiary = VarDB(self.__ADDR_BENEFICIARY, db, value_type=Address)
        self.__addr_token_score = VarDB(self.__ADDR_TOKEN_SCORE, db, value_type=Address)
        self.__funding_goal = VarDB(self.__FUNDING_GOAL, db, value_type=int)
        self.__amount_raise = VarDB(self.__AMOUNT_RAISE, db, value_type=int)
        self.__dead_line = VarDB(self.__DEAD_LINE, db, value_type=int)
        self.__price = VarDB(self.__PRICE, db, value_type=int)
        self.__balances = DictDB(self.__BALANCES, db, value_type=int)
        self.__joiner_list = ArrayDB(self.__JOINER_LIST, db, value_type=Address)
        self.__funding_goal_reached = VarDB(self.__FUNDING_GOAL_REACHED, db, value_type=bool)
        self.__crowd_sale_closed = VarDB(self.__CROWD_SALE_CLOSED, db, value_type=bool)

        self.__sample_token_score = self.create_interface_score(self.__addr_token_score.get(), SampleTokenInterface)

    def on_install(self, funding_goal_in_icx: int = 100, duration_in_minutes: int = 1,
                   icx_cost_of_each_token: int = 1, token_address: str='cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf') -> None:
        super().on_install()

        one_icx = 1 * 10 ** 18
        one_minute_to_sec = 1 * 60
        one_second_to_microsec = 1 * 10 ** 6
        now_seconds = self.now()

        # genesis params
        if_successful_send_to = self.msg.sender
        addr_token_score = Address.from_string(token_address)

        self.__addr_beneficiary.set(if_successful_send_to)
        self.__addr_token_score.set(addr_token_score)
        self.__funding_goal.set(funding_goal_in_icx * one_icx)
        self.__dead_line.set(now_seconds + duration_in_minutes * one_minute_to_sec * one_second_to_microsec)
        price = int(icx_cost_of_each_token * one_icx)
        self.__price.set(price)

        self.__sample_token_score = self.create_interface_score(self.__addr_token_score.get(), SampleTokenInterface)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def total_joiner_count(self):
        return len(self.__joiner_list)

    @payable
    def fallback(self) -> None:
        # if self.__crowd_sale_closed.get():
        #     self.revert('crowd sale is closed')

        amount = self.msg.value
        self.__balances[self.msg.sender] = self.__balances[self.msg.sender] + amount
        self.__amount_raise.set(self.__amount_raise.get() + amount)
        value = int(amount / self.__price.get())

        self.__sample_token_score.transfer(self.msg.sender, value)

        if self.msg.sender not in self.__joiner_list:
            self.__joiner_list.put(self.msg.sender)

        self.FundTransfer(self.msg.sender, amount, True)

    @external
    def check_goal_reached(self):
        # if not self.__after_dead_line():
        #     self.revert('before deadline')

        if self.__amount_raise.get() >= self.__funding_goal.get():
            self.__funding_goal_reached.set(True)
            self.GoalReached(self.__addr_beneficiary.get(), self.__amount_raise.get())
        self.__crowd_sale_closed.set(True)

    def __after_dead_line(self):
        return self.now() >= self.__dead_line.get()

    @external
    def safe_withdrawal(self):
        # if not self.__after_dead_line():
        #     self.revert('before deadline')

        if not self.__funding_goal_reached.get():
            amount = self.__balances[self.msg.sender]
            self.__balances[self.msg.sender] = 0
            if amount > 0:
                if self.icx.send(self.msg.sender, amount):
                    self.FundTransfer(self.msg.sender, amount, False)
                else:
                    self.__balances[self.msg.sender] = amount

        if self.__funding_goal_reached.get() and self.__addr_beneficiary.get() == self.msg.sender:
            if self.icx.send(self.__addr_beneficiary.get(), self.__amount_raise.get()):
                self.FundTransfer(self.__addr_beneficiary.get(), self.__amount_raise.get(),
                                  False)
            else:
                self.__funding_goal_reached.set(False)

"""
    return contents


def get_deploy_payload():
    payload = {
        "version": "0x3",
        "from": "",
        "to": "",
        "stepLimit": "0x12345",
        "timestamp": f'{hex(int(time.time() * 10 ** 6))}',
        "nonce": "0x1",
        "dataType": "deploy",
        "data": {
            "contentType": "application/zip",
            "content": "",
            "params": {
            }
        }
    }
    return payload


def get_deploy_config(path: str) -> dict:
    try:
        with open(path, mode='rb') as config_file:
            config_dict = json.load(config_file)
        deploy_config = config_dict['deploy']
    except:
        raise TbearsConfigFileException
    else:
        return deploy_config


def get_tx_phrase(params: dict) -> str:
    keys = [k for k in params]
    keys.sort()
    key_count = len(keys)
    if key_count == 0:
        return ""
    phrase = ""

    if not params[keys[0]]:
        phrase += keys[0]
    elif not isinstance(params[keys[0]], dict):
        phrase += f'{keys[0]}.{params[keys[0]]}'
    else:
        phrase += f'{keys[0]}.{get_tx_phrase(params[keys[0]])}'

    for i in range(1, key_count):
        key = keys[i]

        if not params[key]:
            phrase += f'.{key}'
        elif not isinstance(params[key], dict):
            phrase += f'.{key}.{params[key]}'
        else:
            phrase += f'.{key}.{get_tx_phrase(params[key])}'

    return phrase


def get_network_url(network_name: str) -> str:
    if network_name == "mainnet":
        return "https://wallet.icon.foundation/api/"
    else:
        return "https://testwallet.icon.foundation/api/"
