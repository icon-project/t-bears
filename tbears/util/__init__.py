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
import re

import pkg_resources

from ..tbears_exception import TBearsWriteFileException


DIR_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_PATH = os.path.abspath(os.path.join(DIR_PATH, '..', '..'))


def write_file(parent_directory: str, file_name: str, contents: str, overwrite: bool = False) -> None:
    """Create file with the contents in the parents directory.

    :param parent_directory: Location to create the file.
    :param file_name: File name
    :param contents: Contents of file.
    """
    try:
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)
        if os.path.exists(f'{parent_directory}/{file_name}') and not overwrite:
            return
        with open(f'{parent_directory}/{file_name}', mode='w') as file:
            file.write(contents)
    except (PermissionError, IsADirectoryError) as e:
        raise TBearsWriteFileException(f"Can't write file {parent_directory}/{file_name}. {e}")


def get_init_template(project: str, score_class: str) -> str:
    return f'from .{project} import {score_class}\n'


def get_score_main_template(score_class: str) -> str:
    """
    :param score_class: Your score class name.
    :return:
    """
    template = """from iconservice import *


class SampleToken(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()
    
    @external(readonly=True)
    def hello(self) -> str:
        print(f'Hello, world!')
        return "Hello"
"""
    return template.replace("SampleToken", score_class)


def get_package_json_dict(project: str, score_class: str) -> dict:
    """Returns packs.json's template.

    :param project: SCORE's name.
    :param score_class: SCORE's main class name.

    :return: package.json's contents.(dict)
    """
    package_json_dict = {
        "version": "0.0.1",
        "main_file": f"{project}",
        "main_score": f"{score_class}"
    }
    return package_json_dict


def get_sample_crowd_sale_contents(score_class: str):
    """
    :param score_class: Your score class name.
    :return:
    """
    template = """from iconservice import *

TAG = 'MyCrowdSale'


class TokenInterface(InterfaceScore):
    @interface
    def transfer(self, _to: Address, _value: int, _data: bytes=None):
        pass


class MyCrowdSale(IconScoreBase):

    _ADDR_BENEFICIARY = 'addr_beneficiary'
    _ADDR_TOKEN_SCORE = 'addr_token_score'
    _FUNDING_GOAL = 'funding_goal'
    _AMOUNT_RAISED = 'amount_raised'
    _DEAD_LINE = 'dead_line'
    _PRICE = 'price'
    _BALANCES = 'balances'
    _JOINER_LIST = 'joiner_list'
    _FUNDING_GOAL_REACHED = 'funding_goal_reached'
    _CROWDSALE_CLOSED = 'crowdsale_closed'

    @eventlog(indexed=3)
    def FundTransfer(self, backer: Address, amount: int, is_contribution: bool):
        pass

    @eventlog(indexed=2)
    def GoalReached(self, recipient: Address, total_amount_raised: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        self._addr_beneficiary = VarDB(self._ADDR_BENEFICIARY, db, value_type=Address)
        self._addr_token_score = VarDB(self._ADDR_TOKEN_SCORE, db, value_type=Address)
        self._funding_goal = VarDB(self._FUNDING_GOAL, db, value_type=int)
        self._amount_raised = VarDB(self._AMOUNT_RAISED, db, value_type=int)
        self._dead_line = VarDB(self._DEAD_LINE, db, value_type=int)
        self._price = VarDB(self._PRICE, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)
        self._joiner_list = ArrayDB(self._JOINER_LIST, db, value_type=Address)
        self._funding_goal_reached = VarDB(self._FUNDING_GOAL_REACHED, db, value_type=bool)
        self._crowdsale_closed = VarDB(self._CROWDSALE_CLOSED, db, value_type=bool)

    def on_install(self, fundingGoalInIcx: int=1000, tokenScore: Address='cx02b13428a8aef265fbaeeb37394d3ae8727f7a19',
    durationInSeconds: int=120) -> None:
        super().on_install()

        Logger.debug(f'on_install: fundingGoalInIcx={fundingGoalInIcx}', TAG)
        Logger.debug(f'on_install: tokenScore={tokenScore}', TAG)
        Logger.debug(f'on_install: durationInSeconds={durationInSeconds}', TAG)

        one_second_in_microseconds = 1 * 10 ** 6
        now_seconds = self.now()
        icx_cost_of_each_token = 1

        self._addr_beneficiary.set(self.msg.sender)
        self._addr_token_score.set(tokenScore)
        self._funding_goal.set(fundingGoalInIcx)
        self._dead_line.set(now_seconds + durationInSeconds * one_second_in_microseconds)
        price = int(icx_cost_of_each_token)
        self._price.set(price)

        self._funding_goal_reached.set(False)
        self._crowdsale_closed.set(True)  # CrowdSale closed by default

    def on_update(self) -> None:
        super().on_update()

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        if self.msg.sender == self._addr_token_score.get() and _from == self.owner:
            # token supply to CrowdSale
            Logger.debug(f'tokenFallback: token supply = "{_value}"', TAG)
            if _value >= 0:
                self._crowdsale_closed.set(False)  # start CrowdSale hereafter
        else:
            # reject if this is an unrecognized token transfer
            Logger.debug(f'tokenFallback: REJECT transfer', TAG)
            self.revert('Unexpected token owner!')

    @payable
    def fallback(self):
        if self._crowdsale_closed.get():
            self.revert('CrowdSale is closed.')

        amount = self.msg.value
        self._balances[self.msg.sender] = self._balances[self.msg.sender] + amount
        self._amount_raised.set(self._amount_raised.get() + amount)
        value = int(amount / self._price.get())
        data = b'called from CrowdSale'
        token_score = self.create_interface_score(self._addr_token_score.get(), TokenInterface)
        token_score.transfer(self.msg.sender, value, data)

        if self.msg.sender not in self._joiner_list:
            self._joiner_list.put(self.msg.sender)

        self.FundTransfer(self.msg.sender, amount, True)
        Logger.debug(f'FundTransfer({self.msg.sender}, {amount}, True)', TAG)

    @external(readonly=True)
    def total_joiner_count(self) -> int:
        return len(self._joiner_list)

    def _after_dead_line(self) -> bool:
        Logger.debug(f'after_dead_line: now()       = {self.now()}', TAG)
        Logger.debug(f'after_dead_line: dead_line() = {self._dead_line.get()}', TAG)
        return self.now() >= self._dead_line.get()

    @external
    def check_goal_reached(self):
        if self._after_dead_line():
            if self._amount_raised.get() >= self._funding_goal.get():
                self._funding_goal_reached.set(True)
                self.GoalReached(self._addr_beneficiary.get(), self._amount_raised.get())
                Logger.debug(f'Goal reached!', TAG)
            self._crowdsale_closed.set(True)

    @external
    def safe_withdrawal(self):
        if self._after_dead_line():
            # each contributor can withdraw the amount they contributed if goal was not reached
            if not self._funding_goal_reached.get():
                amount = self._balances[self.msg.sender]
                self._balances[self.msg.sender] = 0
                if amount > 0:
                    if self.icx.send(self.msg.sender, amount):
                        self.FundTransfer(self.msg.sender, amount, False)
                        Logger.debug(f'FundTransfer({self.msg.sender}, {amount}, False)', TAG)
                    else:
                        self._balances[self.msg.sender] = amount

            if self._funding_goal_reached.get() and self._addr_beneficiary.get() == self.msg.sender:
                if self.icx.send(self._addr_beneficiary.get(), self._amount_raised.get()):
                    self.FundTransfer(self._addr_beneficiary.get(), self._amount_raised.get(), False)
                    Logger.debug(f'FundTransfer({self._addr_beneficiary.get()},'
                                 f'{self._amount_raised.get()}, False)', TAG)
                else:
                    # if the transfer to beneficiary fails, unlock contributors balance
                    Logger.debug(f'Failed to send to beneficiary!', TAG)
                    self._funding_goal_reached.set(False)


"""
    return template.replace("MyCrowdSale", score_class)


def get_sample_token_contents(score_class: str):
    template = """import abc

from iconservice import *

TAG = 'mySampleToken'


class TokenStandard(abc.ABC):
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def symbol(self) -> str:
        pass

    @abc.abstractmethod
    def decimals(self) -> int:
        pass

    @abc.abstractmethod
    def totalSupply(self) -> int:
        pass

    @abc.abstractmethod
    def balanceOf(self, _owner: Address) -> int:
        pass

    @abc.abstractmethod
    def transfer(self, _to: Address, _value: int, _data: bytes=None):
        pass


class CrowdSaleInterface(InterfaceScore):
    @interface
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        pass


class MySampleToken(IconScoreBase, TokenStandard):

    _BALANCES = 'balances'
    _TOTAL_SUPPLY = 'total_supply'

    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._total_supply = VarDB(self._TOTAL_SUPPLY, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)

    def on_install(self, initialSupply: int=1000, decimals: int=18) -> None:
        super().on_install()

        total_supply = initialSupply * 10 ** decimals
        Logger.debug(f'on_install: total_supply={total_supply}', TAG)

        self._total_supply.set(total_supply)
        self._balances[self.msg.sender] = total_supply

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return "MySampleToken"

    @external(readonly=True)
    def symbol(self) -> str:
        return "MST"

    @external(readonly=True)
    def decimals(self) -> int:
        return 18

    @external(readonly=True)
    def totalSupply(self) -> int:
        return self._total_supply.get()

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._balances[_owner]

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes=None):
        if _data is None:
            _data = b'None'
        self._transfer(self.msg.sender, _to, _value, _data)

    def _transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):
        if self._balances[_from] < _value:
            self.revert("Out of balance")

        self._balances[_from] = self._balances[_from] - _value
        self._balances[_to] = self._balances[_to] + _value
        if _to.is_contract:
            crowdsale_score = self.create_interface_score(_to, CrowdSaleInterface)
            crowdsale_score.tokenFallback(_from, _value, _data)
        self.Transfer(_from, _to, _value, _data)
        Logger.debug(f'Transfer({_from}, {_to}, {_value}, {_data})', TAG)

    """
    return template.replace("MySampleToken", score_class)


def is_lowercase_hex_string(value: str) -> bool:
    """Check whether value is hexadecimal format or not

    :param value: text
    :return: True(lowercase hexadecimal) otherwise False
    """
    try:
        result = re.match('[0-9a-f]+', value)
        return len(result.group(0)) == len(value)
    except:
        pass

    return False


def is_tx_hash(tx_hash: str) -> bool:
    """Check hash is valid.

    :param tx_hash:
    :return:
    """
    if isinstance(tx_hash, str) and len(tx_hash) == 66:
        prefix, body = tx_hash[:2], tx_hash[2:]
        return prefix == '0x' and is_lowercase_hex_string(body)

    return False


def get_tbears_version() -> str:
    """Get version of tbears.
    The location of the file that holds the version information is different when packaging and when executing.
    :return: version of tbears.
    """
    try:
        version = pkg_resources.get_distribution('tbears').version
    except pkg_resources.DistributionNotFound:
        version_path = os.path.join(PROJECT_ROOT_PATH, 'VERSION')
        with open(version_path, mode='r') as version_file:
            version = version_file.read()
    except:
        version = 'unknown'
    return version
