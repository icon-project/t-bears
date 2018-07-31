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
import json

from tbears.util.keystore_manager import make_key_store_content
from tbears.tbears_exception import KeyStoreException
from tbears.libs.icx_signer import key_from_key_store


class TestKeyStore(unittest.TestCase):
    def test_private_key(self):
        path = 'keystoretest'
        password = 'qwer1234%'

        # make keystore file
        content = make_key_store_content(password)
        with open(path, mode='wb') as ks:
            ks.write(json.dumps(content).encode())

        # get private key from keystore file
        written_key = key_from_key_store(file_path=path, password=password)
        self.assertTrue(isinstance(written_key, bytes))

        # wrong password
        self.assertRaises(KeyStoreException, key_from_key_store, path, 'wrongpasswd')

        # wrong path
        self.assertRaises(KeyStoreException, key_from_key_store, 'wrongpath', password)
        os.remove(path)