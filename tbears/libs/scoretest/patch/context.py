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
from iconservice.iconscore.icon_score_context import IconScoreContext

from ..mock.block import Block
from ..mock.db import MockKeyValueDatabase
from ..mock.icx_engine import IcxEngine
from ....libs.icon_integrate_test import create_tx_hash

if TYPE_CHECKING:
    from iconservice.base.address import Address

score_mapper = {}
interface_score_mapper = {}
MAIN_NET_REVISION = 8
context_db = MockKeyValueDatabase.create_db()  # Patch SCORE to use dictionary DB instance of LEVEL DB
IcxEngine.db = context_db
icon_network_value = {}


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


def get_default_context():
    mock_context = Mock(spec=IconScoreContext)
    mock_context.configure_mock(msg=Message())
    mock_context.configure_mock(tx=Transaction())
    mock_context.configure_mock(block=Block())
    mock_context.configure_mock(step_counter=None)
    mock_context.configure_mock(type=IconScoreContextType.QUERY)
    mock_context.configure_mock(func_type=IconScoreFuncType.WRITABLE)
    mock_context.configure_mock(current_address=None)
    mock_context.configure_mock(block_batch=None)
    mock_context.configure_mock(tx_batch=None)
    mock_context.configure_mock(event_logs=None)
    mock_context.configure_mock(event_log_stack=[])
    mock_context.configure_mock(traces=[])
    mock_context.configure_mock(icon_score_mapper=score_mapper)
    mock_context.configure_mock(revision=MAIN_NET_REVISION)
    mock_context.icon_score_mapper = score_mapper
    mock_context.validate_score_blacklist = Mock(return_value=True)
    mock_context.get_icon_score = get_icon_score
    return mock_context


def clear_data():
    IcxEngine.db.close()
    score_mapper.clear()
    interface_score_mapper.clear()


class Context:
    context = get_default_context()

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
    def set_msg(cls, sender: Optional['Address'] = None, value: int = 0):
        context = cls.context
        cls._set_msg(context, sender, value)

    @classmethod
    def set_tx(cls, origin: Optional['Address'] = None, timestamp: Optional[int] = None, _hash: Optional[bytes] = None,
               index: int = 0, nonce: int = 0):
        context = cls.context
        cls._set_tx(context, origin, timestamp, _hash, index, nonce)

    @classmethod
    def set_block(cls, height: int = 0, timestamp: Optional[int] = None):
        context = cls.context
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
