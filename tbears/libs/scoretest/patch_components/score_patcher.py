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
from functools import wraps
from inspect import getmembers, isfunction
from typing import Optional
from unittest.mock import Mock

from iconservice import IconScoreBase
from iconservice.base.address import AddressPrefix, Address
from iconservice.base.exception import PayableException
from iconservice.database.db import IconScoreDatabase
from iconservice.icon_constant import IconScoreContextType
from iconservice.iconscore.icon_score_constant import CONST_BIT_FLAG, ConstBitFlag
from iconservice.iconscore.icon_score_context import ContextContainer
from iconservice.iconscore.internal_call import InternalCall

from .context_manager import ContextManager
from ..mock_components.mock_db import MockKeyValueDatabase
from ..mock_components.mock_icx_engine import MockIcxEngine
from ...icon_integrate_test import create_tx_hash

context_db = MockKeyValueDatabase.create_db()
MockIcxEngine.db = context_db
InternalCall.icx_engine = MockIcxEngine()


def create_address(prefix: int = 0, data: bytes = None) -> 'Address':
    if data is None:
        data = create_tx_hash()
    hash_value = hashlib.sha3_256(data).digest()
    return Address(AddressPrefix(prefix), hash_value[-20:])


def _patch_score_method(method, context):
    @wraps(method)
    def patched(*args, **kwargs):
        ContextContainer._push_context(context)
        if context.type == IconScoreContextType.INVOKE:
            ContextManager.increase_tx_nonce()
            ContextManager.increase_tx_index()
        result = method(*args, **kwargs)
        ContextContainer._pop_context()
        return result
    return patched


def patch_score_method(method):

    @wraps(method)
    def patched(*args, **kwargs):
        context = ContextManager.context
        method_flag = getattr(method, CONST_BIT_FLAG, 0)
        score_class, method_name = method.__qualname__.split('.')

        if method_name == 'fallback':
            if not (method_flag & ConstBitFlag.Payable) and context.msg.value > 0:
                raise PayableException(f"This method is not payable", method_name, score_class)

        if bool(method_flag & ConstBitFlag.ReadOnly):
            ContextManager.set_context(IconScoreContextType.QUERY)
        elif (method_flag & ConstBitFlag.External) == ConstBitFlag.External:
            if context.msg.value > 0:
                raise PayableException(f"This method is not payable", method_name, score_class)
            if context.msg.sender is not None and not context.msg.sender.is_contract:
                ContextManager.set_transaction(context.tx.timestamp, context.tx.index,
                                               context.tx.nonce, (args, kwargs))
                ContextManager.set_context(IconScoreContextType.INVOKE)
        elif method_flag & ConstBitFlag.Payable:
            ContextManager.set_transaction(context.tx.timestamp, context.tx.index, context.tx.nonce, (args, kwargs))
            ContextManager.set_context(IconScoreContextType.INVOKE)
            MockIcxEngine.transfer(context, context.msg.sender, context.current_address, context.msg.value)
        elif method_name in ('on_install', 'on_update'):
            ContextManager.set_transaction(context.tx.timestamp, context.tx.index, context.tx.nonce), (args, kwargs)
            ContextManager.set_context(IconScoreContextType.INVOKE)

        patched_method = _patch_score_method(method, context)
        result = patched_method(*args, **kwargs)
        return result

    return patched


class SCOREPatcher:

    @staticmethod
    def get_score_db(score_address: Optional['Address']=None):
        if not score_address:
            score_address = create_address(1)
        score_db = IconScoreDatabase(score_address, context_db)
        return score_db

    @staticmethod
    def initialize_score(score_class, score_db, owner: 'Address'):
        original_get_owner = IconScoreBase.get_owner
        IconScoreBase.get_owner = Mock(return_value=owner)
        score = score_class(score_db)
        IconScoreBase.get_owner = original_get_owner

        SCOREPatcher.patch_score_methods(score, owner, 0)
        return score

    @staticmethod
    def patch_score_methods(score, sender: 'Address'=None, value: int=0, tx_timestamp: Optional[int]=None,
                            block_height: Optional[int]=None):
        SCOREPatcher._set_context(score, sender, value, tx_timestamp, block_height)

        custom_methods = SCOREPatcher.get_custom_methods(score.__class__)
        for m in custom_methods:
            name = m.__qualname__.split('.')[1]
            method = getattr(score, name)
            setattr(score, name, patch_score_method(method))

    @staticmethod
    def _set_context(score, sender: 'Address'=None, value: int=0, tx_timestamp: Optional[int]=None,
                     index: Optional[int]=None, nonce: Optional[int]=None, block_height: Optional[int]=None,
                     context_type: Optional['IconScoreContextType']=None, step_price: int=0, step_costs: dict={},
                     step_limit: int=2_013_265_920):
        ContextManager.context.current_address = score.address
        ContextManager.set_message(sender, value)
        ContextManager.set_block(block_height)
        ContextManager.set_transaction(tx_timestamp, index, nonce)
        ContextManager.validate_timestamp(tx_timestamp)

        ContextManager.set_step_counter(step_costs, step_limit, step_price)

        if context_type is not None:
            ContextManager.strict = True
            ContextManager.set_context(context_type)
        else:
            ContextManager.strict = False


    @staticmethod
    def get_custom_methods(score):
        custom_methods = [method for key, method in getmembers(score, predicate=isfunction)
                          if method.__qualname__.split('.')[0] != 'IconScoreBase']
        methods = set()
        for method in custom_methods:
            if getattr(method, CONST_BIT_FLAG, 0) in (0, 1, 2, 3, 4) or method.__name__ in ('on_install', 'on_update'):
                methods.add(method)

        methods.add(getattr(score, 'fallback'))
        return methods

