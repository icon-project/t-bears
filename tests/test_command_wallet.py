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

from tbears.command.command import Command
from tbears.command.command_server import TBEARS_CLI_ENV
from tbears.config.tbears_config import FN_SERVER_CONF, FN_CLI_CONF, tbears_server_config
from tests.test_util import TEST_UTIL_DIRECTORY


class TestCommandWallet(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        # start
        tbears_config_path = os.path.join(TEST_UTIL_DIRECTORY, f'test_tbears_server_config.json')
        self.start_conf = IconConfig(tbears_config_path, tbears_server_config)
        self.start_conf.load()
        self.start_conf['config'] = tbears_config_path
        self.start_conf = self.start_conf
        self.cmd.cmdServer.start(self.start_conf)
        self.assertTrue(self.cmd.cmdServer.is_service_running())

    def tearDown(self):
        # stop
        self.cmd.cmdServer.stop(None)
        self.assertFalse(self.check_server())
        self.assertTrue(os.path.exists(TBEARS_CLI_ENV))

        # clear
        self.cmd.cmdScore.clear(self.start_conf)
        self.assertFalse(os.path.exists(self.start_conf['scoreRootPath']))
        self.assertFalse(os.path.exists(self.start_conf['stateDbRootPath']))
        self.assertFalse(os.path.exists(TBEARS_CLI_ENV))
        try:
            if os.path.exists(FN_CLI_CONF):
                os.remove(FN_CLI_CONF)
            if os.path.exists(FN_SERVER_CONF):
                os.remove(FN_SERVER_CONF)
            if os.path.exists('./tbears.log'):
                os.remove('./tbears.log')
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

    def tx_command(self, command: str, conf: dict, password: str = None) -> dict:
        conf['password'] = password
        command_handler = getattr(self.cmd.cmdWallet, command)
        response = command_handler(conf=conf)
        # Wait until block_manager confirm block. block_manager for test confirm every second
        time.sleep(2)
        return response

    def test_transfer_command(self):
        # transfer success #1 (without stepLimit)
        args = {"to": f"hx{'a'*40}", "value": 1, "from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6"}
        conf = self.cmd.cmdWallet.get_icon_conf(command='transfer', args=args)
        response = self.tx_command("transfer", conf=conf)
        self.assertEqual(response.get('error', False), False)
        # check result
        tx_hash = response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))

        # transfer success #2 (without stepLimit, with keystore)
        args = {"to": f"hx{'a'*40}", "value": 1, "from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6",
                "keyStore": os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')}
        conf = self.cmd.cmdWallet.get_icon_conf(command='transfer', args=args)
        response = self.tx_command("transfer", conf=conf, password='qwer1234%')
        self.assertEqual(response.get('error', False), False)
        # check result
        tx_hash = response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))

        # transfer fail #1 (apply stepLimit config with command line argument)
        args = {"stepLimit": "0x1", "to": f"hx{'a'*40}", "value": 1,
                "from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6"}
        conf = self.cmd.cmdScore.get_icon_conf(command='transfer', args=args)
        response = self.tx_command("transfer", conf=conf)
        self.assertIsInstance(response.get('error', False), dict)

        # transfer fail #2 (apply stepLimit config with config file)
        tbears_cli_config_step_set_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config_step_set.json')
        args = {"config": tbears_cli_config_step_set_path, "to": f"hx{'a'*40}", "value": 1,
                "from": "hxef73db5d0ad02eb1fadb37d0041be96bfa56d4e6"}
        conf = self.cmd.cmdScore.get_icon_conf(command='transfer', args=args)
        response = self.tx_command("transfer", conf=conf)
        self.assertIsInstance(response.get('error', False), dict)

    def test_sendtx_command(self):
        # use the stepLimit in the json file
        send_json_path = os.path.join(TEST_UTIL_DIRECTORY, 'send.json')
        args = {"json_file": send_json_path}
        conf = self.cmd.cmdWallet.get_icon_conf(command='sendtx', args=args)
        response = self.tx_command("sendtx", conf=conf)
        self.assertEqual(response.get('error', False), False)
        # check result
        tx_hash = response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))
        # check the stepLimit in the confirmed tx
        confirmed_transaction = self.cmd.cmdWallet.txbyhash(conf)
        self.assertTrue(confirmed_transaction['result']['stepLimit'], '0x3000000')

        # use the stepLimit in the json file, with keystore
        args["keyStore"] = os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')
        conf = self.cmd.cmdWallet.get_icon_conf(command='sendtx', args=args)
        response = self.tx_command("sendtx", conf=conf, password='qwer1234%')
        self.assertEqual(response.get('error', False), False)
        # check result
        tx_hash = response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))
        # check the stepLimit in the confirmed tx
        confirmed_transaction = self.cmd.cmdWallet.txbyhash(conf)
        self.assertTrue(confirmed_transaction['result']['stepLimit'], '0x3000000')

        # no stepLimit in the json file, invoke estimateStep
        send_json_path = os.path.join(TEST_UTIL_DIRECTORY, 'send_wo_steplimit.json')
        args = {"json_file": send_json_path}
        conf = self.cmd.cmdWallet.get_icon_conf(command='sendtx', args=args)
        response = self.tx_command("sendtx", conf=conf)
        self.assertEqual(response.get('error', False), False)
        # check result
        tx_hash = response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))

        # no stepLimit, with keystore
        send_json_path = os.path.join(TEST_UTIL_DIRECTORY, 'send_wo_steplimit.json')
        args = {"json_file": send_json_path,
                "keyStore": os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')}
        conf = self.cmd.cmdWallet.get_icon_conf(command='sendtx', args=args)
        response = self.tx_command("sendtx", conf=conf, password='qwer1234%')
        self.assertEqual(response.get('error', False), False)
        # check result
        tx_hash = response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))

        # use the stepLimit specified in the command line argument
        args = {"stepLimit": "0x1", "json_file": send_json_path}
        conf = self.cmd.cmdScore.get_icon_conf(command='sendtx', args=args)
        response = self.tx_command("sendtx", conf=conf)
        self.assertIsInstance(response.get('error', False), dict)

        # use the stepLimit in the config file
        tbears_cli_config_step_set_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config_step_set.json')
        args = {"config": tbears_cli_config_step_set_path, "json_file": send_json_path}
        conf = self.cmd.cmdScore.get_icon_conf(command='sendtx', args=args)
        response = self.tx_command("sendtx", conf=conf)
        self.assertIsInstance(response.get('error', False), dict)