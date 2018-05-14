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
        self.get_tx_result_json = get_tx_result_json
        self.get_god_balance_json = get_god_balance_json
        self.get_test_balance_json = get_test_balance_json
        self.get_token_balance_json = get_token_balance_json
        self.token_total_supply_json = token_total_supply_json
        self.token_transfer_json = token_transfer_json
        self.url = "http://localhost:9000/api/v2"

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
        os.mkdir('./tmp')
        ret1 = init('tmp', "TempScore")
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value, ret1)
        os.rmdir('./tmp')

        # Case when user entered a exists file path for project init.
        TestTBears.touch('./tmpfile')
        ret2 = init('./tmpfile', 'TestScore')
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value, ret2)
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
        init('icxtest', 'ITest')
        run('icxtest')
        response = post(self.url, self.get_god_balance_json).json()
        result = response["result"]
        self.assertEqual("0x2961fff8ca4a62327800000", result)
        stop_server()

    def test_send_icx(self):
        init('icxtest', 'ITest')
        run('icxtest')
        post(self.url, self.send_transaction_json).json()
        res = post(self.url, self.get_test_balance_json).json()
        res_icx_val = int(res["result"], 0) / (10**18)
        self.assertEqual(1.0, res_icx_val)
        stop_server()

    # def test_send_token(self):
    #     pass
    #
    # def test_get_balance_token(self):
    #     init('icxtest', 'Itest')
    #     run('icxtest')
    #     result = post(self.url, self.get_token_balance_json)
    #     print(result.json())
    #     stop_server()


if __name__ == "__main__":
    unittest.main()
