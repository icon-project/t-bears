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

from tbears.command.command_server import CommandServer
from tbears.libs.icon_json import get_icx_getBalance_payload, get_icx_getTransactionResult_payload, \
    get_icx_call_payload, get_dummy_icx_sendTransaction_payload
from tbears.util import make_install_json_payload
from tests.test_util import TEST_UTIL_DIRECTORY
from tests.test_util.tbears_mock_server import API_PATH, init_mock_server
from tests.test_util.json_contents_for_tests import god_address, token_owner_address, token_score_address, \
    get_params_for_get_token_balance, get_data_for_transfer_token, crowd_sale_score_address, treasury_address, \
    test_address


class TestTBears(unittest.TestCase):

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

    def test_token(self):
        run_payload = make_install_json_payload(f'{TEST_UTIL_DIRECTORY}/sample_token')
        _, response = self.app.test_client.post(self.path, json=run_payload)

        # send transaction
        payload = get_dummy_icx_sendTransaction_payload(fr=god_address, to=treasury_address, value=hex(10 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']

        payload = get_icx_getTransactionResult_payload(tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']['status']
        self.assertEqual(result, hex(1))

        # icx_sendTransaction error check
        payload = get_dummy_icx_sendTransaction_payload(fr='', to=treasury_address, value=hex(10 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        error: dict = response_json['error']
        self.assertTrue(isinstance(error, dict))
        code: int = error['code']
        self.assertTrue(isinstance(code, int) and code < 0)
        message: str = error['message']
        self.assertTrue(isinstance(message, str))

        # get balance
        payload = get_icx_getBalance_payload(address=treasury_address)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # check token supply
        payload = get_icx_call_payload(god_address, token_score_address, 'total_supply', {})
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # check token balance
        method_n_params = get_params_for_get_token_balance(token_owner_address)
        payload = get_icx_call_payload(god_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # send token to test_addr
        data = get_data_for_transfer_token(test_address, hex(10 * 10 ** 18))
        payload = get_dummy_icx_sendTransaction_payload(token_owner_address, token_score_address, hex(0),
                                                        data_type='call', data=data)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']

        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result['status'], hex(1))

        # check token balance
        method_n_params = get_params_for_get_token_balance(test_address)
        payload = get_icx_call_payload(god_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # icx_getTransactionResult error check
        payload = get_icx_getTransactionResult_payload(tx_hash='0x00')
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(1, response_json['id'])
        self.assertTrue('error' in response_json)
        self.assertTrue(isinstance(response_json['error']['code'], int))
        self.assertTrue(isinstance(response_json['error']['message'], str))

    def test_score_methods(self):
        run_payload = make_install_json_payload(f'{TEST_UTIL_DIRECTORY}/sample_token')
        _, response = self.app.test_client.post(self.path, json=run_payload)
        run_payload = make_install_json_payload(f'{TEST_UTIL_DIRECTORY}/sample_crowd_sale')
        _, response = self.app.test_client.post(self.path, json=run_payload)
        # seq1
        # genesis -> token_owner 10icx
        payload = get_dummy_icx_sendTransaction_payload(fr=god_address, to=token_owner_address, value=hex(10*10**18))

        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result['status'], hex(1))
        print(result)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_icx_getBalance_payload(address=token_owner_address)
        _, response = self.app.test_client.post(self.path, json=payload)
        res = response.json['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        method_n_params = get_params_for_get_token_balance(token_owner_address)
        payload = get_icx_call_payload(god_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        data = get_data_for_transfer_token(crowd_sale_score_address, hex(1000 * 10 ** 18))
        payload = get_dummy_icx_sendTransaction_payload(token_owner_address, token_score_address, hex(0),
                                                        data_type='call', data=data)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        res = response.json['result']['status']
        self.assertEqual(res, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        method_n_params = get_params_for_get_token_balance(crowd_sale_score_address)
        payload = get_icx_call_payload(god_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        method_n_params = get_params_for_get_token_balance(token_owner_address)
        payload = get_icx_call_payload(god_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_dummy_icx_sendTransaction_payload(fr=token_owner_address, to=crowd_sale_score_address,
                                                        value=hex(2*10**18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=result)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_icx_getBalance_payload(address=token_owner_address)

        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        method_n_params = get_params_for_get_token_balance(token_owner_address)
        payload = get_icx_call_payload(god_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_dummy_icx_sendTransaction_payload(fr=token_owner_address, to=crowd_sale_score_address,
                                                        value=hex(8*10**18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=result)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        payload = get_dummy_icx_sendTransaction_payload(fr=god_address, to=test_address, value=hex(90 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=result)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_dummy_icx_sendTransaction_payload(fr=test_address, to=crowd_sale_score_address,
                                                        value=hex(90 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_dummy_icx_sendTransaction_payload(token_owner_address, crowd_sale_score_address, hex(0),
                                                        data_type='call', data={'method': 'check_goal_reached',
                                                                                "params": {}})
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq14
        # safe withrawal
        payload = get_dummy_icx_sendTransaction_payload(token_owner_address, crowd_sale_score_address, hex(0),
                                                        data_type='call', data={'method': 'safe_withdrawal',
                                                                                'params': {}})
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_icx_getBalance_payload(address=token_owner_address)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
