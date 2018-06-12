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
import os
import shutil
import unittest

from tbears.command import init_SCORE, run_SCORE, clear_SCORE
from tbears.util import post

from .json_contents import *
from .jsonrpc_error_code import *


url = "http://localhost:9000/api/v3"


class TestTransactionResult(unittest.TestCase):

    def tearDown(self):
        clear_SCORE()

        try:
            os.remove('logger.log')
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
        except:
            pass

    def test_unknown_score_method(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_nonexist_method(token_addr=token_score_address)
        res = post(url, payload).json()
        self.assertEqual(res['result'], None)

    def test_method_not_found(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_call_hello()
        payload['method'] = 'unknown'
        res = post(url, payload).json()
        self.assertEqual(res['error']['code'], METHOD_NOT_FOUND)

    def test_invalid_param_get_balance_icx(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_get_icx_balance('123')
        res = post(url, payload).json()
        self.assertEqual(res['result'], None)

    def test_invalid_param_score(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from='123')
        res = post(url, payload).json()
        self.assertEqual(res['result'], hex(0))

    def test_invalid_score_address_query(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_get_token_balance(to='123', addr_from=god_address)
        res = post(url, payload).json()
        self.assertEqual(res['result'], None)

    def test_invalid_param_get_balance_icx(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None)
        payload = get_request_json_of_get_icx_balance('123')
        res = post(url, payload).json()
        self.assertEqual(res['result'], None)

    # def test_nonexistent_score_address_query(self):
    #     init_SCORE('sample_token', 'SampleToken')
    #     run_SCORE('sample_token', None, None)
    #     payload = get_request_json_of_get_token_balance(to=f'cx{"0"*40}', addr_from=god_address)
    #     res = post(url, payload)
    #     self.assertEqual(res['result'], None)
