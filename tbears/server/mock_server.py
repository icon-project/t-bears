# -*- coding: utf-8 -*-
# Copyright 2017-2018 theloop Inc.
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

import time

from iconservice import Address, StepType, TypeConverter, IconServiceBaseException, Logger, ICON_SERVICE_LOG_TAG, \
    ExceptionCode, IconScoreContextType
from iconservice.base.block import Block
from iconservice.iconscore.icon_score_context import IconScoreContext
from iconservice.database.batch import BlockBatch, TransactionBatch
from iconservice.icon_service_engine import IconServiceEngine
from hashlib import sha3_256

from iconservice.iconscore.icon_score_context import IconScoreContextFactory
from iconservice.iconscore.icon_score_step import IconScoreStepCounterFactory
from iconservice.utils import make_response, make_error_response


context_factory = IconScoreContextFactory(max_size=1)
__block_height = -1


def _create_context(context_type: IconScoreContextType) -> IconScoreContext:
    context = context_factory.create(context_type)

    if context.type == IconScoreContextType.INVOKE:
        context.block_batch = BlockBatch()
        context.tx_batch = TransactionBatch()

    return context


def get_block_height():
    global __block_height
    __block_height += 1
    return __block_height


class MockServer:

    def __init__(self):
        self._state_db_root_path = '.db'
        self._icon_score_root_path = '.score'

        engine = IconServiceEngine()
        engine.open(icon_score_root_path=self._icon_score_root_path,
                    state_db_root_path=self._state_db_root_path)
        self._engine = engine

        self.genesis_address = Address.from_string(f'hx{"0"*40}')
        self.owner_address = Address.from_string(f'hx{"a"*40}')
        self.treasury_address = Address.from_string(f'hx1{"0"*39}')

        self._tx_hash = sha3_256(b'tx_hash').digest()
        self._from = self.genesis_address
        self._total_supply = 100 * 10 ** 18

        self._step_counter_factory = IconScoreStepCounterFactory()
        self._step_counter_factory.set_step_unit(StepType.TRANSACTION, 10)
        self._step_counter_factory.set_step_unit(StepType.STORAGE_SET, 10)
        self._step_counter_factory.set_step_unit(StepType.STORAGE_REPLACE, 10)
        self._step_counter_factory.set_step_unit(StepType.STORAGE_DELETE, 10)
        self._step_counter_factory.set_step_unit(StepType.TRANSFER, 10)
        self._step_counter_factory.set_step_unit(StepType.CALL, 10)
        self._step_counter_factory.set_step_unit(StepType.EVENTLOG, 10)

        self._engine._step_counter_factory = self._step_counter_factory
        self._engine._precommit_state = None
        self._init_type_converter()

        accounts = [
            {
                'name': 'god',
                'address': self.genesis_address,
                'balance': self._total_supply
            },
            {
                'name': 'treasury',
                'address': self.treasury_address,
                'balance': 0
            }
        ]

        block = Block(0, 'bloackHash', 0)
        tx = {'method': '',
              'params': {'txHash': 'txHash'},
              'accounts': accounts}
        tx_lists = [tx]

        self._engine.invoke(block, tx_lists)
        self._engine.commit()

    def icx_getBalance(self, request_params):
        self._convert_request_params(request_params)
        return self._query(request_params)

    def icx_sendTransaction(self, request_params: dict):
        pre_validate_result = self._tx_pre_validate(request_params)
        if pre_validate_result == '0x0':
            block_height = get_block_height()
            block_hash = None
            block_timestamp = int(time.time() * 10 ** 6),
            block = Block(block_height, block_hash, block_timestamp)
            tx = {
                "method": "icx_sendTransaction",
                "params": request_params['params']
            }
            tx_result = self._engine.invoke(block, [tx])
            self._engine.commit()
            return tx_result
        else:
            return pre_validate_result

    def icx_call(self, request_params: dict):
        self._convert_request_params(request_params)
        return self._query(request_params)

    def _tx_pre_validate(self, request: dict):
        try:
            converted_request = self._convert_request_params(request)
            self._engine.tx_pre_validate(converted_request)
        except IconServiceBaseException as icon_e:
            Logger.error(icon_e, ICON_SERVICE_LOG_TAG)
            return make_error_response(icon_e.code, icon_e.message)
        except Exception as e:
            Logger.error(e, ICON_SERVICE_LOG_TAG)
            return make_error_response(ExceptionCode.SERVER_ERROR, str(e))
        return make_response(ExceptionCode.OK)

    def _query(self, request: dict):
        try:
            converted_request = self._convert_request_params(request)
            self._engine.query_pre_validate(converted_request)

            value = self._engine.query(method=converted_request['method'],
                                                    params=converted_request['params'])

            if isinstance(value, Address):
                value = str(value)
            response = make_response(value)
        except IconServiceBaseException as icon_e:
            Logger.error(icon_e, ICON_SERVICE_LOG_TAG)
            return make_error_response(icon_e.code, icon_e.message)
        except Exception as e:
            Logger.error(e, ICON_SERVICE_LOG_TAG)
            return make_error_response(ExceptionCode.SERVER_ERROR, str(e))
        return response

    def _convert_request_params(self, request: dict) -> dict:
        params = request['params']
        params = self._type_converter.convert(params, recursive=True)
        request['params'] = params
        return request

    def _init_type_converter(self):
        type_table = {
            'from': 'address',
            'to': 'address',
            'address': 'address',
            'fee': 'int',
            'value': 'int',
            'balance': 'int',
            'timestamp': 'int'
        }
        self._type_converter = TypeConverter(type_table)
