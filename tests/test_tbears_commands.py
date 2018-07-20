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
from tbears.config.tbears_config import tbears_config
from iconcommons.icon_config import IconConfig

from tests.test_util import TEST_UTIL_DIRECTORY


class TestTBearsCommands(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.project_name = 'a_test'
        self.project_class = 'ATest'

    def tearDown(self):
        try:
            if os.path.exists('./deploy.json'):
                os.remove('./deploy.json')
            if os.path.exists('./tbears.log'):
                os.remove('./tbears.log')
            if os.path.exists('./a_test'):
                shutil.rmtree(self.project_name)
            self.cmd.cmdServer.stop(None)
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
        conf = self.cmd.cmdUtil.get_init_args(project=self.project_name, score_class=self.project_class)

        os.mkdir(self.project_name)
        self.assertRaises(TBearsCommandException, self.cmd.cmdUtil.init, conf)
        os.rmdir(self.project_name)

    def test_init_2(self):
        # Case when entering the existing SCORE path for initializing the SCORE.
        conf = self.cmd.cmdUtil.get_init_args(project=self.project_name, score_class=self.project_class)

        self.touch(self.project_name)
        self.assertRaises(TBearsCommandException, self.cmd.cmdUtil.init, conf)
        os.remove(self.project_name)

    def test_init_3(self):
        # Case when entering the right path for initializing the SCORE.
        conf = self.cmd.cmdUtil.get_init_args(project=self.project_name, score_class=self.project_class)
        self.cmd.cmdUtil.init(conf)

        with open(f'{self.project_name}/package.json', mode='r') as package_contents:
            package_json = json.loads(package_contents.read())
        main = package_json['main_file']
        self.assertEqual(self.project_name, main)
        shutil.rmtree(self.project_name)

    def test_start_deploy_transfer_result_stop_clean(self):
        # test start, deploy, stop, clean command
        conf = self.cmd.cmdUtil.get_init_args(project=self.project_name, score_class=self.project_class)

        # init
        self.cmd.cmdUtil.init(conf)

        # start
        tbears_config_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears.json')
        start_conf = IconConfig(tbears_config_path, tbears_config)
        start_conf.load()
        start_conf['config'] = tbears_config_path
        self.cmd.cmdServer.start(start_conf)
        self.assertTrue(self.check_server())

        # deploy
        conf = self.cmd.cmdScore.get_deploy_conf(project=self.project_name)
        deploy_response = self.cmd.cmdScore.deploy(conf=conf)
        self.assertEqual(deploy_response.get('error', False), False)

        # result (query transaction result)
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_result_config(tx_hash)
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))

        # transfer
        key_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')
        conf = self.cmd.cmdWallet.get_transfer_config(key_path, f'hx123{"0"*37}', 1.3e2)
        conf['txType'] = 'real'
        transfer_response_json = self.cmd.cmdWallet.transfer(conf, 'qwer1234%')
        self.assertFalse(transfer_response_json.get('error', False))

        # stop
        self.cmd.cmdServer.stop(None)
        self.assertFalse(self.check_server())

        # clear
        self.cmd.cmdScore.clear(start_conf)
        self.assertFalse(os.path.exists('./.score'))
        self.assertFalse(os.path.exists('./.db'))
        shutil.rmtree(f'./{self.project_name}')

    def test_keystore(self):
        path = './kkeystore'
        password = '1234qwer%'

        # make keystore file
        conf = self.cmd.cmdWallet.get_keystore_args(path=path)
        self.cmd.cmdWallet.keystore(conf, password)
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
