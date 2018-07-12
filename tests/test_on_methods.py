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

from secp256k1 import PrivateKey

from tbears.command.command_score import CommandScore
from tbears.command.command_server import CommandServer
from tbears.util import create_address
from tbears.libs.icon_json import get_icx_call_payload
from tbears.libs.icon_client import IconClient
from tests.json_contents_for_tests import *

TEST_ON_INT_SCORE_PATH = os.path.abspath(os.path.join(DIRECTORY_PATH, 'test_on_init'))
ON_INIT_PARAM_JSON_PATH = os.path.join(DIRECTORY_PATH, 'on_init_test.json')


class TestOnMethods(unittest.TestCase):
    def tearDown(self):
        CommandScore.clear()
        if os.path.exists('./logger.log'):
            os.remove('./logger.log')
        if os.path.exists('./tbears.json'):
            os.remove('./tbears.json')

    def setUp(self):
        self.url = TBEARS_LOCAL_URL
        self.private_key = PrivateKey().private_key
        self.conf = CommandScore.get_conf(ON_INIT_PARAM_JSON_PATH)
        self.icon_client = IconClient(self.conf['uri'])

    def test_on_init(self):
        CommandServer.start()
        CommandScore.deploy(TEST_ON_INT_SCORE_PATH, self.conf)
        test_on_init_address = f'cx{create_address(b"test_on_init")}'
        payload = get_icx_call_payload(god_address, test_on_init_address, 'total_supply')
        response = self.icon_client.send(payload)
        response_json = response.json()
        result = response_json['result']
        CommandServer.stop()
        self.assertEqual(result, hex(2000*10**18))
