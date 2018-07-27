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
import shutil
import unittest

from tbears.server.tbears_db import TbearsDB

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))
DB_PATH = os.path.join(DIRECTORY_PATH, './.tbears_db')


class TestTBearsDB(unittest.TestCase):

    def setUp(self):
        self.TBEARS_DB = TbearsDB(TbearsDB.make_db(DB_PATH))

    def tearDown(self):
        self.TBEARS_DB.close()
        shutil.rmtree(DB_PATH)

    def test_put_and_get(self):
        # put and get
        self.TBEARS_DB.put(b'test_key', b'test_value')
        ret = self.TBEARS_DB.get(b'test_key')
        self.assertEqual(ret, b'test_value')

        # overwrite
        self.TBEARS_DB.put(b'test_key', b'test_value_overwrite')
        ret = self.TBEARS_DB.get(b'test_key')
        self.assertEqual(ret, b'test_value_overwrite')

        # get invalid key
        ret = self.TBEARS_DB.get(b'invalid_key')
        self.assertIsNone(ret)

        # put invalid type
        self.assertRaises(TypeError, self.TBEARS_DB.put, 'test_key', b'test_value')
        self.assertRaises(TypeError, self.TBEARS_DB.put, b'test_key', 123)

    def test_delete(self):
        self.TBEARS_DB.put(b'test_key', b'test_value')
        ret = self.TBEARS_DB.get(b'test_key')
        self.assertEqual(ret, b'test_value')

        self.TBEARS_DB.delete(b'test_key')
        ret = self.TBEARS_DB.get(b'test_key')
        self.assertIsNone(ret)
