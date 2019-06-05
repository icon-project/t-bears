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
from tests.test_util import TEST_UTIL_DIRECTORY, zip_dir


class TestTBearsCommands(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.project_name = 'sample_prj'
        self.project_class = 'SampleClass'
        self.start_conf = None

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
        conf = self.cmd.cmdUtil.get_init_args(project=self.project_name, score_class=self.project_class)
        self.cmd.cmdUtil.init(conf)

        # make project zip file
        zip_dir(self.project_name)

        # start
        tbears_config_path = os.path.join(TEST_UTIL_DIRECTORY, f'test_tbears_server_config.json')
        start_conf = IconConfig(tbears_config_path, tbears_server_config)
        start_conf.load()
        start_conf['config'] = tbears_config_path
        self.start_conf = start_conf
        self.cmd.cmdServer.start(start_conf)
        self.assertTrue(self.cmd.cmdServer.is_service_running())

        # deploy - install case
        conf = self.cmd.cmdScore.get_icon_conf(command='deploy', project=self.project_name)
        deploy_response = self.deploy_cmd(conf=conf)
        self.assertEqual(deploy_response.get('error', False), False)

        # check result
        tx_hash = deploy_response['result']
        conf = self.cmd.cmdWallet.get_icon_conf('txresult', {'hash': tx_hash})
        transaction_result_response = self.cmd.cmdWallet.txresult(conf)
        self.assertFalse(transaction_result_response.get('error', False))

        # stop
        self.cmd.cmdServer.stop(None)
        self.assertFalse(self.check_server())
        self.assertTrue(os.path.exists(TBEARS_CLI_ENV))

        # clear
        self.cmd.cmdScore.clear(start_conf)
        self.assertFalse(os.path.exists(start_conf['scoreRootPath']))
        self.assertFalse(os.path.exists(start_conf['stateDbRootPath']))
        self.assertFalse(os.path.exists(TBEARS_CLI_ENV))
