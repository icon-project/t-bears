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
import shutil
import unittest


from tbears.command import init_SCORE
from tbears.util import make_install_json_payload
from tbears.util.tbears_mock_server import API_PATH, init_mock_server, fill_json_content

from tests.common import *
from tests.jsonrpc_error_code import *


class TestTransactionResult(unittest.TestCase):

    def tearDown(self):

        try:
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
            if os.path.exists('./.test_tbears_db'):
                shutil.rmtree('./.test_tbears_db')
            if os.path.exists('./.score'):
                shutil.rmtree('./.score')
            if os.path.exists('./.db'):
                shutil.rmtree('./.db')
            os.remove('./tbears.log')
        except:
            pass

    def setUp(self):
<<<<<<< HEAD
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.path = API_PATH
        self.app = init_mock_server()
=======
        self.private_key = PrivateKey().private_key
        self.icon_client = IconClient(TBEARS_LOCAL_URL)
>>>>>>> Fix unit test(#39)

    def test_transaction_result(self):
        init_SCORE('sample_token', 'SampleToken')
        run_payload = make_install_json_payload('sample_token')
        _, response = self.app.test_client.post(self.path, json=run_payload)

        params = get_request_json_of_send_icx(god_address, test_address, hex(10 * 10 ** 18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertTrue(response_json['result'].startswith('0x'))

        # send icx with invalid param
        params = get_request_json_of_send_icx(god_address, '123', hex(10 * 10 ** 18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        params = get_request_json_of_send_icx('1', god_address, hex(10 * 10 ** 18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # send transaction to invalid score address
        params = get_request_json_of_transfer_token(fr=god_address, to='', addr_to=test_address, value=hex(1*10**18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], SERVER_ERROR)

        # send transaction to score with invalid param

        params = get_request_json_of_transfer_token(fr=token_owner_address, to='123',
                                                    addr_to=test_address, value=god_address)
        payload = fill_json_content(SEND, params)

        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # send transaction to score with invalid param in score's method.
        params = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                    addr_to=test_address, value=god_address)
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        # tx_result payload
        tx_hash = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(int(response_json['result']['failure']['code'], 0), -SERVER_ERROR)

        # not enough value
        params = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                    addr_to=test_address, value=hex(100000*10**18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json

        # get tx_result payload
        tx_hash = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(int(response_json['result']['failure']['code'], 0), -SCORE_ERROR)

        # not enough icx
        params = get_request_json_of_send_icx(test_address, god_address, hex(1000000 * 10 ** 18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_REQUEST)
