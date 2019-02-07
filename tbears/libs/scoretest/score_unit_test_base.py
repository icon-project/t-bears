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

from iconservice.base.address import Address
from iconservice.iconscore.icon_score_context import ContextGetter

from .mock_components.mock_icx_engine import MockIcxEngine
from .patch_components.context_util import Context, get_icon_score
from .patch_components.score_patcher import ScorePatcher, create_address, get_interface_score

T = TypeVar('T')


class ScoreTestCase(TestCase):

    def setUp(self):
        ScorePatcher.start_patches()
        self.genesis_address = create_address()
        self.test_account1 = create_address()
        self.test_account2 = create_address()
        account_info = {self.genesis_address: 10**30,
                        self.test_account1: 10**21,
                        self.test_account2: 10**21}
        ScoreTestCase.initialize_accounts(account_info)

    def tearDown(self):
        Context.reset_context()
        ScorePatcher.stop_patches()

    @staticmethod
    def transfer(_from: 'Address', to: 'Address', amount: int):
        if to.is_contract:
            sender = ContextGetter._context.msg.sender
            value = ContextGetter._context.msg.value
            Context.set_msg(_from, amount)
            score = get_icon_score(to)
            score.fallback()
            Context.set_msg(sender, value)
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
    def set_msg(sender: Optional['Address']=None, value: int=0):
        Context.set_msg(sender, value)

    @staticmethod
    def set_tx(origin: Optional['Address']=None, timestamp: Optional[int]=None, _hash: bytes=None,
               index: int=0, nonce: int=0):
        Context.set_tx(origin, timestamp, _hash, index, nonce)

    @staticmethod
    def set_block(height: int=0, timestamp: Optional[int]=None):
        Context.set_block(height, timestamp)

    @staticmethod
    def get_score_instance(score_class: Type[T], owner: 'Address', on_install_params: dict={}) -> T:
        score_db = ScorePatcher.get_score_db()
        score = ScorePatcher.initialize_score(score_class, score_db, owner)
        score.on_install(**on_install_params)
        return score

    @staticmethod
    def update_score(prev_score_address: 'Address', score_class: Type[T], on_update_params: dict={})->T:
        prev_score = get_icon_score(prev_score_address)
        score_db = ScorePatcher.get_score_db(prev_score.address)
        score = ScorePatcher.initialize_score(score_class, score_db, prev_score.owner)
        score.on_update(**on_update_params)
        return score

    @staticmethod
    def register_interface_score(internal_score_address):
        ScorePatcher.register_interface_score(internal_score_address)

    @staticmethod
    def patch_internal_method(score_address, method, new_method=lambda: None):
        ScorePatcher.register_interface_score(score_address)
        ScorePatcher.patch_internal_method(score_address, method, new_method)

    @staticmethod
    def assert_internal_call(internal_score_address, method, *params):
        interface_score = get_interface_score(internal_score_address)
        internal_method = getattr(interface_score, method)
        internal_method.assert_called_with(*params)
