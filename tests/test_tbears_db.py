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

import os
import shutil
import unittest

from tbears.block_manager.tbears_db import TbearsDB

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))
DB_PATH = os.path.join(DIRECTORY_PATH, './.tbears_db')


class TestTBearsDB(unittest.TestCase):

    def setUp(self):
        self.TBEARS_DB = TbearsDB(TbearsDB.make_db(DB_PATH))
        self.test_key = b'test_key'
        self.test_value = b'test_value'

    def tearDown(self):
        self.TBEARS_DB.close()
        shutil.rmtree(DB_PATH)

    def test_put_and_get(self):
        # Put and get
        self.TBEARS_DB.put(self.test_key, self.test_value)
        ret = self.TBEARS_DB.get(self.test_key)
        self.assertEqual(ret, self.test_value)

        # overwrite
        overwrite_value = b'test_value_overwrite'
        self.TBEARS_DB.put(self.test_key, overwrite_value)
        ret = self.TBEARS_DB.get(self.test_key)
        self.assertEqual(ret, overwrite_value)

        # get invalid key
        ret = self.TBEARS_DB.get(b'invalid_key')
        self.assertIsNone(ret)

        # put invalid type
        self.assertRaises(TypeError, self.TBEARS_DB.put, 'test_key', self.test_value)
        self.assertRaises(TypeError, self.TBEARS_DB.put, self.test_key, 123)

    def test_delete(self):
        self.TBEARS_DB.put(self.test_key, self.test_value)
        ret = self.TBEARS_DB.get(self.test_key)
        self.assertEqual(ret, self.test_value)
        self.TBEARS_DB.delete(self.test_key)
        ret = self.TBEARS_DB.get(self.test_key)
        self.assertIsNone(ret)

    def test_iterator(self):
        self.TBEARS_DB.put(b'key1', b'value1')
        self.TBEARS_DB.put(b'key2', b'value2')
        self.TBEARS_DB.put(b'key3', b'value3')
        self.TBEARS_DB.put(b'key4', b'value4')
        i = 1

        for _, actual_value in self.TBEARS_DB.iterator():
            expected_value = ('value' + str(i)).encode()
            self.assertEqual(expected_value, actual_value)
            i += 1
