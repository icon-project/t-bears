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
import json
import os
import unittest

from eth_keyfile import create_keyfile_json
from secp256k1 import PrivateKey

from tbears.command import ExitCode
from tbears.command.command_util import CommandUtil
from tbears.tbears_exception import KeyStoreException
from tbears.util.icx_signer import key_from_key_store


def make_key_store_content_for_test(private_key_obj, password):
    private_key = private_key_obj.private_key
    key_store_contents = create_keyfile_json(private_key, password.encode(), iterations=262144, kdf="scrypt")
    return key_store_contents


class TestKeyStore(unittest.TestCase):

    def test_keystore(self):
        path = './kkeystore'
        password = '1234qwer%'
        result = CommandUtil.make_keystore(path, password)
        self.assertEqual(ExitCode.SUCCEEDED, result)
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_private_key(self):
        CommandUtil.make_keystore('keystoretest', 'qwer1234%')
        written_key = key_from_key_store('keystoretest', 'qwer1234%')
        self.assertTrue(isinstance(written_key, bytes))
        os.remove('keystoretest')

    def test_private_key_wrong_password(self):
        CommandUtil.make_keystore('keystoretest2', 'qwer1234%')
        self.assertRaises(KeyStoreException, key_from_key_store, 'keystoretest2', 'qwer1234')
        os.remove('keystoretest2')

    def test_private_key_wrong_path(self):
        CommandUtil.make_keystore('keystoretest2', 'qwer1234%')
        self.assertRaises(KeyStoreException, key_from_key_store, 'wrongpath', 'qwer1234')
        os.remove('keystoretest2')