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

from tests.json_contents import *
from tests.jsonrpc_error_code import *


url = "http://localhost:9000/api/v3"

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))
TBEARS_JSON_PATH = os.path.join(DIRECTORY_PATH, 'test_tbears.json')


class TestTransactionResult(unittest.TestCase):

    def tearDown(self):
        clear_SCORE()

        try:
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
            if os.path.exists('.test_tbears_db'):
                shutil.rmtree('.test_tbears_db')
            os.remove('./tbears.log')
        except:
            pass

    def test_missing_param_send_icx(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None, TBEARS_JSON_PATH)
        # send icx (missing params)
        payload = get_request_json_of_send_icx(god_address, '123', hex(10 * 10 ** 18))

        del payload['params']['from']
        response = post(url, payload).json()
        self.assertEqual(response['error']['code'], INVALID_PARAMS)

        # send icx with invalid param
        payload = get_request_json_of_send_icx(god_address, '123', hex(10 * 10 ** 18))
        response = post(url, payload).json()
        self.assertEqual(response['error']['code'], INVALID_PARAMS)

        payload = get_request_json_of_send_icx('1', god_address, hex(10 * 10 ** 18))
        response = post(url, payload).json()
        self.assertEqual(response['error']['code'], INVALID_PARAMS)

        # send transaction to invalid score address
        payload = get_request_json_of_transfer_token(fr=god_address, to='', addr_to=test_address, value=hex(1*10**18))
        res = post(url, payload).json()
        self.assertEqual(res['error']['code'], SERVER_ERROR)

        # send transaction to score with invalid param

        payload = get_request_json_of_transfer_token(fr=token_owner_address, to='123',
                                                     addr_to=test_address, value=god_address)
        res = post(url, payload).json()
        self.assertEqual(res['error']['code'], INVALID_PARAMS)

        # send transaction to score with invalid param in score's method.
        payload = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                     addr_to=test_address, value=god_address)
        res = post(url, payload)

        # tx_result payload
        payload = get_request_of_icx_getTransactionResult(tx_hash=res.json()['result'])
        tx_result = post(url, payload).json()
        self.assertEqual(int(tx_result['result']['failure']['code'], 0), -SERVER_ERROR)

        # not enough value
        payload = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                     addr_to=test_address, value=hex(100000*10**18))
        tx_hash = post(url, payload).json()['result']

        # get tx_result payload
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        tx_result = post(url, payload)
        self.assertEqual(int(tx_result.json()['result']['failure']['code'], 0), -SCORE_ERROR)

        # not enough icx
        payload = get_request_json_of_send_icx(test_address, god_address, hex(10 * 10 ** 18))

        res = post(url, payload).json()
        self.assertEqual(res['error']['code'], INVALID_REQUEST)
        # failure : INVALID PARAMS
