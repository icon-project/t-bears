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
import os

from tbears.util import post

from tbears.command import run_SCORE, clear_SCORE, make_SCORE_samples, stop_SCORE, init_SCORE

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))


def get_request_json_of_call_hello():
    return {
        "jsonrpc": "2.0",
        "method": "hello",
        "id": 1,
        "params": {}
    }


def get_request_of_icx_getTransactionResult(tx_hash: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 40889,
        "method": "icx_getTransactionResult",
        "params": {"txHash": tx_hash}
    }


def get_request_json_of_get_icx_balance(address: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_getBalance",
        "id": 30889,
        "params": {
            "address": address
        }
    }


def get_request_json_of_send_icx(fr: str, to: str, value: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 10889,
        "params": {
            "from": fr,
            "to": to,
            "value": value,
            "fee": "0x2386f26fc10000",
            "timestamp": "0x1523327456264040",
        }
    }


def get_request_json_of_get_token_balance(to: str, addr_from: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_call",
        "id": 50889,
        "params": {
            "from": "hx0000000000000000000000000000000000000000",
            "to": to,
            "dataType": "call",
            "data": {
                "method": "balance_of",
                "params": {
                    "addr_from": addr_from
                }
            }
        }
    }


def get_request_json_of_transfer_token(fr: str, to: str, addr_to: str, value: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 110889,
        "params": {
            "from": fr,
            "to": to,
            "value": "0x0",
            "fee": "0x2386f26fc10000",
            "timestamp": "0x1523327456264040",
            "dataType": "call",
            "data": {
                "method": "transfer",
                "params": {
                    "addr_to": addr_to,
                    "value": value
                }
            }
        }
    }


def get_request_json_of_check_crowd_end(fr: str, to: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 200889,
        "params": {
            "from": fr,
            "to": to,
            "value": "0x0",
            "fee": "0x2386f26fc10000",
            "timestamp": "0x1523327456264040",
            "dataType": "call",
            "data": {
                "method": "check_goal_reached",
                "params": {}
            }
        }
    }


def get_request_json_of_crowd_withrawal(fr: str, to: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 210889,
        "params": {
            "from": fr,
            "to": to,
            "value": "0x0",
            "fee": "0x2386f26fc10000",
            "timestamp": "0x1523327456264040",
            "dataType": "call",
            "data": {
                "method": "safe_withdrawal",
                "params": {}
            }
        }
    }


def get_request_json_of_token_total_supply(token_addr: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_call",
        "id": 60889,
        "params": {
            "from": "hx0000000000000000000000000000000000000000",
            "to": token_addr,
            "dataType": "call",
            "data": {
                "method": "total_supply",
                "params": {}
            }
        }
    }


god_address = "hx0000000000000000000000000000000000000000"
token_owner_address = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
token_score_address = "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf"
crowd_sale_score_address = "cx8c814aa96fefbbb85131f87f6e0cb7878a95c1d3"
test_addr = "hxbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
treasary_address = "hx1000000000000000000000000000000000000000"


class TestTBears(unittest.TestCase):
    def setUp(self):
        self.url = "http://localhost:9000/api/v3"

    def tearDown(self):
        stop_SCORE()
        clear_SCORE()

        try:
            os.remove('logger.log')
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
            if os.path.exists('sample_crowd_sale'):
                shutil.rmtree('sample_crowd_sale')
        except:
            pass

    def test_token(self):
        init_SCORE('sample_token', 'SampleToken')
        result, _ = run_SCORE('sample_token', None, None)

        # # hello!
        # payload = get_request_json_of_call_hello()
        # res = post(self.url, payload).json()
        # # error!

        # send transaction
        payload = get_request_json_of_send_icx(fr=god_address, to=treasary_address, value=hex(10 * 10 ** 18))
        res = post(self.url, payload).json()
        tx_hash = res['result']
        self.assertTrue(isinstance(tx_hash, str))
        self.assertEqual(66, len(tx_hash))

        payload = get_request_of_icx_getTransactionResult(tx_hash)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # icx_sendTransaction error check
        payload = get_request_json_of_send_icx(fr='', to=treasary_address, value=hex(10 * 10 ** 18))
        res = post(self.url, payload).json()
        error: dict = res['error']
        self.assertTrue(isinstance(error, dict))
        code: int = error['code']
        self.assertTrue(isinstance(code, int) and code < 0)
        message: str = error['message']
        self.assertTrue(isinstance(message, str))

        # get balance
        payload = get_request_json_of_get_icx_balance(address=treasary_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # check token supply
        payload = get_request_json_of_token_total_supply(token_addr=token_score_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # check token balance
        payload = get_request_json_of_get_token_balance(addr_from=token_owner_address, to=token_score_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # send token to test_addr
        payload = get_request_json_of_transfer_token(fr=token_owner_address, addr_to=treasary_address,
                                                     value=hex(10 * 10 ** 18), to=token_score_address)
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # check token balance
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=treasary_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # icx_getTransactionResult error check
        req = get_request_of_icx_getTransactionResult(tx_hash='0x00')
        res = post(self.url, req).json()
        self.assertEqual(req['id'], res['id'])
        self.assertTrue('error' in res)
        self.assertTrue(isinstance(res['error']['code'], int))
        self.assertTrue(isinstance(res['error']['message'], str))

    def test_score_methods(self):
        make_SCORE_samples()
        result, _ = run_SCORE('sample_token', None, None)
        result, _ = run_SCORE('sample_crowd_sale', None, None)
        # seq1
        # genesis -> hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(token_owner) 10icx
        payload = get_request_json_of_send_icx(fr=god_address, to=token_owner_address, value=hex(10*10**18))
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        result = post(self.url, payload).json()['result']
        self.assertEqual(result['status'], hex(1))
        print(result)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        payload = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                     addr_to=crowd_sale_score_address, value=hex(1000*10**18))
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=crowd_sale_score_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_request_json_of_send_icx(fr=token_owner_address, to=crowd_sale_score_address,
                                               value=hex(2*10**18))
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_request_json_of_send_icx(fr=token_owner_address, to=crowd_sale_score_address,
                                               value=hex(8*10**18))
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        payload = get_request_json_of_send_icx(fr=god_address, to=test_addr, value=hex(90*10**18))
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_request_json_of_send_icx(fr=test_addr, to=crowd_sale_score_address,
                                               value=hex(90*10**18))
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_request_json_of_check_crowd_end(fr=token_owner_address, to=crowd_sale_score_address)
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq14
        # safe withrawal
        payload = get_request_json_of_crowd_withrawal(fr=token_owner_address, to=crowd_sale_score_address)
        res = post(self.url, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
