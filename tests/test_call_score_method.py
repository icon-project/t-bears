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

import unittest
import os
import shutil
from tbears.command import init_SCORE, run_SCORE, stop_SCORE, clear_SCORE, make_SCORE_samples
from tbears.util import post
from .json_contents import *

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))


class TestCallScoreMethod(unittest.TestCase):

    def setUp(self):
        self.path = './'
        self.url = "http://localhost:9000/api/v3/"
        self.config = None, None

    def tearDown(self):
        clear_SCORE()
        if os.path.exists('./sample_token'):
            shutil.rmtree('./sample_token')
        if os.path.exists('./test_tbears_db'):
            shutil.rmtree('./test_tbears_db')

        try:
            os.remove('./tbears.log')
        except:
            pass

    @staticmethod
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)

    @staticmethod
    def read_zipfile_as_byte(archive_path: 'str') -> 'bytes':
        with open(archive_path, 'rb') as f:
            byte_data = f.read()
            return byte_data

    def test_get_balance_icx(self):
        self.run_SCORE_for_testing()
        payload = get_request_json_of_get_icx_balance(address=god_address)
        response = post(self.url, payload).json()
        result = response["result"]
        self.assertEqual("0x2961fff8ca4a62327800000", result)
        stop_SCORE()

    def test_send_icx(self):
        self.run_SCORE_for_testing()
        payload = get_request_json_of_send_icx(fr=god_address, to=test_address, value="0xde0b6b3a7640000")
        post(self.url, payload)
        payload = get_request_json_of_get_icx_balance(address=test_address)
        res = post(self.url, payload).json()
        res_icx_val = int(res["result"], 0) / (10 ** 18)
        self.assertEqual(1.0, res_icx_val)
        stop_SCORE()

    def test_get_balance_token(self):
        self.run_SCORE_for_testing()
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        result = post(self.url, payload)
        god_result = result.json()["result"]
        # assert 0x3635c9adc5dea00000 == 1000 * (10 ** 18)
        self.assertEqual("0x3635c9adc5dea00000", god_result)
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=test_address)
        result2 = post(self.url, payload)
        user_result = result2.json()["result"]
        self.assertEqual("0x0", user_result)
        stop_SCORE()

    def test_token_total_supply(self):
        self.run_SCORE_for_testing()
        payload = get_request_json_of_token_total_supply(token_addr=token_score_address)
        result = post(self.url, payload)
        supply = result.json()["result"]
        self.assertEqual("0x3635c9adc5dea00000", supply)
        stop_SCORE()

    def test_token_transfer(self):
        self.run_SCORE_for_testing()
        payload = get_request_json_of_send_icx(fr=god_address, to=token_owner_address, value="0xde0b6b3a7640000")
        post(self.url, payload)
        payload = get_request_json_of_transfer_token(fr=token_owner_address, to=token_score_address,
                                                     value="0x1", addr_to=test_address)
        post(self.url, payload)

        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=test_address)
        token_balance_res1 = post(self.url, payload)
        token_balance = token_balance_res1.json()["result"]
        self.assertEqual("0x1", token_balance)
        stop_SCORE()

    def test_samples(self):
        make_SCORE_samples()
        self.assertTrue(os.path.exists('./sample_crowd_sale'))
        self.assertTrue(os.path.exists('./sample_token'))
        shutil.rmtree('./sample_crowd_sale')
        shutil.rmtree('./sample_token')

    @staticmethod
    def run_SCORE_for_testing():
        init_SCORE("sample_token", "SampleToken")
        result, _ = run_SCORE('sample_token', None, None, os.path.join(DIRECTORY_PATH, 'test_tbears.json'))


if __name__ == "__main__":
    unittest.main()
