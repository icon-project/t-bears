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
from tbears.tbears.command import ExitCode, init, start_server, stop_server, run, stop, clear
from tbears.tbears.util import post
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
        self.url = "http://localhost:9000/api/v2"
        self.give_icx_to_token_owner_json = give_icx_to_token_owner_json

    def tearDown(self):
        clear()

    @staticmethod
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)

    @staticmethod
    def read_zipfile_as_byte(archive_path: 'str') -> 'bytes':
        with open(archive_path, 'rb') as f:
            byte_data = f.read()
            return byte_data

    def test_init(self):
        # Case when user entered a exists directory path for project init.
        os.mkdir('./temp')
        ret1 = init('temp', "TempScore")
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY, ret1)
        os.rmdir('./temp')

        # Case when user entered a exists file path for project init.
        TestTBears.touch('./tmpfile')
        ret2 = init('./tmpfile', 'TestScore')
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY, ret2)
        os.remove('./tmpfile')

        # Case when user entered a appropriate path for project init.
        project_name = 'tbear_test'
        ret3 = init(project_name, "TestScore")
        self.assertEqual(ExitCode.SUCCEEDED.value, ret3)
        with open(f'{project_name}/package.json', mode='r') as package_contents:
            package_json = json.loads(package_contents.read())
        main = package_json['main_file']
        self.assertEqual(project_name, main)
        shutil.rmtree(project_name)

    def test_stop_server(self):
        start_server()
        time.sleep(1)
        stop_server()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9000))

        self.assertFalse(result is 0)

    def test_run(self):
        init('asdf', 'Asdf')
        result = run('asdf')
        self.assertEqual(1, result)
        stop_server()
        shutil.rmtree('./asdf')

    def test_clear(self):
        start_server()
        time.sleep(0.5)
        clear()
        self.assertTrue(os.path.exists('./.db') is False)
        self.assertTrue(os.path.exists('./.score') is False)
        stop_server()

    def test_get_balance_icx(self):
        self.run_server()
        response = post(self.url, self.get_god_balance_json).json()
        result = response["result"]
        self.assertEqual("0x2961fff8ca4a62327800000", result)
        stop_server()

    def test_send_icx(self):
        self.run_server()
        post(self.url, self.send_transaction_json).json()
        res = post(self.url, self.get_test_balance_json).json()
        res_icx_val = int(res["result"], 0) / (10**18)
        self.assertEqual(1.0, res_icx_val)
        stop_server()

    def test_get_balance_token(self):
        self.run_server()
        result = post(self.url, self.get_god_token_balance_json)
        god_result = result.json()["result"]
        # assert 0x3635c9adc5dea00000 == 1000 * (10 ** 18)
        self.assertEqual("0x3635c9adc5dea00000", god_result)
        result2 = post(self.url, self.get_token_balance_json1)
        user_result = result2.json()["result"]
        self.assertEqual("0x0", user_result)

        stop_server()

    def test_token_total_supply(self):
        self.run_server()
        result = post(self.url, self.token_total_supply_json)
        supply = result.json()["result"]
        self.assertEqual("0x3635c9adc5dea00000", supply)
        stop_server()

    def test_token_transfer(self):
        self.run_server()
        post(self.url, self.give_icx_to_token_owner_json)
        post(self.url, self.token_transfer_json)
        token_balance_res1 = post(self.url, self.get_token_balance_json1)
        token_balance = token_balance_res1.json()["result"]
        self.assertEqual("0x1", token_balance)
        stop_server()

    @staticmethod
    def run_server():
        init("tokentest", "Tokentest")
        run('tokentest')


if __name__ == "__main__":
    unittest.main()
