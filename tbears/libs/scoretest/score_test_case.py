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
from typing import TypeVar, Type, Optional, List
from unittest import TestCase
from unittest.mock import Mock, patch

from iconservice import IconScoreBase
from iconservice.base.address import Address
from iconservice.base.exception import InvalidRequestException
from iconservice.iconscore.context.context import ContextGetter
from iconservice.iconscore.icon_score_base2 import PRepInfo

from .mock.icx_engine import IcxEngine
from .patch.context import Context, get_icon_score
from .patch.score_patcher import ScorePatcher, create_address, get_interface_score, start_SCORE_APIs_patch

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
    def get_score_instance(score_class: Type[T], owner: 'Address', on_install_params: dict = {},
                           score_address: Optional[Address] = None) -> T:
        """Get an instance of the SCORE class passed as an score_class arguments

        :param score_class: SCORE class to instantiate
        :param owner: Address to set as owner of SCORE
        :param on_install_params: To be passed to the SCORE on_install method
        :param score_address: score address
        :return: Initialized SCORE
        """
        validate_score(score_class)
        score_db = ScorePatcher.get_score_db(score_address)
        score = ScorePatcher.initialize_score(score_class, score_db, owner)
        setattr(score, "call", Mock())
        score.on_install(**on_install_params)
        ScoreTestCase.set_msg(None, None)
        start_SCORE_APIs_patch(score_class.__module__)
        return score

    @staticmethod
    def update_score(prev_score_address: 'Address', score_class: Type[T], on_update_params: dict = {}) -> T:
        """Update SCORE at 'prev_score_address' with 'score_class' instance and get updated SCORE

        :param prev_score_address: address of SCORE to update
        :param score_class: SCORE class to update
        :param on_update_params: To be passed to the SCORE on_update method
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
    def set_msg(sender: Optional['Address'] = None, value: int = 0):
        """Set msg property used inside SCORE

        :param sender: sender attribute of msg
        :param value: value attribute of msg
        """
        Context.set_msg(sender, value)

    @staticmethod
    def set_tx(origin: Optional['Address'] = None, timestamp: Optional[int] = None, _hash: bytes = None,
               index: int = 0, nonce: int = 0):
        """Set tx property used inside SCORE

        :param origin: origin attribute of tx
        :param timestamp: timestamp attribute of tx
        :param _hash: hash attribute of tx
        :param index: index attribute of tx
        :param nonce: nonce attribute of tx
        """
        Context.set_tx(origin, timestamp, _hash, index, nonce)

    @staticmethod
    def set_block(height: int = 0, timestamp: Optional[int] = None):
        """Sets block property used inside SCORE

        :param height: height attribute of block
        :param timestamp: timestamp attribute of block
        """
        Context.set_block(height, timestamp)

    @staticmethod
    def register_interface_score(internal_score_address):
        """Register interface SCORE. This method must be called before testing internal call

        :param internal_score_address: address of interface SCORE
        """
        ScorePatcher.register_interface_score(internal_score_address)

    @staticmethod
    def patch_internal_method(internal_score_address, method, new_method=lambda: None):
        """Patch method of SCORE on internal_score_address with given method

        This method call register_interface_score method. so, don't need to call register_interface_score method
        if this method called.

        :param internal_score_address: address of the SCORE having method to be called
        :param method: method to be patched
        :param new_method: method to patch
        """
        ScorePatcher.register_interface_score(internal_score_address)
        ScorePatcher.patch_internal_method(internal_score_address, method, new_method)

    @staticmethod
    def patch_call(score_instance, new_method=lambda: None):
        """Patch IconScoreBase.call method. This method must be called if score.call querying other SCORE's method

        :param score_instance: score instance to patch
        :param new_method: method to patch
        """
        setattr(score_instance, "call", Mock(side_effect=new_method))

    @staticmethod
    def assert_internal_call(internal_score_address, method, *params):
        """Assert internal call was called with the specified arguments.

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
            IcxEngine.transfer(None, _from, to, amount)

    @staticmethod
    def get_balance(address: 'Address'):
        """Query icx balance of given address

        :param address: address to query for icx balance
        :return: icx balance of given address
        """
        return IcxEngine.get_balance(None, address)

    @staticmethod
    def initialize_accounts(accounts_info: dict):
        """Initialize accounts using given dictionary info

        :param accounts_info: dictionary with address as key and balance as value
        """
        for account, amount in accounts_info.items():
            IcxEngine.db.put(None, account.to_bytes(), amount)

    @staticmethod
    def patch_main_preps(module: str, prep_info_list: List[PRepInfo]):
        patch(f"{module}.get_main_prep_info", return_value=(prep_info_list, int)).start()

    @staticmethod
    def patch_sub_preps(module: str, prep_info_list: List[PRepInfo]):
        patch(f"{module}.get_main_prep_info", return_value=(prep_info_list, int)).start()
