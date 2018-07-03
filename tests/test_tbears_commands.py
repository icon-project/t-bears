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
import json
import shutil
import socket
from tbears.command import ExitCode, init_SCORE, run_SCORE, stop_SCORE, clear_SCORE
from tests.common import URL

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))


class TestTBearsCommands(unittest.TestCase):
    def setUp(self):
        self.path = './'
        self.url = URL
        self.config = None, None, os.path.join(DIRECTORY_PATH, 'test_tbears.json')

    def tearDown(self):
        clear_SCORE()
        try:
            if os.path.exists('./.test_tbears_db'):
                shutil.rmtree('./.test_tbears_db')
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

    def test_init_SCORE_1(self):
        # Case when entering the existing SCORE directory for initializing the SCORE.
        os.mkdir('./a_test_init1')
        result_code = init_SCORE('a_test_init1', "ATestInit1")
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value, result_code)
        os.rmdir('./a_test_init1')

    def test_init_SCORE_2(self):
        # Case when entering the existing SCORE path for initializing the SCORE.
        self.touch('./a_test_init2')
        result_code = init_SCORE('./a_test_init2', 'ATestInit2')
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value, result_code)
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
        result_code, _ = run_SCORE('a_test_run', *self.config)
        self.assertEqual(1, result_code)
        shutil.rmtree('./a_test_run')

    def test_stop_SCORE_1(self):
        # Case when stopping SCORE and checking if socket is unconnected.
        init_SCORE('a_test_stop', 'ATestStop')
        result_code, _ = run_SCORE('a_test_stop', *self.config)
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
        result_code, _ = run_SCORE('a_test_clear', *self.config)
        self.assertEqual(1, result_code)
        stop_SCORE()
        clear_SCORE()
        self.assertFalse(os.path.exists('./.db'))
        self.assertFalse(os.path.exists('./.score'))
        shutil.rmtree('./a_test_clear')
