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
from typing import Any, Union, List
from unittest import TestCase
from unittest.mock import Mock

from iconcommons import IconConfig
from iconsdk.builder.call_builder import Call
from iconsdk.builder.transaction_builder import MessageTransactionBuilder, TransactionBuilder
from iconsdk.exception import IconServiceBaseException, URLException
from iconsdk.icon_service import IconService
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.utils.converter import convert
from iconsdk.utils.templates import TRANSACTION_RESULT
from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.address import Address
from iconservice.base.block import Block
from iconservice.base.type_converter import TypeConverter, ParamType
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey, DATA_BYTE_ORDER, IconScoreContextType, RCCalculateResult
from iconservice.icon_inner_service import MakeResponse
from iconservice.icon_service_engine import IconServiceEngine
from iconservice.iconscore.icon_score_context import IconScoreContext
from iconservice.iiss.reward_calc.ipc.reward_calc_proxy import RewardCalcProxy, CalculateDoneNotification
from iconservice.utils import to_camel_case

from tbears.config.tbears_config import TEST_ACCOUNTS, TEST1_PRIVATE_KEY, tbears_server_config, TConfigKey as TbConf

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
        cls._wallet_array = [KeyWallet.load(v) for v in TEST_ACCOUNTS]

    def setUp(self,
              genesis_accounts: List[Account] = None,
              block_confirm_interval: int = tbears_server_config[TbConf.BLOCK_CONFIRM_INTERVAL],
              network_only: bool = False,
              network_delay_ms: int = tbears_server_config[TbConf.NETWORK_DELAY_MS]):

        self._block_height = -1
        self._prev_block_hash = None
        self._block_confirm_interval = block_confirm_interval
        self._network_only: bool = network_only
        self._network_delay: float = network_delay_ms / 1000

        if self._network_only:
            return

        root_clear(self._score_root_path, self._state_db_root_path)

        config = IconConfig("", default_icon_config)
        config.load()
        config.update_conf({ConfigKey.BUILTIN_SCORE_OWNER: self._test1.get_address()})
        config.update_conf({ConfigKey.SCORE_ROOT_PATH: self._score_root_path,
                            ConfigKey.STATE_DB_ROOT_PATH: self._state_db_root_path})
        config.update_conf(self._make_init_config())

        self.icon_service_engine = IconServiceEngine()
        self._mock_rc_proxy()
        self.icon_service_engine.open(config)

        self._genesis_invoke(genesis_accounts)
        self._tx_results: dict = {}

    def tearDown(self):
        if not self._network_only:
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
        block = Block(self._block_height + 1, block_hash, timestamp_us, None, 0)
        tx_results, _, _, _ = self.icon_service_engine.invoke(
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

        block = Block(block_height + 1, block_hash, timestamp_us, self._prev_block_hash)

        tx_results, state_root_hash, added_transactions, main_preps = self.icon_service_engine.invoke(block, tx_list)

        convert_tx_results = [tx_result.to_dict(to_camel_case) for tx_result in tx_results]
        results = {
            'txResults': convert_tx_results,
            'stateRootHash': bytes.hex(state_root_hash),
            'addedTransactions': added_transactions
        }
        if main_preps:
            results['prep'] = main_preps

        response = MakeResponse.make_response(results)

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

    def _process_transaction_in_local(self, request: dict):
        params = TypeConverter.convert(request, ParamType.TRANSACTION_PARAMS_DATA)
        tx_hash: bytes = create_tx_hash()
        params['txHash'] = tx_hash
        tx = {
            'method': 'icx_sendTransaction',
            'params': params
        }

        prev_block, response = self._make_and_req_block([tx])
        self._write_precommit_state(prev_block)

        txresults: dict = response["txResults"]

        # convert TX result as sdk style
        for txresult in txresults:
            key: str = txresult["txHash"]
            self._tx_results[key] = convert(txresult, TRANSACTION_RESULT, True)

        return tx_hash.hex()

    def _get_tx_result(self, tx_hash: str) -> dict:
        return self._tx_results[tx_hash]

    # ========== API ========== #

    def process_transaction(self, request: SignedTransaction,
                            network: IconService = None,
                            block_confirm_interval: int = -1) -> dict:
        if self._network_only and network is None:
            raise URLException("Set network URL")

        if block_confirm_interval == -1:
            block_confirm_interval = self._block_confirm_interval

        if network is not None:
            # Send the transaction to network
            tx_hash: str = network.send_transaction(request)
            sleep(block_confirm_interval + 0.1)
            # Get transaction result
            tx_result: dict = network.get_transaction_result(tx_hash)
        else:
            # process the transaction in local
            tx_hash: str = self._process_transaction_in_local(request.signed_transaction_dict)
            tx_result: dict = self._get_tx_result(tx_hash)
        return tx_result

    def process_transaction_bulk(self,
                                 requests: list,
                                 network: IconService = None,
                                 block_confirm_interval: int = -1) -> list:
        if self._network_only and network is None:
            raise URLException("Set network URL")

        if block_confirm_interval == -1:
            block_confirm_interval = self._block_confirm_interval

        tx_results: list = []

        try:
            if network is not None:
                tx_hashes: list = []
                for req in requests:
                    # Send the transaction to network
                    tx_hash = network.send_transaction(req)
                    tx_hashes.append(tx_hash)

                sleep(block_confirm_interval)

                # Get transaction result
                for h in tx_hashes:
                    tx_result = network.get_transaction_result(h)
                    tx_results.append(tx_result)
            else:
                for req in requests:
                    # process the transaction in local
                    tx_result = self._process_transaction_in_local(req.signed_transaction_dict)
                    tx_results.append(tx_result)
        except IconServiceBaseException as e:
            tx_result = e.message
            tx_results.append(tx_result)

        return tx_results

    def process_call(self, call: Call, network: IconService = None):
        if self._network_only and network is None:
            raise URLException("Set network URL")

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

    def process_message_tx(self, network: IconService = None,
                           msg: str = "dummy",
                           block_confirm_interval: int = -1) -> dict:
        if self._network_only and network is None:
            raise URLException("Set network URL")

        if block_confirm_interval == -1:
            block_confirm_interval = self._block_confirm_interval

        msg_byte = msg.encode('utf-8')

        # build message tx
        transaction = MessageTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._test1.get_address()) \
            .step_limit(10000000000) \
            .nid(3) \
            .nonce(100) \
            .data(f"0x{msg_byte.hex()}") \
            .build()

        # signing message tx
        request = SignedTransaction(transaction, self._test1)

        try:
            if network is not None:
                # Send the transaction to network
                tx_hash = network.send_transaction(request)
                sleep(block_confirm_interval)
                # Get transaction result
                tx_result = network.get_transaction_result(tx_hash)
            else:
                # process the transaction in local
                tx_results = self._process_transaction_in_local(request.signed_transaction_dict)
        except IconServiceBaseException as e:
            tx_result = e.message

        return tx_result

    def process_confirm_block_tx(self, network: IconService):
        # build message tx
        transaction = TransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to("hx0000000000000000000000000000000000000000") \
            .value(0) \
            .step_limit(10_000_000_000) \
            .nonce(0) \
            .build()

        # signing message tx
        request = SignedTransaction(transaction, self._test1)

        network.send_transaction(request)
        if self._block_confirm_interval > 0:
            sleep(self._block_confirm_interval)
        else:
            sleep(self._network_delay)

    def process_transaction_without_txresult(self,
                                             request: SignedTransaction,
                                             network: IconService) -> list:
        tx_hashes: list = [network.send_transaction(request)]
        if self._block_confirm_interval > 0:
            sleep(self._block_confirm_interval)
        return tx_hashes

    def process_transaction_bulk_without_txresult(self,
                                                  requests: list,
                                                  network: IconService) -> list:
        tx_hashes: list = []
        for req in requests:
            # Send the transaction to network
            tx_hashes.append(network.send_transaction(req))
        if self._block_confirm_interval > 0:
            sleep(self._block_confirm_interval)
        return tx_hashes

    def process_message_tx_without_txresult(self,
                                            network: IconService,
                                            from_: 'KeyWallet',
                                            to_: Union['KeyWallet', str],
                                            step_limit: int = 10_000_000_000,
                                            msg: str = "dummy") -> list:

        if isinstance(to_, KeyWallet):
            to_ = to_.get_address()

        msg_byte = msg.encode('utf-8')

        # build message tx
        transaction = MessageTransactionBuilder() \
            .from_(from_.get_address()) \
            .to(to_) \
            .step_limit(step_limit) \
            .nid(3) \
            .nonce(100) \
            .data(f"0x{msg_byte.hex()}") \
            .build()

        # signing message tx
        request = SignedTransaction(transaction, from_)
        tx_hashes: list = [network.send_transaction(request)]
        sleep(self._block_confirm_interval)
        return tx_hashes

    def get_txresults(self,
                      network: IconService,
                      tx_hashes: list) -> list:
        tx_results: list = []

        for h in tx_hashes:
            tx_result = network.get_transaction_result(h)
            tx_results.append(tx_result)
        return tx_results

    def mock_calculate(self, _path, _block_height):
        context: 'IconScoreContext' = IconScoreContext(IconScoreContextType.QUERY)
        end_block_height_of_calc: int = context.storage.iiss.get_end_block_height_of_calc(context)
        calc_period: int = context.storage.iiss.get_calc_period(context)
        response = CalculateDoneNotification(0, True, end_block_height_of_calc - calc_period, 0, b'mocked_response')
        self._calculate_done_callback(response)

    def _calculate_done_callback(self, _response: 'CalculateDoneNotification'):
        pass

    @classmethod
    def _mock_rc_proxy(cls, mock_calculate: callable = mock_calculate):
        RewardCalcProxy.open = Mock()
        RewardCalcProxy.start = Mock()
        RewardCalcProxy.stop = Mock()
        RewardCalcProxy.close = Mock()
        RewardCalcProxy.get_version = Mock()
        RewardCalcProxy.calculate = mock_calculate
        RewardCalcProxy.claim_iscore = Mock()
        RewardCalcProxy.query_iscore = Mock()
        RewardCalcProxy.commit_block = Mock()
        RewardCalcProxy.commit_claim = Mock()
        RewardCalcProxy.query_calculate_result = Mock(return_value=(RCCalculateResult.SUCCESS, 0, 0, bytes()))
