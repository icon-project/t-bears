#
# Copyright 2019 ICON Foundation
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
#

import os
import shutil
import socket
import time
import unittest

from iconcommons.icon_config import IconConfig
from iconservice.base.address import Address, AddressPrefix

from tbears.command.command import Command
from tbears.command.command_server import TBEARS_CLI_ENV
from tbears.config.tbears_config import FN_SERVER_CONF, FN_CLI_CONF, tbears_server_config

from tests.test_util import TEST_DIRECTORY, TEST_UTIL_DIRECTORY, zip_dir


class TestCommandScore(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.project_name = 'sample_prj'
        self.project_class = 'SampleClass'
        self.start_conf = None

        tbears_config_path = os.path.join(TEST_UTIL_DIRECTORY, f'test_tbears_server_config.json')
        start_conf = IconConfig(tbears_config_path, tbears_server_config)
        start_conf.load()
        start_conf['config'] = tbears_config_path
        self.start_conf = start_conf

    def tearDown(self):
        try:
            if os.path.exists(f'{self.project_name}.zip'):
                os.remove(f'{self.project_name}.zip')
            if os.path.exists(FN_CLI_CONF):
                os.remove(FN_CLI_CONF)
            if os.path.exists(FN_SERVER_CONF):
                os.remove(FN_SERVER_CONF)
            if os.path.exists('./tbears.log'):
                os.remove('./tbears.log')
            if os.path.exists(self.project_name):
                shutil.rmtree(self.project_name)
            self.cmd.cmdServer.stop(None)
            if os.path.exists('exc'):
                shutil.rmtree('exc')
            self.cmd.cmdScore.clear(self.start_conf if self.start_conf else tbears_server_config)
        except:
            pass

    @staticmethod
    def check_server():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if socket is connected, the result code is 0 (false).
        result = sock.connect_ex(('127.0.0.1', 9000))
        sock.close()
        return result == 0

    def deploy_cmd(self, conf: dict, password: str = None) -> dict:
        conf['password'] = password
        response = self.cmd.cmdScore.deploy(conf=conf)
        # Wait until block_manager confirm block. block_manager for test confirm every second
        time.sleep(2)
        return response

    def test_deploy_command(self):
        # make sample project
        conf = self.cmd.cmdUtil.get_init_args(project=self.project_name, score_class=self.project_class)
        self.cmd.cmdUtil.init(conf)

        # make project zip file
        zip_dir(self.project_name)

        # start
        self.cmd.cmdServer.start(self.start_conf)
        self.assertTrue(self.cmd.cmdServer.is_service_running())

        # deploy - install success #1 (without stepLimit)
        args = {"from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6"}
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=self.project_name, args=args)
        deploy_response = self.deploy_cmd(conf=conf)
        self.assertEqual(deploy_response.get('error', False), False)
        # check result
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        score_address = transaction_result_response['result']['scoreAddress']
        self.assertFalse(transaction_result_response.get('error', False))

        # deploy - install success #2 (without stepLimit, with keystore)
        args['keyStore'] = os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=self.project_name, args=args)
        deploy_response = self.deploy_cmd(conf=conf, password='qwer1234%')
        self.assertEqual(deploy_response.get('error', False), False)
        # check result
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        score_address = transaction_result_response['result']['scoreAddress']
        self.assertFalse(transaction_result_response.get('error', False))

        # deploy - install fail #1 (apply stepLimit with command line argument)
        args["stepLimit"] = "0x1"
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=self.project_name, args=args)
        deploy_response = self.deploy_cmd(conf=conf, password='qwer1234%')
        self.assertIsInstance(deploy_response.get('error', False), dict)

        # deploy - install fail #2 (apply stepLimit with config file)
        tbears_cli_config_step_set_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config_step_set.json')
        args = {"config": tbears_cli_config_step_set_path}
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=self.project_name, args=args)
        deploy_response = self.deploy_cmd(conf=conf)
        self.assertIsInstance(deploy_response.get('error', False), dict)

        # deploy - update case1 (not using stepLimit config)
        args = {"from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6", "to": score_address}
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=self.project_name, args=args)
        deploy_response = self.deploy_cmd(conf=conf)
        self.assertEqual(deploy_response.get('error', False), False)
        # check result
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        score_address = transaction_result_response['result']['scoreAddress']
        self.assertFalse(transaction_result_response.get('error', False))

        # deploy - update case2 (using stepLimit config with command line argument)
        args["stepLimit"] = "0x1"
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=self.project_name, args=args)
        deploy_response = self.deploy_cmd(conf=conf)
        self.assertIsInstance(deploy_response.get('error', False), dict)

        # deploy - update case3 (using stepLimit config with config file)
        tbears_cli_config_step_set_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config_step_set.json')
        args = {"config": tbears_cli_config_step_set_path, "to": score_address}
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=self.project_name, args=args)
        deploy_response = self.deploy_cmd(conf=conf)
        self.assertIsInstance(deploy_response.get('error', False), dict)

        # stop
        self.cmd.cmdServer.stop(None)
        self.assertFalse(self.check_server())
        self.assertTrue(os.path.exists(TBEARS_CLI_ENV))

        # clear
        self.cmd.cmdScore.clear(self.start_conf)
        self.assertFalse(os.path.exists(self.start_conf['scoreRootPath']))
        self.assertFalse(os.path.exists(self.start_conf['stateDbRootPath']))
        self.assertFalse(os.path.exists(TBEARS_CLI_ENV))

    def test_deploy_command_with_score_params(self):
        # start
        self.cmd.cmdServer.start(self.start_conf)
        self.assertTrue(self.cmd.cmdServer.is_service_running())

        project_name = os.path.join(TEST_DIRECTORY, "simpleScore2")

        # deploy - install with scoreParams
        deploy_args = {
            "mode": "install",
            "from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6",
            "scoreParams": {
                "score_address": str(Address.from_prefix_and_int(AddressPrefix.CONTRACT, 123))
            }
        }
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=project_name, args=deploy_args)
        deploy_response = self.deploy_cmd(conf=conf)
        self.assertEqual(deploy_response.get('error', False), False)
        # check result
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txbyhash', {'hash': tx_hash})
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        score_address = transaction_result_response['result']['scoreAddress']
        self.assertFalse(transaction_result_response.get('error', False))

        # deploy - update with scoreParams
        deploy_args["mode"] = "update"
        deploy_args["to"] = score_address
        deploy_args["scoreParams"] = { "value": "test_value"}
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=project_name, args=deploy_args)
        deploy_response = self.deploy_cmd(conf=conf)
        self.assertEqual(deploy_response.get('error', False), False)
        # check result
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        score_address = transaction_result_response['result']['scoreAddress']
        self.assertFalse(transaction_result_response.get('error', False))
