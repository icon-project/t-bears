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

from iconservice.base.exception import InvalidRequestException
from iconservice.base.message import Message
from iconservice.base.transaction import Transaction
from iconservice.builtin_scores.governance.governance import STEP_TYPE_DEFAULT, STEP_TYPE_CONTRACT_CALL, \
    STEP_TYPE_CONTRACT_CREATE, STEP_TYPE_CONTRACT_UPDATE, STEP_TYPE_CONTRACT_DESTRUCT, STEP_TYPE_CONTRACT_SET, \
    STEP_TYPE_GET, STEP_TYPE_REPLACE, STEP_TYPE_SET, STEP_TYPE_DELETE, STEP_TYPE_INPUT, STEP_TYPE_EVENT_LOG, \
    STEP_TYPE_API_CALL
from iconservice.database.batch import TransactionBatch
from iconservice.icon_constant import IconScoreContextType, IconScoreFuncType
from iconservice.iconscore.icon_score_context import IconScoreContext
from iconservice.iconscore.icon_score_step import IconScoreStepCounterFactory, StepType

from ..mock_components.mock_block import MockBlock
from ...icon_integrate_test import create_tx_hash

if TYPE_CHECKING:
    from iconservice.base.address import Address

score_mapper = {}
tx_hash_set = set()

initial_costs = {
    STEP_TYPE_DEFAULT: 1_000_000,
    STEP_TYPE_CONTRACT_CALL: 15_000,
    STEP_TYPE_CONTRACT_CREATE: 200_000,
    STEP_TYPE_CONTRACT_UPDATE: 80_000,
    STEP_TYPE_CONTRACT_DESTRUCT: -70_000,
    STEP_TYPE_CONTRACT_SET: 30_000,
    STEP_TYPE_GET: 0,
    STEP_TYPE_SET: 200,
    STEP_TYPE_REPLACE: 50,
    STEP_TYPE_DELETE: -150,
    STEP_TYPE_INPUT: 200,
    STEP_TYPE_EVENT_LOG: 100,
    STEP_TYPE_API_CALL: 0
}


def add_tx(tx_hash: bytes):
    if tx_hash in tx_hash_set:
        raise InvalidRequestException("duplicated tx")

    tx_hash_set.add(tx_hash)


def get_icon_score(address: 'Address'):
    return score_mapper[address]


def get_patched_context(context: 'IconScoreContext'):
    block = MockBlock()
    context.block = block
    context.icon_score_mapper = score_mapper
    context.traces = []
    context.tx_batch = TransactionBatch()
    context.validate_score_blacklist = Mock(return_value=True)
    context.tx = Transaction()
    context.msg = Message()
    context.get_icon_score = Mock(side_effect=get_icon_score)
    return context


class ContextManager:
    context = get_patched_context(IconScoreContext())
    strict = False
    service_flag = 15
    step_counter_factory = IconScoreStepCounterFactory()
    context.step_counter = step_counter_factory.create(0)
    max_step_limits = {}

    @classmethod
    def set_block(cls, height: int=0):
        if height is not None:
            context = cls.context
            context.block._height = height

    @classmethod
    def set_message_sender(cls, sender: Optional['Address']):
        cls.context.msg.sender = sender

    @classmethod
    def set_message_value(cls, value: int=0):
        cls.context.msg.value = value

    @classmethod
    def set_message(cls, sender: Optional['Address'], value: int=0):
        cls.set_message_sender(sender)
        cls.set_message_value(value)

    @classmethod
    def set_invoke_context(cls):
        cls.context.type = IconScoreContextType.INVOKE
        cls.context.event_logs = []
        cls.context.func_type = IconScoreFuncType.WRITABLE

    @classmethod
    def set_query_context(cls):
        cls.context.type = IconScoreContextType.QUERY
        cls.context.func_type = IconScoreFuncType.READONLY

    @classmethod
    def set_context(cls, context_type: Optional[IconScoreContextType]):
        if cls.strict is False:
            cls.set_context_using_type(context_type)

    @classmethod
    def set_context_using_type(cls, context_type: Optional[IconScoreContextType]=None):
        if context_type == IconScoreContextType.QUERY:
            cls.set_query_context()
        else:
            cls.set_invoke_context()

    @classmethod
    def set_transaction(cls, timestamp: Optional[int]=None, index: Optional[int]=None, nonce: Optional[int]=None,
                        arguments: Optional[tuple]=None):
        tx = cls.context.tx
        tx._timestamp = cls.context.block.timestamp if timestamp is None else timestamp
        tx._origin = cls.context.msg.sender
        tx._index = tx._index if index is None else index
        if nonce is None:
            tx._nonce = tx._nonce if tx._nonce is not None else 0
        tx_data = cls.get_tx_data(arguments)
        tx._hash = create_tx_hash(tx_data)

    @classmethod
    def get_tx_data(cls, arguments: Optional[tuple]=None):
        tx = cls.context.tx
        tx_data = f"{tx.origin}{tx.nonce}{cls.context.current_address}{cls.context.msg.value}" \
                  f"{tx.timestamp}{arguments}".encode()
        return tx_data

    @classmethod
    def increase_tx_index(cls):
        cls.context.tx._index += 1

    @classmethod
    def increase_tx_nonce(cls):
        cls.context.tx._nonce += 1

    @classmethod
    def validate_timestamp(cls, timestamp: Optional[int]=None):
        if timestamp is not None and timestamp > cls.context.block.timestamp:
            raise InvalidRequestException(f"invalid timestamp: {timestamp},"
                                          f"blocktimestamp: {cls.context.block.timestamp}")

    @classmethod
    def set_step_counter(cls, step_price_dict: dict=initial_costs,
                         step_limit: int=2_013_265_920, step_price: int=10_000_000_000):
        for k, v in step_price_dict.items():
            try:
                cls.step_counter_factory.set_step_cost(
                    StepType(k), v)
            except ValueError:
                pass

        cls.step_counter_factory.set_step_price(step_price)
        cls.context.step_counter = cls.step_counter_factory.create(step_limit)
