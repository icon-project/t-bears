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

send_icx_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 10889,
    "params": {
        "from": "",
        "to": "",
        "value": "",
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
    }
}

get_token_balance_json = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 50889,
    "params": {
        "from": "hx0000000000000000000000000000000000000000",
        "to": "",
        "dataType": "call",
        "data": {
            "method": "balance_of",
            "params": {
                "addr_from": ""
            }
        }
    }
}

icx_get_balance_json = {
    "jsonrpc": "2.0",
    "method": "icx_getBalance",
    "id": 30889,
    "params": {
        "address": ""
    }
}

transfer_token_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 110889,
    "params": {
        "from": "",
        "to": "",
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
        "dataType": "call",
        "data": {
            "method": "transfer",
            "params": {
                "addr_to": "",
                "value": ""
            }
        }
    }
}

check_crowd_sale_end_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 200889,
    "params": {
        "from": "",
        "to": "",
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

crowd_sale_withrawal_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 210889,
    "params": {
        "from": "",
        "to": "",
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
check_token_supply = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 60889,
    "params": {
        "from": "hx0000000000000000000000000000000000000000",
        "to": "",
        "dataType": "call",
        "data": {
            "method": "total_supply",
            "params": {}
        }
    }
}
method_dict = {
    'send_icx': send_icx_json,
    'get_token_balance': get_token_balance_json,
    'icx_get_balance': icx_get_balance_json,
    'transfer_token': transfer_token_json,
    'check_crowd_sale_end': check_crowd_sale_end_json,
    'crowd_sale_withrawal': crowd_sale_withrawal_json,
    'check_token_supply': check_token_supply
}


def get_payload(method: str, **kwargs):
    method_json = method_dict[method]
    for key, value in kwargs.items():
        try:
            if key == 'fr':
                method_json['params']['from'] = value
                continue
            if key == 'value1':
                method_json['params']['value'] = value
                continue
            elif key == 'value2':
                method_json['params']['data']['params']['value'] = value
                continue
            if key in method_json['params']:
                method_json['params'][key] = value
            elif key in method_json['params']['data']['params']:
                method_json['params']['data']['params'][key] = value
        except KeyError:
            continue
    return method_json


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
        result, _ = run_SCORE('sample_token')

        # send transaction
        payload = get_payload('send_icx', fr=god_address, to=treasary_address, value1=hex(10*10**18))
        res = post(self.url, payload).json()['result'][0]['status']
        self.assertEqual(res, hex(1))

        # get balance
        payload = get_payload('icx_get_balance', address=treasary_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # check token supply
        payload = get_payload('check_token_supply', to=token_score_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(1000*10**18))

        # check token balance
        payload = get_payload('get_token_balance', addr_from=token_owner_address, to=token_score_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(1000*10**18))

        # send token to test_addr
        payload = get_payload('transfer_token', fr=token_owner_address,
                              addr_to=treasary_address, value2=hex(10*10**18), to=token_score_address)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # check token balance
        payload = get_payload('get_token_balance', to=token_score_address, addr_from=treasary_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

    def test_score_methods(self):
        make_SCORE_samples()
        result, _ = run_SCORE('sample_token')
        result, _ = run_SCORE('sample_crowd_sale')
        # seq1
        # genesis -> hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(token_owner) 10icx
        payload = get_payload('send_icx', fr=god_address, to=token_owner_address, value1=hex(10*10**18))
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_payload('icx_get_balance', address=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        payload = get_payload('get_token_balance', to=token_score_address, addr_from=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        payload = get_payload('transfer_token', fr=token_owner_address, to=token_score_address,
                              addr_to=crowd_sale_score_address, value2=hex(1000*10**18))
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_payload('get_token_balance', to=token_score_address, addr_from=crowd_sale_score_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_payload('get_token_balance', to=token_score_address, addr_from=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_payload('send_icx', fr=token_owner_address, to=crowd_sale_score_address, value1=hex(2*10**18))
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_payload('icx_get_balance', address=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_payload('get_token_balance', to=token_score_address, addr_from=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_payload('send_icx', fr=token_owner_address, to=crowd_sale_score_address, value=hex(8*10**18))
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        payload = get_payload('send_icx', fr=god_address, to=test_addr, value1=hex(90*10**18))
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_payload('send_icx', fr=test_addr, to=crowd_sale_score_address, value1=hex(90*10**18))
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_payload('check_crowd_sale_end', to=crowd_sale_score_address, fr=token_owner_address)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq14
        # safe withrawal
        payload = get_payload('crowd_sale_withrawal', fr=token_owner_address, to=crowd_sale_score_address)
        res = post(self.url, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_payload('icx_get_balance', address=token_owner_address)
        res = post(self.url, payload).json()['result']
        self.assertEqual(res, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
