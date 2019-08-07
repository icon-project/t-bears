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

from iconsdk.exception import KeyStoreException
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.utils.convert_type import convert_hex_str_to_bytes


def key_from_key_store(file_path, password):
    wallet = KeyWallet.load(file_path, password)
    return convert_hex_str_to_bytes(wallet.get_private_key())


class TestKeyStore(unittest.TestCase):
    def test_private_key(self):
        path = 'keystoretest'
        password = 'qwer1234%'

        content = KeyWallet.create()
        content.store(path, password)

        # get private key from keystore file
        written_key = key_from_key_store(file_path=path, password=password)
        self.assertTrue(isinstance(written_key, bytes))

        # wrong password
        self.assertRaises(KeyStoreException, key_from_key_store, path, 'wrongpasswd')

        # wrong path
        self.assertRaises(KeyStoreException, key_from_key_store, 'wrongpath', password)
        os.remove(path)