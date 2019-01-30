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

from iconservice import IconScoreBase
from iconservice.base.address import Address
from iconservice.iconscore.icon_score_context import IconScoreContext, ContextGetter
from iconservice.iconscore.internal_call import InternalCall

from .mock_components.mock_icx_engine import MockIcxEngine
from .patch_components.context_util import ContextUtil, get_icon_score
from .patch_components.score_patcher import SCOREPatcher, create_address

T = TypeVar('T')


class SCOREUnitTestBase(TestCase):

    def setUp(self):
        SCOREPatcher.start_patches()
        self.genesis_address = create_address(0)
        self.test_account1 = create_address(0)
        self.test_account2 = create_address(0)
        account_info = {self.genesis_address: 10**30,
                        self.test_account1: 10**21,
                        self.test_account2: 10**21}
        SCOREUnitTestBase.initialize_accounts(account_info)

    def tearDown(self):
        ContextUtil.reset_context()
        SCOREPatcher.stop_patches()

    @staticmethod
    def transfer(_from: 'Address', to: 'Address', amount: int):
        if to.is_contract:
            sender = ContextGetter._context.msg.sender
            value = ContextGetter._context.msg.value
            ContextUtil.set_sender(_from)
            ContextUtil.set_value(amount)
            score = get_icon_score(to)
            score.fallback()
            ContextUtil.set_sender(sender)
            ContextUtil.set_value(value)
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
    def set_context(context: 'IconScoreContext'):
        SCOREPatcher._set_mock_context(context)

    @staticmethod
    def set_sender(sender: Optional['Address']=None):
        ContextUtil.set_sender(sender)

    @staticmethod
    def set_value(value: Optional[int]=0):
        ContextUtil.set_value(value)

    @staticmethod
    def set_block_height(height: int=0):
        ContextUtil.set_block_height(height)

    @staticmethod
    def get_score_instance(score_class: Type[T], owner: 'Address', on_install_params: dict={}) -> T:
        score_db = SCOREPatcher.get_score_db()
        score = SCOREPatcher.initialize_score(score_class, score_db, owner)
        score.on_install(**on_install_params)
        return score

    @staticmethod
    def update_score(prev_score: 'IconScoreBase', score_class: Type[T], on_update_params: dict={})->T:
        score_db = SCOREPatcher.get_score_db(prev_score.address)
        score = SCOREPatcher.initialize_score(score_class, score_db, prev_score.owner)
        score.on_update(**on_update_params)
        return score

    @staticmethod
    def assert_internal_call(from_score, to_score, function_name, params):
        external_call = InternalCall.other_external_call
        external_call.assert_called()

        match = False
        for call_args in external_call.call_args_list:
            if call_args[0][0] == from_score and call_args[0][1] == to_score and call_args[0][2] == function_name:
                param_match = True
                for index, param in enumerate(params):
                    if call_args[0][3][index] != param:
                        param_match = False
                        break
                if param_match:
                    match = True
                    break

        assert match is True

