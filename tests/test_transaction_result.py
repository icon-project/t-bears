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
import os
import shutil
import unittest

from tbears.command import init_SCORE, run_SCORE, clear_SCORE
from tbears.util import post

from .json_contents import *
from .jsonrpc_error_code import *


url = "http://localhost:9000/api/v3"


class TestTransactionResult(unittest.TestCase):

    def tearDown(self):
        clear_SCORE()

        try:
            os.remove('logger.log')
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
        except:
            pass

    def test_missing_param_send_icx(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_send_icx(god_address, '123', hex(10 * 10 ** 18))

        del payload['params']['from']
        response = post(url, payload).json()
        self.assertEqual(response['error']['code'], INVALID_PARAMS)

    def test_invalid_param_send_icx(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_send_icx(god_address, '123', hex(10 * 10 ** 18))
        response = post(url, payload).json()
        self.assertEqual(response['error']['code'], INVALID_PARAMS)

        payload = get_request_json_of_send_icx('1', god_address, hex(10 * 10 ** 18))
        response = post(url, payload).json()
        self.assertEqual(response['error']['code'], INVALID_PARAMS)

    def test_invalid_score_address_invoke(self):
        init_SCORE('sample_token', "SampleToken")
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_transfer_token(fr=god_address, to='', addr_to=test_address, value=hex(1*10**18))
        response = post(url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=response)
        tx_result = post(url, payload).json()
        self.assertEqual(int(tx_result['result']['failure']['code'], 0), -SERVER_ERROR)

    def test_invalid_param_score_invoke(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)

        payload = get_request_json_of_transfer_token(fr=token_owner_address, to='123',
                                                     addr_to=test_address, value=god_address)
        res = post(url, payload)

        # tx_result payload
        payload = get_request_of_icx_getTransactionResult(tx_hash=res.json()['result'])
        tx_result = post(url, payload).json()
        self.assertEqual(int(tx_result['result']['failure']['code'], 0), -SERVER_ERROR)

    def test_invalid_param_in_score_invoke(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)

        payload = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                     addr_to=test_address, value=god_address)
        res = post(url, payload)

        # tx_result payload
        payload = get_request_of_icx_getTransactionResult(tx_hash=res.json()['result'])
        tx_result = post(url, payload).json()
        self.assertEqual(int(tx_result['result']['failure']['code'], 0), -SERVER_ERROR)

    def test_not_enough_value_score_invoke(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)

        payload = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                     addr_to=test_address, value=hex(100000*10**18))
        tx_hash = post(url, payload).json()['result']

        # get tx_result payload
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        tx_result = post(url, payload)
        self.assertEqual(int(tx_result.json()['result']['failure']['code'], 0), -SCORE_ERROR)

    def test_not_enough_balance_send_icx(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_send_icx(test_address, god_address, hex(10 * 10 ** 18))

        response = post(url, payload).json()

        # tx_result payload
        payload = get_request_of_icx_getTransactionResult(tx_hash=response['result'])
        tx_result = post(url, payload).json()
        self.assertEqual(int(tx_result['result']['failure']['code'], 0), -INVALID_PARAMS)
        # failure : INVALID PARAMS
