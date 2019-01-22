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
from typing import TYPE_CHECKING

from iconservice.base.exception import InvalidRequestException

from .mock_db import MockPlyvelDB

if TYPE_CHECKING:
    from iconservice.base.address import Address
    from iconservice.iconscore.icon_score_context import IconScoreContext


class MockIcxEngine:
    db: MockPlyvelDB = None

    @classmethod
    def get_balance(cls, context: 'IconScoreContext', address: 'Address') -> int:
        balance = none_to_zero(cls.db.get(context, address.to_bytes()))
        return balance

    @classmethod
    def transfer(cls, context: 'IconScoreContext', _from: 'Address', _to: 'Address', amount: int):
        _sender_address = _from.to_bytes()
        _receiver_address = _to.to_bytes()

        sender_balance = none_to_zero(cls.db.get(context, _sender_address))
        receiver_balance = none_to_zero(cls.db.get(context, _receiver_address))

        if sender_balance < amount:
            raise InvalidRequestException('out of balance')

        sender_balance -= amount
        receiver_balance += amount

        cls.db._db[_sender_address] = sender_balance
        cls.db._db[_receiver_address] = receiver_balance


def none_to_zero(balance) -> int:
    if balance is None:
        return 0
    return balance
