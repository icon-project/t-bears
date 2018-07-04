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
import shutil
import unittest

from secp256k1 import PrivateKey

from tbears.command import init_SCORE, run_SCORE, clear_SCORE
from tbears.util.icon_client import IconClient

from tests.common import *
from tests.jsonrpc_error_code import *


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

    def setUp(self):
        self.private_key = PrivateKey().private_key
        self.icon_client = IconClient(URL, 3, self.private_key)

    def test_transaction_result(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)

        # send icx with invalid param
        payload = get_request_json_of_send_icx(god_address, '123', hex(10 * 10 ** 18))
        response = self.icon_client.send(SEND, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        payload = get_request_json_of_send_icx('1', god_address, hex(10 * 10 ** 18))
        response = self.icon_client.send(SEND, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # send transaction to invalid score address
        payload = get_request_json_of_transfer_token(fr=god_address, to='', addr_to=test_address, value=hex(1*10**18))
        response = self.icon_client.send(SEND, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], SERVER_ERROR)

        # send transaction to score with invalid param

        payload = get_request_json_of_transfer_token(fr=token_owner_address, to='123',
                                                     addr_to=test_address, value=god_address)
        response = self.icon_client.send(SEND, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # send transaction to score with invalid param in score's method.
        payload = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                     addr_to=test_address, value=god_address)
        response = self.icon_client.send(SEND, payload)
        response_json = response.json()
        # tx_result payload
        payload = get_request_of_icx_getTransactionResult(tx_hash=response_json['result'])
        response = self.icon_client.send(TX_RESULT, payload)
        response_json = response.json()
        self.assertEqual(int(response_json['result']['failure']['code'], 0), -SERVER_ERROR)

        # not enough value
        payload = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                     addr_to=test_address, value=hex(100000*10**18))
        response = self.icon_client.send(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']

        # get tx_result payload
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = self.icon_client.send(TX_RESULT, payload)
        response_json = response.json()
        self.assertEqual(int(response_json['result']['failure']['code'], 0), -SCORE_ERROR)

        # not enough icx
        payload = get_request_json_of_send_icx(test_address, god_address, hex(10 * 10 ** 18))
        response = self.icon_client.send(SEND, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], INVALID_REQUEST)

    def test_tx_result_prefix(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)

        payload = get_request_json_of_send_icx(fr=god_address, to=test_address, value=hex(10*10**18))
        response = self.icon_client.send(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        self.assertTrue(tx_hash.startswith('0x'))

        payload = get_request_of_icx_getTransactionResult(tx_hash)
        response = self.icon_client.send(TX_RESULT, payload)
        response_json = response.json()
        self.assertTrue(response_json['result']['txHash'].startswith('0x'))
