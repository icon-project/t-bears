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
import os
from functools import wraps
from inspect import getmembers, isfunction
from typing import Optional
from unittest.mock import Mock, patch

from iconservice import InterfaceScore
from iconservice.base.address import Address, AddressPrefix
from iconservice.base.exception import InvalidPayableException, InvalidInterfaceException, InvalidRequestException
from iconservice.database.db import IconScoreDatabase
from iconservice.icon_constant import IconScoreFuncType, IconScoreContextType
from iconservice.iconscore.icon_score_base import IconScoreBase
from iconservice.iconscore.icon_score_constant import CONST_BIT_FLAG, ConstBitFlag, FORMAT_IS_NOT_DERIVED_OF_OBJECT
from iconservice.iconscore.icon_score_context import IconScoreContext, ContextGetter

from .context import Context, score_mapper, interface_score_mapper
from ..mock.db import MockKeyValueDatabase
from ..mock.icx_engine import IcxEngine

context_db = None
CONTEXT_PATCHER = patch('iconservice.iconscore.icon_score_context.ContextGetter._context')


def create_address(prefix: AddressPrefix=AddressPrefix.EOA) -> 'Address':
    return Address.from_bytes(prefix.to_bytes(1, 'big') + os.urandom(20))


def patch_score_method(method):
    """Patch SCORE method.
    Refer to the decorator and patch the method to have the appropriate context

    :param method: method to patch
    :return: patched method
    """

    @wraps(method)
    def patched(*args, **kwargs):
        context: 'Mock' = ContextGetter._context
        method_flag = getattr(method, CONST_BIT_FLAG, 0)
        score_class, method_name = method.__qualname__.split('.')
        context.current_address = method.__self__.address

        if method_name == 'fallback':
            if not (method_flag & ConstBitFlag.Payable) and context.msg.value > 0:
                raise InvalidPayableException(f"This method is not payable")

        if method_flag & ConstBitFlag.ReadOnly == ConstBitFlag.ReadOnly:
            Context._set_query_context(context)
        else:
            Context._set_invoke_context(context)
        if method_flag & ConstBitFlag.Payable:
            IcxEngine.transfer(context, context.msg.sender, context.current_address, context.msg.value)

        context.readonly = context.type == IconScoreContextType.QUERY or context.func_type == IconScoreFuncType.READONLY

        result = method(*args, **kwargs)
        return result

    return patched


def get_interface_score(score_address):
    try:
        interface_score = interface_score_mapper[score_address]
    except KeyError:
        raise InvalidInterfaceException(FORMAT_IS_NOT_DERIVED_OF_OBJECT.format(InterfaceScore.__name__))
    else:
        return interface_score


def new_create_interface_score(score_address, interface_score):
    """Hooking method for SCORE.create_interface_score

    :param score_address: address of internal call SCORE
    :param interface_score:
    :return: mock instance
    """
    return get_interface_score(score_address)


class ScorePatcher:

    @staticmethod
    def get_score_db(score_address: Optional['Address']=None):
        """Get db of SCORE that having score_address.
        create cx prefixed address and set it as SCORE's address if score_address is None

        :param score_address: address of score.
        :return: db SCORE use
        """
        global context_db
        if not score_address:
            score_address = create_address(AddressPrefix.CONTRACT)
        score_db = IconScoreDatabase(score_address, context_db)
        return score_db

    @staticmethod
    def initialize_score(score_class, score_db, owner: 'Address'):
        """Get an instance of the SCORE class passed as an score_class arguments

        :param score_class: SCORE class to instantiate
        :param score_db: database the SCORE use
        :param owner: owner of SCORE
        :return: Instantiated SCORE
        """
        original_get_owner = IconScoreBase.get_owner
        IconScoreBase.get_owner = Mock(return_value=owner)
        score = score_class(score_db)
        IconScoreBase.get_owner = original_get_owner
        context = Context.get_context()
        ScorePatcher._set_mock_context(context)
        Context.set_msg(owner, 0)
        ScorePatcher.patch_score_methods(score)
        ScorePatcher.patch_score_event_logs(score)
        ScorePatcher.patch_interface_scores(score)
        score_mapper[score.address] = score
        return score

    @staticmethod
    def _set_mock_context(context: 'IconScoreContext'):
        mock_context = Mock(spec=IconScoreContext)
        mock_context.configure_mock(msg=context.msg)
        mock_context.configure_mock(tx=context.tx)
        mock_context.configure_mock(block=context.block)
        mock_context.configure_mock(step_counter=None)
        mock_context.configure_mock(type=context.type)
        mock_context.configure_mock(func_type=context.func_type)
        mock_context.configure_mock(current_address=context.current_address)
        mock_context.configure_mock(block_batch=context.block_batch)
        mock_context.configure_mock(tx_batch=context.tx_batch)
        mock_context.configure_mock(event_logs=context.event_logs)
        mock_context.configure_mock(event_log_stack=context.event_log_stack)
        mock_context.configure_mock(traces=context.traces)
        mock_context.configure_mock(icon_score_mapper=context.icon_score_mapper)
        ContextGetter._context = mock_context

    @staticmethod
    def patch_score_methods(score):
        """Patch all SCORE method by calling patch_score_method function

        :param score: SCORE to be patched
        """
        custom_methods = ScorePatcher.get_custom_methods(score.__class__)
        for custom_method in custom_methods:
            name = custom_method.__qualname__.split('.')[1]
            method = getattr(score, name)
            setattr(score, name, patch_score_method(method))

    @staticmethod
    def get_custom_methods(score):
        """Get user defined methods inside SCORE

        :param score: SCORE to get the custom method
        :return: user defined methods inside SCORE
        """
        custom_methods = ScorePatcher._get_custom_methods(score)
        methods = set()
        for method in custom_methods:
            if getattr(method, CONST_BIT_FLAG, 0) in (0, 1, 2, 3, 4) or method.__name__ in ('on_install', 'on_update'):
                methods.add(method)

        methods.add(getattr(score, 'fallback'))
        return methods

    @staticmethod
    def _get_custom_methods(score):
        custom_methods = [method for key, method in getmembers(score, predicate=isfunction)
                          if method.__qualname__.split('.')[0] != 'IconScoreBase']
        return custom_methods

    @staticmethod
    def register_interface_score(internal_score_address: Address):
        """Register interface SCORE. This method must be called before testing internal call(Calling other SCORE method)

        :param internal_score_address: address of internal call SCORE
        """
        if not internal_score_address.is_contract:
            raise InvalidRequestException(f"{internal_score_address} is not SCORE")
        interface_score_mapper[internal_score_address] = Mock()

    @staticmethod
    def patch_interface_scores(score):
        """Patch internal call SCORE with mock instance"""
        setattr(score, 'create_interface_score', new_create_interface_score)

    @staticmethod
    def patch_internal_method(internal_score_address, method, new_method):
        """Patch internal method with given 'new_method'

        :param internal_score_address: address of the SCORE having method to be called
        :param method: method to be patched
        :param new_method: method to patch
        """
        interface_score = get_interface_score(internal_score_address)
        setattr(interface_score, method, Mock(side_effect=new_method))

    @staticmethod
    def patch_score_event_logs(score):
        """Patch all event_logs inside SCORE

        :param score: SCORE to be patched
        """
        custom_methods = ScorePatcher._get_custom_methods(score.__class__)
        for method in custom_methods:
            if getattr(method, CONST_BIT_FLAG, 0) == ConstBitFlag.EventLog:
                setattr(score, method.__name__, Mock())

    @staticmethod
    def start_patches():
        """Patch SCORE to use dictionary DB instance of LEVEL DB"""

        global context_db
        context_db = MockKeyValueDatabase.create_db()
        IcxEngine.db = context_db
        CONTEXT_PATCHER.start()

    @staticmethod
    def stop_patches():
        """Stop patching and clear db"""

        CONTEXT_PATCHER.stop()
        IcxEngine.db.close()
        score_mapper.clear()
        interface_score_mapper.clear()
