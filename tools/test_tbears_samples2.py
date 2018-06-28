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

from iconservice import Address

from tbears.util import post

from tbears.command import run_SCORE, clear_SCORE, make_SCORE_samples, stop_SCORE, init_SCORE
from tbears.util.test_client import send_req

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))
TBEARS_JSON_PATH = os.path.join(DIRECTORY_PATH, 'test_tbears.json')


def get_request_json_of_call_hello():
    return {
        "jsonrpc": "2.0",
        "method": "hello",
        "id": 1,
        "params": {}
    }


def get_request_of_icx_getTransactionResult(tx_hash: str) -> dict:
    return {"txHash": tx_hash}


def get_request_json_of_get_icx_balance(address: str) -> dict:
    return {"address": address}


def get_request_json_of_send_icx(fr: str, to: str, value: str) -> dict:
    return {
        "from": fr,
        "to": to,
        "value": value,
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
    }


def get_request_json_of_get_token_balance(to: str, addr_from: str) -> dict:
    return {
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


def get_request_json_of_transfer_token(fr: str, to: str, addr_to: str, value: str) -> dict:
    return {
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


def get_request_json_of_check_crowd_end(fr: str, to: str) -> dict:
    return {
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


def get_request_json_of_crowd_withrawal(fr: str, to: str) -> dict:
    return {
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


def get_request_json_of_token_total_supply(token_addr: str) -> dict:
    return {
        "from": "hx0000000000000000000000000000000000000000",
        "to": token_addr,
        "dataType": "call",
        "data": {
            "method": "total_supply",
            "params": {}
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

    def test_score_methods(self):
        # seq1
        # genesis -> hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(token_owner) 10icx
        payload = get_request_json_of_send_icx(fr=Address.from_string(god_address),
                                               to=Address.from_string(token_owner_address),
                                               value=10*10**18)

        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        result = send_req('icx_getTransactionResult', payload).json()['result']
        self.assertEqual(result['status'], hex(1))
        print(result)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(token_owner_address))
        res = send_req('icx_getBalance', payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(token_owner_address))
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        payload = get_request_json_of_transfer_token(fr=Address.from_string(token_owner_address),
                                                     to=Address.from_string(token_score_address),
                                                     addr_to=Address.from_string(crowd_sale_score_address),
                                                     value=1000*10**18)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(crowd_sale_score_address))
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(res, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_request_json_of_send_icx(fr=token_owner_address, to=crowd_sale_score_address,
                                               value=hex(2*10**18))
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(token_owner_address))

        res = send_req('icx_getBalance', payload).json()['result']
        self.assertEqual(res, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(token_owner_address))
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(res, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(token_owner_address),
                                               to=Address.from_string(crowd_sale_score_address),
                                               value=8*10**18)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(god_address),
                                               to=Address.from_string(test_addr),
                                               value=90*10**18)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(test_addr),
                                               to=Address.from_string(crowd_sale_score_address),
                                               value=90*10**18)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_request_json_of_check_crowd_end(fr=Address.from_string(token_owner_address),
                                                      to=Address.from_string(crowd_sale_score_address))
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq14
        # safe withrawal
        payload = get_request_json_of_crowd_withrawal(fr=token_owner_address, to=crowd_sale_score_address)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        res = send_req('icx_getBalance', payload).json()['result']
        self.assertEqual(res, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
