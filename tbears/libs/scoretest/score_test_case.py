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
from iconservice.base.exception import InvalidRequestException
from iconservice.iconscore.icon_score_context import ContextGetter

from .mock_components.mock_icx_engine import MockIcxEngine
from .patch_components.context import Context, get_icon_score
from .patch_components.score_patcher import ScorePatcher, create_address, get_interface_score

T = TypeVar('T')


def validate_score(score):
    if issubclass(score, IconScoreBase) is False:
        raise InvalidRequestException(f"{score.__name__} is invalid SCORE class")


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
        Context.initialize_variables()

    def tearDown(self):
        Context.reset_context()
        ScorePatcher.stop_patches()

    @staticmethod
    def get_score_instance(score_class: Type[T], owner: 'Address', on_install_params: dict={}) -> T:
        """Get an instance of the SCORE class passed as an score_class arguments

        :param score_class: SCORE class to instantiate
        :param owner: owner of SCORE
        :param on_install_params: parameters of on_install method
        :return: Initialized SCORE
        """
        validate_score(score_class)
        score_db = ScorePatcher.get_score_db()
        score = ScorePatcher.initialize_score(score_class, score_db, owner)
        score.on_install(**on_install_params)
        ScoreTestCase.set_msg(None, None)
        return score

    @staticmethod
    def update_score(prev_score_address: 'Address', score_class: Type[T], on_update_params: dict={})->T:
        """Update SCORE at 'prev_score_address' with 'score_class' instance and get updated SCORE

        :param prev_score_address: address of SCORE to update
        :param score_class: SCORE class to update
        :param on_update_params: parameters of on_update method
        :return: Updated SCORE
        """
        validate_score(score_class)
        prev_score = get_icon_score(prev_score_address)
        score_db = ScorePatcher.get_score_db(prev_score.address)
        score = ScorePatcher.initialize_score(score_class, score_db, prev_score.owner)
        score.on_update(**on_update_params)
        ScoreTestCase.set_msg(None, None)
        return score

    @staticmethod
    def set_msg(sender: Optional['Address']=None, value: int=0):
        """Sets msg property used inside SCORE

        :param sender: Set sender attribute of msg to given sender argument
        :param value: Set value attribute of msg to given value argument
        """
        Context.set_msg(sender, value)

    @staticmethod
    def set_tx(origin: Optional['Address']=None, timestamp: Optional[int]=None, _hash: bytes=None,
               index: int=0, nonce: int=0):
        """Sets tx property used inside SCORE

        :param origin: Set origin attribute of tx to given origin argument
        :param timestamp: Set timestamp attribute of tx to given timestamp argument
        :param _hash: Set hash attribute of tx to given _hash argument
        :param index: Set index attribute of tx to given index argument
        :param nonce: Set nonce attribute of tx to given nonce argument
        """
        Context.set_tx(origin, timestamp, _hash, index, nonce)

    @staticmethod
    def set_block(height: int=0, timestamp: Optional[int]=None):
        """Sets block property used inside SCORE

        :param height: Set height attribute of block to given height argument
        :param timestamp: Set timestamp attribute of block to given timestamp argument
        """
        Context.set_block(height, timestamp)

    @staticmethod
    def register_interface_score(internal_score_address):
        """Register interface SCORE. This method must be called before testing internal call(Calling other SCORE method)

        :param internal_score_address: address of interface SCORE
        """
        ScorePatcher.register_interface_score(internal_score_address)

    @staticmethod
    def patch_internal_method(score_address, method, new_method=lambda: None):
        """Patch internal method with given 'new_method'
        This method call register_interface_score method. so, don't need to call register_interface_score method
        if this method called.

        :param score_address: address of the SCORE having method to be called
        :param method: method to be patched
        :param new_method: method to patch
        """
        ScorePatcher.register_interface_score(score_address)
        ScorePatcher.patch_internal_method(score_address, method, new_method)

    @staticmethod
    def assert_internal_call(internal_score_address, method, *params):
        """assert that internal call(mock) was called with the specified arguments.
        Raises an AssertionError if the params passed in are
        different to the last call to the mock.

        :param internal_score_address: address of internal call SCORE
        :param method: method to check
        :param params: params to check
        """
        interface_score = get_interface_score(internal_score_address)
        internal_method = getattr(interface_score, method)
        internal_method.assert_called_with(*params)

    @staticmethod
    def transfer(_from: 'Address', to: 'Address', amount: int):
        """Transfer icx to given 'to' address

        :param _from: address of sender
        :param to: address of receiver
        :param amount: amount to transfer
        """
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
        """Query icx balance of given address

        :param address: address to query for icx balance
        :return: icx balance of given address
        """
        return MockIcxEngine.get_balance(None, address)

    @staticmethod
    def initialize_accounts(accounts_info: dict):
        """Initialize accounts using given dictionary info

        :param accounts_info: dictionary with address as key and balance as value
        """
        for account, amount in accounts_info.items():
            MockIcxEngine.db.put(None, account.to_bytes(), amount)
