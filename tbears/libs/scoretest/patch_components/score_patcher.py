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
from unittest.mock import Mock, patch

from iconservice.base.address import AddressPrefix, Address
from iconservice.base.exception import PayableException
from iconservice.database.db import IconScoreDatabase
from iconservice.iconscore.icon_score_base import IconScoreBase
from iconservice.iconscore.icon_score_constant import CONST_BIT_FLAG, ConstBitFlag
from iconservice.iconscore.icon_score_context import IconScoreContext, ContextGetter

from .context_util import ContextUtil, score_mapper
from ..mock_components.mock_db import MockKeyValueDatabase
from ..mock_components.mock_icx_engine import MockIcxEngine
from ....libs.icon_integrate_test import create_tx_hash

context_db = None
CONTEXT_PATCHER = patch('iconservice.iconscore.icon_score_context.ContextGetter._context')


def create_address(prefix: int = 0, data: bytes = None) -> 'Address':
    if data is None:
        data = create_tx_hash()
    hash_value = hashlib.sha3_256(data).digest()
    return Address(AddressPrefix(prefix), hash_value[-20:])


def patch_score_method(method):

    @wraps(method)
    def patched(*args, **kwargs):
        context = ContextGetter._context
        method_flag = getattr(method, CONST_BIT_FLAG, 0)
        score_class, method_name = method.__qualname__.split('.')
        context.configure_mock(current_address=method.__self__.address)

        if method_name == 'fallback':
            if not (method_flag & ConstBitFlag.Payable) and context.msg.value > 0:
                raise PayableException(f"This method is not payable", method_name, score_class)

        if method_flag & ConstBitFlag.ReadOnly == ConstBitFlag.ReadOnly:
            ContextUtil._set_query_context(context)
        elif (method_flag & ConstBitFlag.External) == ConstBitFlag.External:
            ContextUtil._set_invoke_context(context)
            if context.msg.value > 0:
                raise PayableException(f"This method is not payable", method_name, score_class)
        elif method_flag & ConstBitFlag.Payable:
            ContextUtil._set_invoke_context(context)
            MockIcxEngine.transfer(context, context.msg.sender, context.current_address, context.msg.value)
        elif method_name in ('on_install', 'on_update'):
            ContextUtil._set_invoke_context(context)

        result = method(*args, **kwargs)
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
        ContextUtil.set_context(owner, 0)
        context = ContextUtil.get_context()
        SCOREPatcher.set_context(context)
        SCOREPatcher.patch_score_methods(score)
        SCOREPatcher.patch_score_event_logs(score)
        score_mapper[score.address] = score
        return score

    @staticmethod
    def set_context(context: 'IconScoreContext'):
        SCOREPatcher._set_mock_context(context)

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
        mock_context.configure_mock(staces=context.traces)
        mock_context.configure_mock(icon_score_mapper=context.icon_score_mapper)
        mock_context.configure_mock(internal_call=context.internal_call)
        ContextGetter._context = mock_context

    @staticmethod
    def patch_score_methods(score):
        custom_methods = SCOREPatcher.get_custom_methods(score.__class__)
        for m in custom_methods:
            name = m.__qualname__.split('.')[1]
            method = getattr(score, name)
            setattr(score, name, patch_score_method(method))

    @staticmethod
    def get_custom_methods(score):
        custom_methods = SCOREPatcher._get_custom_methods(score)
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
    def patch_score_event_logs(score):
        custom_methods = SCOREPatcher._get_custom_methods(score.__class__)
        for method in custom_methods:
            if getattr(method, CONST_BIT_FLAG, 0) == ConstBitFlag.EventLog:
                setattr(score, method.__name__, Mock())

    @staticmethod
    def start_patches():
        global context_db
        context_db = MockKeyValueDatabase.create_db()
        MockIcxEngine.db = context_db
        CONTEXT_PATCHER.start()

    @staticmethod
    def stop_patches():
        CONTEXT_PATCHER.stop()
        MockIcxEngine.db.close()
        score_mapper.clear()
