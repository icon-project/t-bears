# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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

import hashlib
import inspect
import random
import sys
from collections import namedtuple
from shutil import rmtree
from time import time, sleep
from typing import Any
from typing import List
from unittest import TestCase

from iconcommons import IconConfig

from iconsdk.builder.call_builder import Call
from iconsdk.converter import convert_transaction_result
from iconsdk.exception import IconServiceBaseException
from iconsdk.icon_service import IconService
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from iconservice.base.address import Address
from iconservice.base.block import Block
from iconservice.base.type_converter import TypeConverter, ParamType
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey, DATA_BYTE_ORDER
from iconservice.icon_inner_service import MakeResponse
from iconservice.icon_service_engine import IconServiceEngine
from iconservice.utils import to_camel_case

from tbears.config.tbears_config import TEST1_PRIVATE_KEY, tbears_server_config, ConfigKey as TbConf

SCORE_INSTALL_ADDRESS = f"cx{'0' * 40}"
Account = namedtuple('Account', 'name address balance')


def create_hash_256(data: bytes = None) -> bytes:
    if data is None:
        max_int = sys.maxsize
        length = (max_int.bit_length() + 7) // 8
        data = int(random.randint(0, max_int)).to_bytes(length, DATA_BYTE_ORDER)

    return hashlib.sha3_256(data).digest()


def create_tx_hash(data: bytes = None) -> bytes:
    return create_hash_256(data)


def create_block_hash(data: bytes = None) -> bytes:
    return create_tx_hash(data)


def root_clear(score_path: str, state_db_path: str):
    rmtree(score_path, ignore_errors=True)
    rmtree(state_db_path, ignore_errors=True)


def create_timestamp():
    return int(time() * 10 ** 6)


class IconIntegrateTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._score_root_path = '.testscore'
        cls._state_db_root_path = '.teststatedb'

        cls._icx_factor = 10 ** 18

        cls._genesis: 'KeyWallet' = KeyWallet.create()
        cls._fee_treasury: 'KeyWallet' = KeyWallet.create()
        cls._test1: 'KeyWallet' = KeyWallet.load(bytes.fromhex(TEST1_PRIVATE_KEY))

        cls._wallet_array = [KeyWallet.create() for _ in range(10)]

    def setUp(self, genesis_accounts: List[Account] = None):
        root_clear(self._score_root_path, self._state_db_root_path)

        self._block_height = 0
        self._prev_block_hash = None

        config = IconConfig("", default_icon_config)
        config.load()
        config.update_conf({ConfigKey.BUILTIN_SCORE_OWNER: self._test1.get_address()})
        config.update_conf({ConfigKey.SCORE_ROOT_PATH: self._score_root_path,
                            ConfigKey.STATE_DB_ROOT_PATH: self._state_db_root_path})
        config.update_conf(self._make_init_config())
        self.icon_service_engine = IconServiceEngine()
        self.icon_service_engine.open(config)

        self._genesis_invoke(genesis_accounts)

    def tearDown(self):
        self.icon_service_engine.close()
        root_clear(self._score_root_path, self._state_db_root_path)

    def _make_init_config(self) -> dict:
        return {}

    @staticmethod
    def _append_list(tx: dict, genesis_accounts: List[Account]) -> None:
        """Appends additional genesis account list to genesisData

        :param genesis_accounts: additional genesis account list consisted of namedtuple named Account
        of which keys are name, address and balance
        :return: None
        """
        for account_as_namedtuple in genesis_accounts:
            tx["genesisData"]['accounts'].append({
                "name": account_as_namedtuple.name,
                "address": account_as_namedtuple.address,
                "balance": account_as_namedtuple.balance
            })

    def _genesis_invoke(self, genesis_accounts: List[Account]) -> list:
        tx_hash = create_tx_hash()
        timestamp_us = create_timestamp()
        request_params = {
            'txHash': tx_hash,
            'version': 3,
            'timestamp': timestamp_us
        }

        tx = {
            'method': 'icx_sendTransaction',
            'params': request_params,
            'genesisData': {
                "accounts": [
                    {
                        "name": "genesis",
                        "address": Address.from_string(self._genesis.get_address()),
                        "balance": 100 * self._icx_factor
                    },
                    {
                        "name": "fee_treasury",
                        "address": Address.from_string(self._fee_treasury.get_address()),
                        "balance": 0
                    },
                    {
                        "name": "_admin",
                        "address": Address.from_string(self._test1.get_address()),
                        "balance": 1_000_000 * self._icx_factor
                    }
                ]
            },
        }

        if genesis_accounts:
            self._append_list(tx, genesis_accounts)

        block_hash = create_block_hash()
        block = Block(self._block_height, block_hash, timestamp_us, None)
        tx_results, _ = self.icon_service_engine.invoke(
            block,
            [tx]
        )
        if 'block' in inspect.signature(self.icon_service_engine.commit).parameters:
            self.icon_service_engine.commit(block)
        else:
            self.icon_service_engine.commit(block.height, block.hash, block.hash)

        self._block_height += 1
        self._prev_block_hash = block_hash

        return tx_results

    def _make_and_req_block(self, tx_list: list, block_height: int = None) -> tuple:
        if block_height is None:
            block_height: int = self._block_height
        block_hash = create_block_hash()
        timestamp_us = create_timestamp()

        block = Block(block_height, block_hash, timestamp_us, self._prev_block_hash)

        tx_results, state_root_hash = self.icon_service_engine.invoke(block, tx_list)

        convert_tx_results = [tx_result.to_dict(to_camel_case) for tx_result in tx_results]
        response = MakeResponse.make_response(convert_tx_results)

        return block, response

    def _write_precommit_state(self, block: 'Block') -> None:
        if 'block' in inspect.signature(self.icon_service_engine.commit).parameters:
            self.icon_service_engine.commit(block)
        else:
            self.icon_service_engine.commit(block.height, block.hash, block.hash)
        self._block_height += 1
        self._prev_block_hash = block.hash

    def _query(self, request: dict, method: str = 'icx_call') -> Any:
        response = self.icon_service_engine.query(method, request)

        # convert response
        if isinstance(response, int):
            response = hex(response)
        elif isinstance(response, Address):
            response = str(response)
        return response

    def _process_transaction_in_local(self, request: dict) -> dict:
        params = TypeConverter.convert(request, ParamType.TRANSACTION_PARAMS_DATA)
        params['txHash'] = create_tx_hash()
        tx = {
            'method': 'icx_sendTransaction',
            'params': params
        }

        prev_block, tx_results = self._make_and_req_block([tx])
        self._write_precommit_state(prev_block)

        # convert TX result as sdk style
        convert_transaction_result(tx_results[0])

        return tx_results[0]

    def process_transaction(self, request: SignedTransaction,
                            network: IconService = None,
                            block_confirm_interval: int = tbears_server_config[TbConf.BLOCK_CONFIRM_INTERVAL]) -> dict:
        try:
            if network is not None:
                # Send the transaction to network
                tx_hash = network.send_transaction(request)
                sleep(block_confirm_interval)
                # Get transaction result
                tx_result = network.get_transaction_result(tx_hash)
            else:
                # process the transaction in local
                tx_result = self._process_transaction_in_local(request.signed_transaction_dict)
        except IconServiceBaseException as e:
            tx_result = e.message

        return tx_result

    def process_call(self, call: Call, network: IconService = None):
        try:
            if network is not None:
                response = network.call(call)
            else:
                request = {
                    "from": Address.from_string(call.from_),
                    "to": Address.from_string(call.to),
                    "dataType": "call",
                    "data": {
                        "method": call.method
                    }
                }

                if isinstance(call.params, dict):
                    request["data"]["params"] = call.params

                response = self._query(request=request)
        except IconServiceBaseException as e:
            response = e.message

        return response
