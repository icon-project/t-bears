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

from iconservice import Address

from tbears.command import run_SCORE, clear_SCORE, make_SCORE_samples, init_SCORE
from tests.sample_test_client import send_req
from tests.common import *

token_owner_address = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
token_score_address = "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf"
crowd_sale_score_address = "cx8c814aa96fefbbb85131f87f6e0cb7878a95c1d3"
test_addr = "hxbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
treasury_address = "hx1000000000000000000000000000000000000000"


class TestTBears(unittest.TestCase):

    def tearDown(self):
        clear_SCORE()

        try:
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
            if os.path.exists('sample_crowd_sale'):
                shutil.rmtree('sample_crowd_sale')
            if os.path.exists('.test_tbears_db'):
                shutil.rmtree('.test_tbears_db')
            os.remove('./tbears.log')
        except:
            pass

    def test_token(self):
        init_SCORE('sample_token', 'SampleToken')
        result, response = run_SCORE('sample_token', None, None, TBEARS_JSON_PATH)
        response = response.json()

        # send transaction
        payload = get_request_json_of_send_icx(fr=Address.from_string(god_address),
                                               to=Address.from_string(treasury_address), value=10 * 10 ** 18)
        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']

        payload = get_request_of_icx_getTransactionResult(tx_hash)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']['status']
        self.assertEqual(result, hex(1))

        # icx_sendTransaction error check
        payload = get_request_json_of_send_icx(fr='', to=treasury_address, value=10 * 10 ** 18)
        response = send_req(SEND, payload)
        response_json = response.json()
        error: dict = response_json['error']
        self.assertTrue(isinstance(error, dict))
        code: int = error['code']
        self.assertTrue(isinstance(code, int) and code < 0)
        message: str = error['message']
        self.assertTrue(isinstance(message, str))

        # get balance
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(treasury_address))
        response = send_req(BAL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # check token supply
        payload = get_request_json_of_token_total_supply(token_addr=Address.from_string(token_score_address))
        response = send_req(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # check token balance
        payload = get_request_json_of_get_token_balance(addr_from=Address.from_string(token_owner_address),
                                                        to=Address.from_string(token_score_address))
        response = send_req(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # send token to test_addr
        payload = get_request_json_of_transfer_token(fr=Address.from_string(token_owner_address),
                                                     addr_to=Address.from_string(treasury_address),
                                                     value=10 * 10 ** 18, to=Address.from_string(token_score_address))
        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']

        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result['status'], hex(1))

        # check token balance
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(treasury_address))
        response = send_req(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # icx_getTransactionResult error check
        req = get_request_of_icx_getTransactionResult(tx_hash='0x00')
        response = send_req(TX_RESULT, req)
        response_json = response.json()
        self.assertEqual(1, response_json['id'])
        self.assertTrue('error' in response_json)
        self.assertTrue(isinstance(response_json['error']['code'], int))
        self.assertTrue(isinstance(response_json['error']['message'], str))

    def test_score_methods(self):
        make_SCORE_samples()
        result, _ = run_SCORE('sample_token', None, None, TBEARS_JSON_PATH)
        result, _ = run_SCORE('sample_crowd_sale', None, None, TBEARS_JSON_PATH)
        # seq1
        # genesis -> token_owner 10icx
        payload = get_request_json_of_send_icx(fr=Address.from_string(god_address),
                                               to=Address.from_string(token_owner_address),
                                               value=10*10**18)

        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result['status'], hex(1))
        print(result)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(token_owner_address))
        res = send_req(BAL, payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(token_owner_address))
        response = send_req(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        payload = get_request_json_of_transfer_token(fr=Address.from_string(token_owner_address),
                                                     to=Address.from_string(token_score_address),
                                                     addr_to=Address.from_string(crowd_sale_score_address),
                                                     value=1000*10**18)
        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        res = send_req(TX_RESULT, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(crowd_sale_score_address))
        response = send_req(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        response = send_req(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_request_json_of_send_icx(fr=token_owner_address, to=crowd_sale_score_address,
                                               value=hex(2*10**18))
        response = send_req(SEND, payload)
        response_json = response.json()
        result = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(token_owner_address))

        response = send_req(BAL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(token_owner_address))
        response = send_req(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(token_owner_address),
                                               to=Address.from_string(crowd_sale_score_address),
                                               value=8*10**18)
        response = send_req(SEND, payload)
        response_json = response.json()
        result = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(god_address),
                                               to=Address.from_string(test_addr),
                                               value=90*10**18)
        response = send_req(SEND, payload)
        response_json = response.json()
        result = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(test_addr),
                                               to=Address.from_string(crowd_sale_score_address),
                                               value=90*10**18)
        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_request_json_of_check_crowd_end(fr=Address.from_string(token_owner_address),
                                                      to=Address.from_string(crowd_sale_score_address))
        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq14
        # safe withrawal
        payload = get_request_json_of_crowd_withrawal(fr=token_owner_address, to=crowd_sale_score_address)
        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = send_req(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        response = send_req(BAL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
