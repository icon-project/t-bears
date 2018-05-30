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

import time
import unittest
import os
import json
import shutil
import socket
from tbears.command import ExitCode, init_SCORE, run_SCORE, stop_SCORE, clear_SCORE, make_SCORE_samples
from tbears.util import post
from .json_contents import *

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))


class TestTBears(unittest.TestCase):
    def setUp(self):
        self.path = './'
        self.send_transaction_json = send_transaction_json
        self.get_god_balance_json = god_balance_json
        self.get_test_balance_json = test_balance_json
        self.get_token_balance_json1 = token_balance_json1
        self.get_token_balance_json2 = token_balance_json2
        self.get_god_token_balance_json = token_god_balance_json
        self.token_total_supply_json = token_total_supply_json
        self.token_transfer_json = token_transfer_json
        self.url = "http://localhost:9000/api/v3"
        self.give_icx_to_token_owner_json = give_icx_to_token_owner_json

    def tearDown(self):
        clear_SCORE()

    @staticmethod
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)

    @staticmethod
    def read_zipfile_as_byte(archive_path: 'str') -> 'bytes':
        with open(archive_path, 'rb') as f:
            byte_data = f.read()
            return byte_data

    def test_init_SCORE_1(self):
        # Case when entering the existing SCORE directory for initializing the SCORE.
        os.mkdir('./a_test_init1')
        result_code = init_SCORE('a_test_init1', "ATestInit1")
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY, result_code)
        os.rmdir('./a_test_init1')

    def test_init_SCORE_2(self):
        # Case when entering the existing SCORE path for initializing the SCORE.
        TestTBears.touch('./a_test_init2')
        result_code = init_SCORE('./a_test_init2', 'ATestInit2')
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY, result_code)
        os.remove('./a_test_init2')

    def test_init_SCORE_3(self):
        # Case when entering the right path for initializing the SCORE.
        score_name = 'a_test_init3'
        result_code = init_SCORE(score_name, "ATestInit3")
        self.assertEqual(ExitCode.SUCCEEDED.value, result_code)
        with open(f'{score_name}/package.json', mode='r') as package_contents:
            package_json = json.loads(package_contents.read())
        main = package_json['main_file']
        self.assertEqual(score_name, main)
        shutil.rmtree(score_name)

    def test_run_SCORE_1(self):
        # Case when running SCORE and returning the right result code.
        init_SCORE('a_test_run', 'ATestRun')
        result_code, _ = run_SCORE('a_test_run')
        self.assertEqual(1, result_code)
        shutil.rmtree('./a_test_run')

    def test_stop_SCORE_1(self):
        # Case when stopping SCORE and checking if socket is unconnected.
        init_SCORE('a_test_stop', 'ATestStop')
        result_code, _ = run_SCORE('a_test_stop')
        self.assertEqual(1, result_code)

        stop_SCORE()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if socket is connected, the result code is 0 (false).
        result_is_unconnected = sock.connect_ex(('127.0.0.1', 9000))
        self.assertTrue(result_is_unconnected)
        shutil.rmtree('./a_test_stop')

    def test_clear_SCORE_1(self):
        # Case when clearing SCORE and checking if the directories are cleared.
        init_SCORE('a_test_clear', 'ATestClear')
        result_code, _ = run_SCORE('a_test_clear')
        self.assertEqual(1, result_code)
        stop_SCORE()
        clear_SCORE()
        self.assertFalse(os.path.exists('./.db'))
        self.assertFalse(os.path.exists('./.score'))
        shutil.rmtree('./a_test_clear')

    def test_get_balance_icx(self):
        self.run_SCORE_for_testing()
        response = post(self.url, self.get_god_balance_json).json()
        result = response["result"]
        self.assertEqual("0x2961fff8ca4a62327800000", result)
        stop_SCORE()

    def test_send_icx(self):
        self.run_SCORE_for_testing()
        post(self.url, self.send_transaction_json).json()
        res = post(self.url, self.get_test_balance_json).json()
        res_icx_val = int(res["result"], 0) / (10 ** 18)
        self.assertEqual(1.0, res_icx_val)
        stop_SCORE()

    def test_get_balance_token(self):
        self.run_SCORE_for_testing()
        result = post(self.url, self.get_god_token_balance_json)
        god_result = result.json()["result"]
        # assert 0x3635c9adc5dea00000 == 1000 * (10 ** 18)
        self.assertEqual("0x3635c9adc5dea00000", god_result)
        result2 = post(self.url, self.get_token_balance_json1)
        user_result = result2.json()["result"]
        self.assertEqual("0x0", user_result)

        stop_SCORE()

    def test_token_total_supply(self):
        self.run_SCORE_for_testing()
        result = post(self.url, self.token_total_supply_json)
        supply = result.json()["result"]
        self.assertEqual("0x3635c9adc5dea00000", supply)
        stop_SCORE()

    def test_token_transfer(self):
        self.run_SCORE_for_testing()
        post(self.url, self.give_icx_to_token_owner_json)
        post(self.url, self.token_transfer_json)
        token_balance_res1 = post(self.url, self.get_token_balance_json1)
        token_balance = token_balance_res1.json()["result"]
        self.assertEqual("0x1", token_balance)
        stop_SCORE()
        shutil.rmtree('./tokentest')

    def test_samples(self):
        make_SCORE_samples()
        sample_root_path = './scoreSample'
        self.assertTrue(os.path.exists('./sampleCrowdSale'))
        self.assertTrue(os.path.exists('./tokentest'))

    @staticmethod
    def run_SCORE_for_testing():
        # init_SCORE("a_test", "ATest")
        # run_SCORE('a_test')
        init_SCORE("tokentest", "Tokentest")
        result, _ = run_SCORE('tokentest')


if __name__ == "__main__":
    unittest.main()
