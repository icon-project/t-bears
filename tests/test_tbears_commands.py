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
from tbears.command.command import Command
from tbears.tbears_exception import TBearsCommandException
from tbears.util.icx_signer import key_from_key_store
from iconcommons.icon_config import IconConfig


class TestTBearsCommands(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()

    def tearDown(self):
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

    def check_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if socket is connected, the result code is 0 (false).
        result = sock.connect_ex(('127.0.0.1', 9000))
        sock.close()
        return result == 0

    def test_init_1(self):
        # Case when entering the existing SCORE directory for initializing the SCORE.
        project = 'a_test_init1'
        score_class = 'ATestInit1'
        conf = self.cmd.cmdUtil.get_init_args(project=project, score_class=score_class)

        os.mkdir(project)
        self.assertRaises(TBearsCommandException, self.cmd.cmdUtil.init, conf)
        os.rmdir(project)

    def test_init_2(self):
        # Case when entering the existing SCORE path for initializing the SCORE.
        project = 'a_test_init2'
        score_class = 'ATestInit2'
        conf = self.cmd.cmdUtil.get_init_args(project=project, score_class=score_class)

        self.touch(project)
        self.assertRaises(TBearsCommandException, self.cmd.cmdUtil.init, conf)
        os.remove(project)

    def test_init_3(self):
        # Case when entering the right path for initializing the SCORE.
        project = 'a_test_init3'
        score_class = 'ATestInit3'
        conf = self.cmd.cmdUtil.get_init_args(project=project, score_class=score_class)
        self.cmd.cmdUtil.init(conf)

        with open(f'{project}/package.json', mode='r') as package_contents:
            package_json = json.loads(package_contents.read())
        main = package_json['main_file']
        self.assertEqual(project, main)
        shutil.rmtree(project)

    def test_start_deploy_stop_clean(self):
        # test start, deploy, stop, clean command
        project = 'a_test'
        score_class = 'ATest'
        conf = self.cmd.cmdUtil.get_init_args(project=project, score_class=score_class)

        # init
        self.cmd.cmdUtil.init(conf)

        # start

        self.cmd.cmdServer.start(conf=IconConfig(""))
        self.assertTrue(self.check_server())

        # deploy
        conf = self.cmd.cmdScore.get_deploy_conf(project=project)
        response = self.cmd.cmdScore.deploy(conf=conf)
        self.assertEqual(response.get('error', False), False)

        # stop
        self.cmd.cmdServer.stop(None)
        self.assertFalse(self.check_server())

        # clear
        self.cmd.cmdScore.clear(None)
        self.assertFalse(os.path.exists('./.db'))
        self.assertFalse(os.path.exists('./.score'))
        shutil.rmtree(f'./{project}')

    def test_keystore(self):
        path = './kkeystore'
        password = '1234qwer%'

        # make keystore file
        conf = self.cmd.cmdUtil.get_keystore_args(path=path)
        self.cmd.cmdUtil.keystore(conf, password)
        self.assertTrue(os.path.exists(path))

        # get private key from file
        try:
            key_from_key_store(file_path=path, password=password)
        except:
            exception_raised = True
        else:
            exception_raised = False
        self.assertFalse(exception_raised)


        os.remove(path)
