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

from tbears.command import run_SCORE, clear_SCORE
from tbears.util import create_address
from tbears.util.icon_client import IconClient
from tests.common import *

TEST_ON_INT_SCORE_PATH = os.path.abspath(os.path.join(DIRECTORY_PATH, 'test_on_init'))


class TestOnMethods(unittest.TestCase):
    def tearDown(self):
        clear_SCORE()

    def setUp(self):
        self.url = URL
        self.private_key = PrivateKey().private_key
        self.icon_client = IconClient(self.url, 3, self.private_key)

    def test_on_init(self):
        run_SCORE(TEST_ON_INT_SCORE_PATH, 'install', TBEARS_JSON_PATH)
        test_on_init_address = f'cx{create_address(b"test_on_init")}'
        payload = get_request_json_of_token_total_supply(test_on_init_address)
        response = self.icon_client.send(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(2000*10**18))
