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
import time
import unittest
import json
import shutil
import socket
from tbears.command.command import Command
from tbears.tbears_exception import TBearsCommandException
from tbears.util.icx_signer import key_from_key_store
from tbears.config.tbears_config import FN_SERVER_CONF, FN_CLI_CONF, tbears_server_config, tbears_cli_config
from iconcommons.icon_config import IconConfig

from tests.test_util import TEST_UTIL_DIRECTORY, get_total_supply


class TestTBearsCommands(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.project_name = 'a_test'
        self.project_class = 'ATest'
        self.start_conf = None

    def tearDown(self):
        try:
            if os.path.exists(FN_CLI_CONF):
                os.remove(FN_CLI_CONF)
            if os.path.exists('./tbears.log'):
                os.remove('./tbears.log')
            if os.path.exists(self.project_name):
                shutil.rmtree(self.project_name)
            self.cmd.cmdServer.stop(None)
            self.cmd.cmdScore.clear(self.start_conf if self.start_conf else tbears_server_config)
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
        tbears_config_path = os.path.join(TEST_UTIL_DIRECTORY, f'test_tbears_server_config.json')
        start_conf = IconConfig(tbears_config_path, tbears_server_config)
        start_conf.load()
        start_conf['config'] = tbears_config_path
        self.start_conf = start_conf
        self.cmd.cmdServer.start(start_conf)
        self.assertTrue(self.cmd.cmdServer.is_server_running())

        # totalsup
        total_sup = get_total_supply(tbears_config_path)
        conf = IconConfig(FN_CLI_CONF, tbears_cli_config)
        total_supply_response = self.cmd.cmdWallet.totalsup(conf)
        self.assertEqual(total_sup, total_supply_response['result'])

        # get balance - get balance of genesis address
        genesis_info = start_conf['genesis']['accounts'][0]
        conf['address'] = genesis_info['address']
        genesis_balance = genesis_info['balance']
        get_balance_response = self.cmd.cmdWallet.balance(conf)
        self.assertEqual(genesis_balance, get_balance_response['result'])

        # get balance - get balance of treasury address
        treasury_info = start_conf['genesis']['accounts'][1]
        conf['address'] = treasury_info['address']
        treasury_balance = treasury_info['balance']
        get_balance_response = self.cmd.cmdWallet.balance(conf)
        self.assertEqual(treasury_balance, get_balance_response['result'])

        # deploy - f"-t tbears -m install"
        conf = self.cmd.cmdScore.get_score_conf(command='deploy', project=self.project_name)
        deploy_response = self.cmd.cmdScore.deploy(conf=conf)
        self.assertEqual(deploy_response.get('error', False), False)

        # result (query transaction result)
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_result_config(tx_hash)
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))

        # scoreapi
        score_address = transaction_result_response['result']['scoreAddress']
        conf['address'] = score_address
        score_api_response = self.cmd.cmdWallet.scoreapi(conf)
        self.assertFalse(score_api_response.get('error', False))

        # deploy - f"-t tbears -m update --to socreAddress from_transactionResult -c tbears_cli_config.json"
        scoreAddress = transaction_result_response['result']['scoreAddress']
        conf = self.cmd.cmdScore.get_score_conf(command='deploy', project=self.project_name)
        conf['mode'] = 'update'
        conf['to'] = scoreAddress
        conf['conf'] = './tbears_cli_config.json'
        deploy_response = self.cmd.cmdScore.deploy(conf=conf)
        self.assertEqual(deploy_response.get('error', False), False)

        # result (query transaction result)
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_result_config(tx_hash)
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))
        self.assertEqual(transaction_result_response['result']['status'], "0x1")
        self.assertEqual(transaction_result_response['result']['scoreAddress'], scoreAddress)

        # deploy - f"-t zip -m install -k test_keystore"
        conf = self.cmd.cmdScore.get_score_conf(command='deploy', project=self.project_name)
        conf['keyStore'] = os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')
        conf['contentType'] = 'zip'
        deploy_response = self.cmd.cmdScore.deploy(conf=conf, password='qwer1234%')
        self.assertEqual(deploy_response.get('error', False), False)

        # result (query transaction result)
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_result_config(tx_hash)
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))
        self.assertEqual(transaction_result_response['result']['status'], "0x1")

        # deploy - f"-t zip -m update -k test_keystore --to scoreAddres_from_transactionResult
        scoreAddress = transaction_result_response['result']['scoreAddress']
        conf = self.cmd.cmdScore.get_score_conf(command='deploy', project=self.project_name)
        conf['keyStore'] = os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')
        conf['contentType'] = 'zip'
        conf['mode'] = 'update'
        conf['to'] = scoreAddress
        deploy_response = self.cmd.cmdScore.deploy(conf=conf, password='qwer1234%')
        self.assertEqual(deploy_response.get('error', False), False)

        # result (query transaction result)
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_result_config(tx_hash)
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))
        self.assertEqual(transaction_result_response['result']['status'], "0x1")
        self.assertEqual(transaction_result_response['result']['scoreAddress'], scoreAddress)

        # gettx (query transaction)
        gettx_response = self.cmd.cmdWallet.gettx(conf)
        gettx_response_result = gettx_response['result']
        gettx_params = gettx_response_result['params']
        self.assertIn('method', gettx_response_result)
        self.assertIn('params', gettx_response_result)
        self.assertIn('from', gettx_params)
        self.assertIn('to', gettx_params)
        self.assertIn('value', gettx_params)

        # transfer
        key_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')
        conf = self.cmd.cmdWallet.get_transfer_config(key_path, f'hx123{"0"*37}', 0.3e2)
        transfer_response_json = self.cmd.cmdWallet.transfer(conf, 'qwer1234%')
        self.assertFalse(transfer_response_json.get('error', False))

        # stop
        self.cmd.cmdServer.stop(None)
        self.assertFalse(self.check_server())

        # clear
        self.cmd.cmdScore.clear(start_conf)
        self.assertFalse(os.path.exists(start_conf['scoreRootPath']))
        self.assertFalse(os.path.exists(start_conf['stateDbRootPath']))
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
