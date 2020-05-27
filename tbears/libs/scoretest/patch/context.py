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
from iconservice.iconscore.icon_score_context_util import IconScoreContextUtil
from iconservice.iconscore.internal_call import InternalCall

from ..mock.block import Block
from ....libs.icon_integrate_test import create_tx_hash
from ....libs.scoretest.mock.icx_engine import IcxEngine

if TYPE_CHECKING:
    from iconservice.base.address import Address

score_mapper = {}
interface_score_mapper = {}


def get_icon_score(address: 'Address'):
    """This method will be called when SCORE call get_icon_score method while test using score-unittest-framework

    :param address: address of SCORE
    :return: SCORE
    """
    if address.is_contract is False:
        raise InvalidParamsException(f"{address} is not SCORE")
    elif isinstance(score_mapper.get(address, None), IconScoreBase) is False:
        raise InvalidParamsException(f"{address} is not active SCORE")
    return score_mapper[address]


def internal_get_balance(self: InternalCall, address: 'Address'):
    """Hooking method for InternalCall.get_icx_balance"""
    return IcxEngine.get_balance(None, address)


def internal_transfer(self: 'InternalCall', _from: 'Address', _to: 'Address', amount: int):
    """Hooking method for InternalCal.icx_transfer_call"""
    IcxEngine.transfer(ContextGetter._context, _from, _to, amount)


InternalCall.get_icx_balance = internal_get_balance
InternalCall.icx_transfer_call = internal_transfer
IconScoreContextUtil.get_owner = lambda context, score_address: context.msg.sender


def get_default_context():
    context = IconScoreContext()
    block = Block()
    context.block = block
    context.icon_score_mapper = score_mapper
    context.traces = []
    context.validate_score_blacklist = Mock(return_value=True)
    context.tx = Transaction()
    context.msg = Message()
    context.get_icon_score = get_icon_score
    context.block_batch = None
    context.tx_batch = None
    return context


class Context:
    context = get_default_context()

    @classmethod
    def initialize_variables(cls, sender: Optional['Address']=None, value: int=0, tx_timestamp: Optional[int]=None,
                             block_height: int=0, func_type: 'IconScoreFuncType'=IconScoreFuncType.READONLY,
                             context_type: 'IconScoreContextType'=IconScoreContextType.QUERY):
        cls._set_block(cls.context, block_height)
        cls._set_msg(cls.context, sender, value)
        cls._set_tx(cls.context, sender, tx_timestamp, None, 0, 0)
        cls._set_func_type(cls.context, func_type)
        cls._set_context_type(cls.context, context_type)

    @classmethod
    def get_context(cls):
        return cls.context

    @classmethod
    def reset_context(cls):
        cls.context = get_default_context()

    @staticmethod
    def _set_invoke_context(context):
        context.type = IconScoreContextType.INVOKE
        context.event_logs = []
        context.func_type = IconScoreFuncType.WRITABLE

    @staticmethod
    def _set_query_context(context):
        context.type = IconScoreContextType.QUERY
        context.func_type = IconScoreFuncType.READONLY

    @classmethod
    def set_msg(cls, sender: Optional['Address']=None, value: int=0):
        context = cls.context = ContextGetter._context
        cls._set_msg(context, sender, value)

    @classmethod
    def set_tx(cls, origin: Optional['Address']=None, timestamp: Optional[int]=None, _hash: Optional[bytes]=None,
               index: int=0, nonce: int=0):
        context = cls.context = ContextGetter._context
        cls._set_tx(context, origin, timestamp, _hash, index, nonce)

    @classmethod
    def set_block(cls, height: int=0, timestamp: Optional[int]=None):
        context = cls.context = ContextGetter._context
        cls._set_block(context, height, timestamp)

    @staticmethod
    def _set_msg(context, sender: Optional['Address'] = None, value: int = 0):
        msg = context.msg
        msg.sender = sender
        msg.value = value

    @staticmethod
    def _set_tx(context, origin: Optional['Address'] = None, timestamp: Optional[int] = None,
                _hash: Optional[bytes] = None, index: int = 0, nonce: int = 0):
        tx = context.tx
        tx._origin = origin
        tx._timestamp = timestamp
        tx._hash = _hash if _hash is not None else create_tx_hash()
        tx._index = index
        tx._nonce = nonce

    @staticmethod
    def _set_block(context, height: int = 0, timestamp: Optional[int] = None):
        block: Block = context.block
        block._height = height
        if timestamp:
            block.timestamp = timestamp

    @staticmethod
    def _set_func_type(context: 'IconScoreContext', func_type: 'IconScoreFuncType'=IconScoreFuncType.WRITABLE):
        context.func_type = func_type

    @staticmethod
    def _set_context_type(context: 'IconScoreContext',
                          context_type: 'IconScoreContextType'=IconScoreContextType.INVOKE):
        context.type = context_type
