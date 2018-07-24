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
import base64
import hashlib

from eth_keyfile import extract_key_from_keyfile
from secp256k1 import PrivateKey, PublicKey, ECDSA
from tbears.util.icx_signer import IcxSigner, key_from_key_store
from secp256k1 import PrivateKey

from tbears.tbears_exception import KeyStoreException


class TestIcxSigner(unittest.TestCase):
    def setUp(self):
        self.test_private_key = PrivateKey()
        self.signer = IcxSigner(self.test_private_key.private_key)

        m = hashlib.sha256()
        m.update(b'message_for_test')
        # prepare massage msg_hash
        self.hashedMessage = m.digest()

    def test_sign_recoverable(self):
        # check if signature which sign_recoverable method made is vaild
        # use ecdsa_verify. to use this function, convert sign
        # check secp256k1 doc: https://github.com/ludbb/secp256k1-py

        # get sign, recovery
        sign, recovery_id = self.signer.sign_recoverable(self.hashedMessage)

        # convert recoverable sig to normal sig
        deserialized_recoverable_sig = self.test_private_key.ecdsa_recoverable_deserialize(sign, recovery_id)
        normal_sig = self.test_private_key.ecdsa_recoverable_convert(deserialized_recoverable_sig)

        # check sig
        self.assertTrue(self.test_private_key.pubkey.ecdsa_verify(self.hashedMessage, normal_sig, raw=True))

        # failure case: verify using changed message
        m = hashlib.sha256()
        m.update(b'invalid message')
        invalidMessage = m.digest()
        self.assertFalse(self.test_private_key.pubkey.ecdsa_verify(invalidMessage, normal_sig, raw=True))

        # failure case: verify using invalid private key
        invalidPrivateKey = PrivateKey()
        self.assertFalse(invalidPrivateKey.pubkey.ecdsa_verify(self.hashedMessage, normal_sig, raw=True))

    def test_sign(self):
        # check signature encoding

        # make signature
        sign = self.signer.sign(self.hashedMessage)

        decodedSign = base64.b64decode(sign)
        extracted_id = int.from_bytes(decodedSign[-1:], byteorder='big')
        extracted_sig = decodedSign[:len(decodedSign) - 1]

        expected_signature, expected_recovery_id = self.signer.sign_recoverable(self.hashedMessage)
        self.assertEqual(extracted_id, expected_recovery_id)
        self.assertEqual(extracted_sig, expected_signature)

    def test_key_from_key_store(self):
        # To-do: test private, need private key (to be implemented)
        # key_from_key_store('./tests/test_util/test_keystore', 'qwer1234%')

        self.assertRaises(KeyStoreException, key_from_key_store, './invalid_file_path', 'qwer1234%')

        self.assertRaises(KeyStoreException, key_from_key_store, './tests/test_util/test_keystore', 'qwer12')









