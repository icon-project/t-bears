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
from tbears.util.libs.icon_json import get_icx_call_payload, get_icx_getScoreApi_payload, get_icx_getBalance_payload
from tbears.util.libs.jsonrpc_error_code import METHOD_NOT_FOUND, INVALID_PARAMS
from tbears.util.tbears_mock_server import API_PATH, init_mock_server
from tests.json_contents_for_tests import *

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

        try:
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
            if os.path.exists('./.test_tbears_db'):
                shutil.rmtree('./.test_tbears_db')
            if os.path.exists('./.score'):
                shutil.rmtree('./.score')
            if os.path.exists('./.db'):
                shutil.rmtree('./.db')
            if os.path.exists('./tbears.json'):
                os.remove('./tbears.json')
            os.remove('./tbears.log')
        except:
            pass

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.path = API_PATH
        self.app = init_mock_server()

    def test_score_queries_filed(self):
        # unknown score method test
        init_SCORE('sample_token', 'SampleToken')
        run_payload = make_install_json_payload('sample_token')
        _, response = self.app.test_client.post(self.path, json=run_payload)

        method_n_params = get_request_json_of_nonexist_method()
        payload = get_icx_call_payload(token_owner_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], METHOD_NOT_FOUND)

        # invalid param - icx get balance
        payload = get_icx_getBalance_payload('123')
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # call score method with invalid param
        method_n_params = get_params_for_get_token_balance(addr_from='123')
        payload = get_icx_call_payload(token_owner_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # call score method(invalid score address)
        method_n_params = get_params_for_get_token_balance(god_address)
        payload = get_icx_call_payload(token_owner_address, 'invalid_score_address', *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        self.assertEqual(response_json['error']['code'], INVALID_PARAMS)

        # get score api test
        payload = get_icx_getScoreApi_payload(address=token_score_address)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        api_result = response_json["result"]
        self.assertEqual(pre_define_api, api_result)

    # def test_nonexistent_score_address_query(self):
    #     init_SCORE('sample_token', 'SampleToken')
    #     run_SCORE('sample_token', None, None, TBEARS_JSON_PATH)
    #     payload = get_request_json_of_get_token_balance(to=f'cx{"0"*40}', addr_from=god_address)
    #     res = post(url, payload).json()
    #     self.assertEqual(res['result'], None)
