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

from tbears.command import make_SCORE_samples, init_SCORE
from tbears.util import make_install_json_payload
from tbears.util.tbears_mock_server import API_PATH, init_mock_server, fill_json_content
from tests.common import *

token_owner_address = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
token_score_address = "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf"
crowd_sale_score_address = "cx8c814aa96fefbbb85131f87f6e0cb7878a95c1d3"
test_addr = "hxbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
treasury_address = "hx1000000000000000000000000000000000000000"


class TestTBears(unittest.TestCase):

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
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.path = API_PATH
        self.app = init_mock_server()

    def test_token(self):
        init_SCORE('sample_token', 'SampleToken')
        run_payload = make_install_json_payload('sample_token')
        _, response = self.app.test_client.post(self.path, json=run_payload)

        # send transaction
        params = get_request_json_of_send_icx(fr=god_address,
                                              to=treasury_address, value=hex(10 * 10 ** 18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']

        params = get_request_of_icx_getTransactionResult(tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']['status']
        self.assertEqual(result, hex(1))

        # icx_sendTransaction error check
        params = get_request_json_of_send_icx(fr='', to=treasury_address, value=hex(10 * 10 ** 18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        error: dict = response_json['error']
        self.assertTrue(isinstance(error, dict))
        code: int = error['code']
        self.assertTrue(isinstance(code, int) and code < 0)
        message: str = error['message']
        self.assertTrue(isinstance(message, str))

        # get balance
        params = get_request_json_of_get_icx_balance(address=treasury_address)
        payload = fill_json_content(BAL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # check token supply
        params = get_request_json_of_token_total_supply(token_addr=token_score_address)
        payload = fill_json_content(CALL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # check token balance
        params = get_request_json_of_get_token_balance(addr_from=token_owner_address, to=token_score_address)
        payload = fill_json_content(CALL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # send token to test_addr
        params = get_request_json_of_transfer_token(fr=token_owner_address, addr_to=treasury_address,
                                                    value=hex(10 * 10 ** 18), to=token_score_address)
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']

        params = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result['status'], hex(1))

        # check token balance
        params = get_request_json_of_get_token_balance(to=token_score_address,
                                                       addr_from=treasury_address)
        payload = fill_json_content(CALL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # icx_getTransactionResult error check
        params = get_request_of_icx_getTransactionResult(tx_hash='0x00')
        payload = fill_json_content(TX_RESULT, params)
        payload['id'] = 1
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(1, response_json['id'])
        self.assertTrue('error' in response_json)
        self.assertTrue(isinstance(response_json['error']['code'], int))
        self.assertTrue(isinstance(response_json['error']['message'], str))

    def test_score_methods(self):
        make_SCORE_samples()
        run_payload = make_install_json_payload('sample_token')
        _, response = self.app.test_client.post(self.path, json=run_payload)
        run_payload = make_install_json_payload('sample_crowd_sale')
        _, response = self.app.test_client.post(self.path, json=run_payload)
        # seq1
        # genesis -> token_owner 10icx
        params = get_request_json_of_send_icx(fr=god_address,
                                              to=token_owner_address,
                                              value=hex(10*10**18))
        payload = fill_json_content(SEND, params)

        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result['status'], hex(1))
        print(result)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        params = get_request_json_of_get_icx_balance(address=token_owner_address)
        payload = fill_json_content(BAL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        res = response.json['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        params = get_request_json_of_get_token_balance(to=token_score_address,
                                                       addr_from=token_owner_address)
        payload = fill_json_content(CALL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        params = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                    addr_to=crowd_sale_score_address,  value=hex(1000*10**18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        res = response.json['result']['status']
        self.assertEqual(res, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        params = get_request_json_of_get_token_balance(to=token_score_address,
                                                       addr_from=crowd_sale_score_address)
        payload = fill_json_content(CALL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        params = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        payload = fill_json_content(CALL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        params = get_request_json_of_send_icx(fr=token_owner_address, to=crowd_sale_score_address, value=hex(2*10**18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=result)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        params = get_request_json_of_get_icx_balance(address=token_owner_address)
        payload = fill_json_content(BAL, params)

        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        params = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        payload = fill_json_content(CALL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        params = get_request_json_of_send_icx(fr=token_owner_address, to=crowd_sale_score_address, value=hex(8*10**18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=result)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        params = get_request_json_of_send_icx(fr=god_address, to=test_addr, value=hex(90*10**18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=result)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        params = get_request_json_of_send_icx(fr=test_addr, to=crowd_sale_score_address, value=hex(90*10**18))
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq13
        # check CrowdSaleEnd
        params = get_request_json_of_check_crowd_end(fr=token_owner_address, to=crowd_sale_score_address)
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq14
        # safe withrawal
        params = get_request_json_of_crowd_withrawal(fr=token_owner_address, to=crowd_sale_score_address)
        payload = fill_json_content(SEND, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        params = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        payload = fill_json_content(TX_RESULT, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        params = get_request_json_of_get_icx_balance(address=token_owner_address)
        payload = fill_json_content(BAL, params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
