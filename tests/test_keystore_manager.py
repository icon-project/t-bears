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
import unittest
import json

from tbears.util.keystore_manager import make_key_store_content
from tbears.libs.icx_signer import key_from_key_store
from tbears.command.command_wallet import CommandWallet
from tbears.tbears_exception import TBearsCommandException
from tbears.command.command import Command


class TestKeyStoreManager(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.parser = self.cmd.parser
        self.keystore_path = 'unit_test_keystore'
        self.keystore_password = 'qwer1234%'

    def tearDown(self):
        if os.path.isfile(self.keystore_path):
            os.remove(self.keystore_path)

    def test_make_key_store_content(self):
        # make keystore file
        content = make_key_store_content(self.keystore_password)
        with open(self.keystore_path, mode='wb') as ks:
            ks.write(json.dumps(content).encode())

        # get private key from keystore file
        written_key = key_from_key_store(file_path=self.keystore_path, password=self.keystore_password)
        self.assertTrue(isinstance(written_key, bytes))

        os.remove(self.keystore_path)

    def test_validate_password(self):
        # Invalid password (password length is more than 8)
        invalid_password = 'qwe123!'
        self.assertRaises(TBearsCommandException, CommandWallet._check_keystore, invalid_password)

        # Invalid password (password has to be combined with special character and alphabet and number)
        invalid_password = 'qwer12345'
        self.assertRaises(TBearsCommandException, CommandWallet._check_keystore, invalid_password)
