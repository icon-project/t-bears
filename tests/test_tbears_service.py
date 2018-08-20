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
import shutil
import time

from iconcommons.icon_config import IconConfig

from tbears.command.command import Command
from tbears.config.tbears_config import FN_CLI_CONF, tbears_server_config, FN_SERVER_CONF
from tbears.libs.icon_jsonrpc import IconJsonrpc, IconClient
from tbears.block_manager.message_code import Response, responseCodeMap

from tests.test_util import TEST_UTIL_DIRECTORY


class TestTBearsService(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.project_name = 'a_test'
        self.project_class = 'ATest'
        self.start_conf = None
        try:
            self.cmd.cmdServer.stop(None)
            self.cmd.cmdScore.clear(None)
        except:
            pass

    def tearDown(self):
        try:
            if os.path.exists(FN_CLI_CONF):
                os.remove(FN_CLI_CONF)
            if os.path.exists(FN_SERVER_CONF):
                os.remove(FN_SERVER_CONF)
            if os.path.exists('./tbears.log'):
                os.remove('./tbears.log')
            if os.path.exists(self.project_name):
                shutil.rmtree(self.project_name)
            self.cmd.cmdServer.stop(None)
            self.cmd.cmdScore.clear(None)
        except:
            pass

    def test_duplicated_tx(self):
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
        self.assertTrue(self.cmd.cmdServer.is_service_running())

        # prepare to send
        genesis_info = start_conf['genesis']['accounts'][0]
        from_addr = genesis_info['address']
        icon_jsonrpc = IconJsonrpc.from_string(from_addr)
        icon_client = IconClient(f'http://127.0.0.1:{start_conf["port"]}/api/v3')

        to_addr = f'hx{"d"*40}'
        timestamp = hex(int(time.time() * 10 ** 6))

        # send transaction
        request = icon_jsonrpc.sendTransaction(to=to_addr, timestamp=timestamp)
        response = icon_client.send(request)
        self.assertTrue('result' in response)

        # send again
        response = icon_client.send(request)
        self.assertTrue('error' in response)
        self.assertEqual(responseCodeMap[Response.fail_tx_invalid_duplicated_hash][1], response['error']['message'])
