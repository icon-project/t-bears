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
import asyncio
import unittest

from secp256k1 import PrivateKey

from tbears.command.command_score import CommandScore
from tbears.command.command_server import CommandServer
from tbears.util import create_address, make_install_json_payload
from tbears.libs.icon_json import get_icx_call_payload
from tbears.libs.icon_client import IconClient
from tests.test_util import TEST_UTIL_DIRECTORY
from tests.test_util.json_contents_for_tests import *
from tests.test_util.tbears_mock_server import API_PATH, init_mock_server

TEST_ON_INT_SCORE_PATH = os.path.abspath(os.path.join(TEST_UTIL_DIRECTORY, 'test_on_init'))
ON_INIT_PARAM_JSON_PATH = os.path.join(DIRECTORY_PATH, 'on_init_test.json')


class TestOnMethods(unittest.TestCase):
    def tearDown(self):
        CommandScore.clear()
        if os.path.exists('./logger.log'):
            os.remove('./logger.log')
        if os.path.exists('./tbears.json'):
            os.remove('./tbears.json')

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.path = API_PATH
        self.app = init_mock_server()

    def test_on_init(self):
        install_payload = make_install_json_payload(TEST_ON_INT_SCORE_PATH, deploy_params={"init_supply": "0x7d0"})
        self.app.test_client.post(self.path, json=install_payload)
        test_on_init_address = f'cx{create_address(b"test_on_init")}'
        payload = get_icx_call_payload(god_address, test_on_init_address, 'total_supply')
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        CommandServer.stop()
        self.assertEqual(result, hex(2000*10**18))
