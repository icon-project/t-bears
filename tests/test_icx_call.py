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


pre_define_api = \
        [
            {
                'type': 'function',
                'name': 'balance_of',
                'inputs':
                    [
                        {
                            'name': 'addr_from',
                            'type': 'Address'
                        }
                    ],
                'readonly': '0x1',
                'outputs':
                    [
                        {
                            'type': 'int'
                        }
                    ]
            },
            {
                'type': 'fallback',
                'name': 'fallback',
                'inputs': [],
            },
            {
                'type': 'function',
                'name': 'total_supply',
                'inputs': [],
                'readonly': '0x1',
                'outputs':
                    [
                        {
                            'type': 'int'
                        }
                    ]
            },
            {
                'type': 'function',
                'name': 'transfer',
                'inputs':
                    [
                        {
                            'name': 'addr_to',
                            'type': 'Address'
                        },
                        {
                            'name': 'value',
                            'type': 'int'
                        }
                    ],
                'outputs':
                    [
                        {
                            'type': 'bool'
                        }
                    ]
            },
            {
                'type': 'eventlog',
                'name': 'Transfer',
                'inputs':
                    [
                        {
                            'name': 'addr_from',
                            'type': 'Address',
                            'indexed': '0x1'
                        },
                        {
                            'name': 'addr_to',
                            'type': 'Address',
                            'indexed': '0x1'
                        },
                        {
                            'name': 'value',
                            'type': 'int',
                            'indexed': '0x1'
                        }
                    ]
            }
        ]


class TestTransactionResult(unittest.TestCase):

    def tearDown(self):
        clear_SCORE()

        try:
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
            if os.path.exists('./.test_tbears_db'):
                shutil.rmtree('./.test_tbears_db')
            os.remove('./tbears.log')
        except:
            pass

    def setUp(self):
        self.url = URL
        self.private_key = PrivateKey().private_key
        self.icon_client = IconClient(self.url, 3, self.private_key)

    def test_score_queries_filed(self):
        # unknown score method test
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_nonexist_method(token_addr=token_score_address)
        response = self.icon_client.send(CALL, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], METHOD_NOT_FOUND)

        # method not found.
        payload = get_request_json_of_call_hello()
        payload['method'] = 'unknown'
        response = self.icon_client.send(CALL, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # invalid param - icx get balance
        payload = get_request_json_of_get_icx_balance('123')
        response = self.icon_client.send(CALL, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # call score method with invalid param
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from='123')
        response = self.icon_client.send(CALL, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # call score method(invalid score address)
        payload = get_request_json_of_get_token_balance(to='123', addr_from=god_address)
        response = self.icon_client.send(CALL, payload)
        response_json = response.json()
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # get score api test
        payload = get_request_json_of_get_score_api(address=token_score_address)
        response = self.icon_client.send(API, payload)
        response_json = response.json()
        api_result = response_json["result"]
        self.assertEqual(pre_define_api, api_result)

    # def test_nonexistent_score_address_query(self):
    #     init_SCORE('sample_token', 'SampleToken')
    #     run_SCORE('sample_token', None, None, TBEARS_JSON_PATH)
    #     payload = get_request_json_of_get_token_balance(to=f'cx{"0"*40}', addr_from=god_address)
    #     res = post(url, payload).json()
    #     self.assertEqual(res['result'], None)
