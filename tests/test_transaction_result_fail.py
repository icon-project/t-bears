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
import asyncio
import os
import shutil
import unittest

from tbears.libs.icon_json import get_icx_getTransactionResult_payload, get_dummy_icx_sendTransaction_payload
from tbears.util import make_install_json_payload
from tbears.libs.jsonrpc_error_code import INVALID_PARAMS, SERVER_ERROR, SCORE_ERROR, INVALID_REQUEST
from tests.test_util import TEST_UTIL_DIRECTORY
from tests.test_util.tbears_mock_server import API_PATH, init_mock_server
from tests.test_util.json_contents_for_tests import god_address, treasury_address, get_data_for_transfer_token, \
    token_owner_address, token_score_address, test_address


class TestTransactionResult(unittest.TestCase):

    def tearDown(self):

        try:
            if os.path.exists('./.score'):
                shutil.rmtree('./.score')
            if os.path.exists('./.db'):
                shutil.rmtree('./.db')
            os.remove('./tbears.log')
        except:
            pass

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.path = API_PATH
        self.app = init_mock_server()

    def test_transaction_result(self):
        run_payload = make_install_json_payload(f'{TEST_UTIL_DIRECTORY}/sample_token')
        _, response = self.app.test_client.post(self.path, json=run_payload)

        payload = get_dummy_icx_sendTransaction_payload(god_address, test_address, hex(10 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertTrue(response_json['result'].startswith('0x'))

        # send icx with invalid param
        payload = get_dummy_icx_sendTransaction_payload(god_address, '123', hex(10 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        payload = get_dummy_icx_sendTransaction_payload('1', god_address, hex(10 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # send transaction to score with invalid param in score's method.
        data = get_data_for_transfer_token(treasury_address, god_address)
        payload = get_dummy_icx_sendTransaction_payload(token_owner_address, token_score_address, hex(0),
                                                        data_type='call', data=data)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        # tx_result payload
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(int(response_json['result']['failure']['code'], 0), -SERVER_ERROR)

        # not enough value
        data= get_data_for_transfer_token(treasury_address, hex(1000000 * 10 ** 18))
        payload = get_dummy_icx_sendTransaction_payload(token_owner_address, token_score_address, hex(0),
                                                        data_type='call', data=data)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json

        # get tx_result payload
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(int(response_json['result']['failure']['code'], 0), -SCORE_ERROR)

        # not enough icx
        payload = get_dummy_icx_sendTransaction_payload(treasury_address, god_address, hex(1000000 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_REQUEST)
