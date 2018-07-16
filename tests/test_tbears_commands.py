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
import unittest
import json
import shutil
import socket
from tbears.command import ExitCode
from tbears.command.command_server import CommandServer
from tbears.command.command_score import CommandScore
from tbears.command.command_util import CommandUtil


class TestTBearsCommands(unittest.TestCase):
    def setUp(self):
        self.path = './'
        self.host = '127.0.0.1'
        self.port = 9008
        self.conf = CommandScore.get_conf()
        self.conf['uri'] = f'http://{self.host}:{self.port}/api/v3'

    def tearDown(self):
        CommandScore.clear()
        try:
            if os.path.exists('./deploy.json'):
                os.remove('./deploy.json')
            if os.path.exists('./tbears.log'):
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

    def check_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if socket is connected, the result code is 0 (false).
        result = sock.connect_ex((self.host, self.port))
        sock.close()
        return result == 0

    def test_init_1(self):
        # Case when entering the existing SCORE directory for initializing the SCORE.
        os.mkdir('./a_test_init1')
        result_code = CommandServer.init('a_test_init1', "ATestInit1")
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value, result_code)
        os.rmdir('./a_test_init1')

    def test_init_2(self):
        # Case when entering the existing SCORE path for initializing the SCORE.
        self.touch('./a_test_init2')
        result_code = CommandServer.init('./a_test_init2', 'ATestInit2')
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value, result_code)
        os.remove('./a_test_init2')

    def test_init_3(self):
        # Case when entering the right path for initializing the SCORE.
        score_name = 'a_test_init3'
        result_code = CommandServer.init(score_name, "ATestInit3")
        self.assertEqual(ExitCode.SUCCEEDED.value, result_code)
        with open(f'{score_name}/package.json', mode='r') as package_contents:
            package_json = json.loads(package_contents.read())
        main = package_json['main_file']
        self.assertEqual(score_name, main)
        shutil.rmtree(score_name)

    def test_start_deploy_stop_clean(self):
        # test start, deploy, stop, clean command
        project = 'a_test'
        score_class = 'ATest'

        # init
        CommandServer.init(project=project, score_class=score_class)

        # start
        CommandServer.start(host=self.host, port=self.port)
        self.assertTrue(self.check_server())

        # deploy
        result_code, _ = CommandScore.deploy(project=project, conf=self.conf)
        self.assertEqual(1, result_code)

        # stop
        CommandServer.stop()
        self.assertFalse(self.check_server())

        # clear
        CommandScore.clear()
        self.assertFalse(os.path.exists('./.db'))
        self.assertFalse(os.path.exists('./.score'))
        shutil.rmtree(f'./{project}')

    def test_keystore(self):
        path = './kkeystore'
        password = '1234qwer%'
        result = CommandUtil.make_keystore(path, password)
        self.assertEqual(ExitCode.SUCCEEDED, result)
        self.assertTrue(os.path.exists(path))
        os.remove(path)
