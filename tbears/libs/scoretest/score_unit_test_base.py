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
from typing import TypeVar, Type, Optional
from unittest import TestCase
from unittest.mock import Mock

from iconservice.base.address import Address
from iconservice.icon_constant import IconScoreContextType
from iconservice.iconscore.icon_score_context import IconScoreContext

from .mock_components.mock_icx_engine import MockIcxEngine
from .patch_components.context_manager import score_mapper, ContextManager, initial_costs
from .patch_components.score_patcher import SCOREPatcher, create_address

T = TypeVar('T')


class SCOREUnitTestBase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.genesis_address = create_address(0)
        cls.test_account1 = create_address(0)
        cls.test_account2 = create_address(0)
        account_info = {cls.genesis_address: 10**30,
                        cls.test_account1: 10**21,
                        cls.test_account2: 10**21}
        SCOREUnitTestBase.initialize_accounts(account_info)
        SCOREUnitTestBase.set_revision()

    @staticmethod
    def send_icx(_from: 'Address', to: 'Address', amount: int):
        if to.is_contract:
            _sender, _to, _value = ContextManager.context.msg.sender, ContextManager.context.current_address, \
                                   ContextManager.context.msg.value
            SCOREUnitTestBase.set_context(score_mapper[to], _from, amount)
            score_mapper[to].fallback()
            SCOREUnitTestBase.set_context(score_mapper[_to], _sender, _value)
        else:
            MockIcxEngine.transfer(None, _from, to, amount)

    @staticmethod
    def get_balance(address: 'Address'):
        return MockIcxEngine.get_balance(None, address)

    @staticmethod
    def initialize_accounts(accounts_info: dict):
        for account, amount in accounts_info.items():
            MockIcxEngine.db.put(None, account.to_bytes(), amount)

    @staticmethod
    def set_context(score, sender: 'Address'=None, msg_value: int=0, tx_timestamp: Optional[int]=None,
                    tx_index: Optional[int]=None, nonce: Optional[int]=None, block_height: Optional[int]=None,
                    context_type: Optional[IconScoreContextType]=None, step_price: int=0,
                    step_price_dict: dict=initial_costs, step_limit: int=2_013_265_920):
        SCOREPatcher._set_context(score, sender, msg_value, tx_timestamp, tx_index, nonce, block_height, context_type,
                                  step_price, step_price_dict, step_limit)

    @staticmethod
    def get_score_instance(score_class: Type[T], owner: 'Address', on_install_params: dict={}) -> T:
        score_db = SCOREPatcher.get_score_db()
        score = SCOREPatcher.initialize_score(score_class, score_db, owner)
        score.on_install(**on_install_params)
        score_mapper[score.address] = score
        return score

    @staticmethod
    def update_score(prev_score_address: 'Address', score: Type[T], on_update_params: dict={})->T:
        score_db = SCOREPatcher.get_score_db(prev_score_address)
        score = SCOREPatcher.initialize_score(score, score_db, score_mapper[prev_score_address].owner)
        score.on_update(**on_update_params)
        score_mapper[score.address] = score
        return score

    @staticmethod
    def set_revision(revision: int=99):
        IconScoreContext.get_revision = Mock(return_value=revision)
