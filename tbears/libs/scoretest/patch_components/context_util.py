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
from typing import Optional, TYPE_CHECKING
from unittest.mock import Mock

from iconservice import IconScoreBase
from iconservice.base.exception import InvalidParamsException
from iconservice.base.message import Message
from iconservice.base.transaction import Transaction
from iconservice.icon_constant import IconScoreContextType, IconScoreFuncType
from iconservice.iconscore.icon_score_context import IconScoreContext, ContextGetter
from iconservice.iconscore.internal_call import InternalCall

from tbears.libs.icon_integrate_test import create_tx_hash
from tbears.libs.scoretest.mock_components.mock_icx_engine import MockIcxEngine
from ..mock_components.mock_block import MockBlock

if TYPE_CHECKING:
    from iconservice.base.address import Address

score_mapper = {}


def get_icon_score(address: 'Address'):
    if address.is_contract is False:
        raise InvalidParamsException(f"{address} is not SCORE")
    elif isinstance(score_mapper.get(address, None), IconScoreBase) is False:
        raise InvalidParamsException(f"{address} is not active SCORE")
    return score_mapper[address]


def get_balance(self: 'InternalCall', address: 'Address'):
    return MockIcxEngine.get_balance(None, address)


def transfer(self: 'InternalCall', _from: 'Address', _to: 'Address', amount: int):
    MockIcxEngine.transfer(ContextGetter._context, _from, _to, amount)


def get_default_context(context: 'IconScoreContext'):
    block = MockBlock()
    context.block = block
    context.icon_score_mapper = score_mapper
    context.traces = []
    context.validate_score_blacklist = Mock(return_value=True)
    context.tx = Transaction()
    context.msg = Message()
    context.get_icon_score = Mock(side_effect=get_icon_score)
    context.block_batch = None
    context.tx_batch = None
    return context


InternalCall.get_icx_balance = get_balance
InternalCall.icx_transfer_call = transfer
InternalCall.other_external_call = Mock()


class ContextUtil:
    context = get_default_context(IconScoreContext())

    @classmethod
    def set_context(cls, sender: 'Address'=None, value: int=0, tx_timestamp: Optional[int]=None,
                    block_height: int=0, func_type: 'IconScoreFuncType'=IconScoreFuncType.READONLY,
                    context_type: 'IconScoreContextType'=IconScoreContextType.QUERY):
        cls._set_block(cls.context, block_height)
        cls._set_message(cls.context, sender, value)
        cls._set_transaction(cls.context, tx_timestamp)
        cls._set_func_type(cls.context, func_type)
        cls._set_context_type(cls.context, context_type)

    @classmethod
    def get_context(cls):
        return cls.context

    @staticmethod
    def _set_invoke_context(context):
        context.configure_mock(type=IconScoreContextType.INVOKE)
        context.configure_mock(event_logs=[])
        context.configure_mock(func_type=IconScoreFuncType.WRITABLE)

    @staticmethod
    def _set_query_context(context):
        context.configure_mock(type=IconScoreContextType.QUERY)
        context.configure_mock(func_type=IconScoreFuncType.READONLY)

    @classmethod
    def set_sender(cls, sender: Optional['Address']):
        context = cls.context = ContextGetter._context
        msg = context.msg
        tx = context.tx
        msg.sender = sender
        tx._origin = sender
        context.configure_mock(msg=msg)
        context.configure_mock(tx=tx)

    @classmethod
    def set_value(cls, value):
        context = cls.context = ContextGetter._context
        msg = context.msg
        msg.value = value
        context.configure_mock(msg=msg)

    @classmethod
    def set_block_height(cls, height):
        context = cls.context = ContextGetter._context
        block = context.block
        block._height = height

    @staticmethod
    def _set_block(context, height: int=0):
        context.block._height = height

    @staticmethod
    def _set_message_sender(context, sender: Optional['Address']):
        context.msg.sender = sender

    @staticmethod
    def _set_message_value(context, value: int=0):
        context.msg.value = value

    @staticmethod
    def _set_message(context, sender: Optional['Address'], value: int=0):
        ContextUtil._set_message_sender(context, sender)
        ContextUtil._set_message_value(context, value)

    @staticmethod
    def _set_transaction(context, timestamp: Optional[int]=None):
        tx = context.tx
        tx._timestamp = context.block.timestamp if timestamp is None else timestamp
        tx._origin = context.msg.sender
        tx._index = None
        tx._nonce = None
        tx._hash = create_tx_hash()

    @staticmethod
    def _set_func_type(context: 'IconScoreContext', func_type: 'IconScoreFuncType'=IconScoreFuncType.WRITABLE):
        context.func_type = func_type

    @staticmethod
    def _set_context_type(context: 'IconScoreContext',
                          context_type: 'IconScoreContextType'=IconScoreContextType.INVOKE):
        context.type = context_type
