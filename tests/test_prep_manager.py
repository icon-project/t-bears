# -*- coding: utf-8 -*-
# Copyright 2017-2018 ICON Foundation
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

from tbears.block_manager.block_manager import PRepManager
from tbears.config.tbears_config import keystore_test1


PREP_LIST = [
    {
        "id": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
        "publicKey": "04a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a615b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26",
        "p2pEndPoint": "target://123.45.67.89:7100"
    },
    {
        "id": "hx13aca3210918a9b116973f3c4b27c41a54d5dad1",
        "publicKey": "0483ae642ca89c9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a615b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281e3a27",
        "p2pEndPoint": "target://210.34.56.17:7100"
    }
]


class TestTBearsPRepManager(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_prev_block_contributors_info(self):
        # There is no P-Reps
        manager = PRepManager(is_generator_rotation=True, gen_count_per_leader=1)
        info = manager.get_prev_block_contributors_info()
        self.assertEqual(keystore_test1.get('address'), info.get('prevBlockGenerator'))
        self.assertEqual(0, len(info.get('prevBlockValidators')))

        # There is 2 P-Reps
        manager = PRepManager(is_generator_rotation=True, gen_count_per_leader=1, prep_list=PREP_LIST)
        info = manager.get_prev_block_contributors_info()
        self.assertEqual(PREP_LIST[0].get('id'), info.get('prevBlockGenerator'))
        self.assertEqual(len(PREP_LIST) - 1, len(info.get('prevBlockValidators')))
        self.assertEqual(PREP_LIST[1].get('id'), info.get('prevBlockValidators')[0])

        # after rotate
        info = manager.get_prev_block_contributors_info()
        self.assertEqual(PREP_LIST[1].get('id'), info.get('prevBlockGenerator'))
        self.assertEqual(len(PREP_LIST) - 1, len(info.get('prevBlockValidators')))
        self.assertEqual(PREP_LIST[0].get('id'), info.get('prevBlockValidators')[0])
