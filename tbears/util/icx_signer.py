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
import base64
import hashlib

from eth_keyfile import extract_key_from_keyfile
from secp256k1 import PrivateKey

from tbears.tbears_exception import KeyStoreException


def key_from_key_store(file_path, password) -> bytes:
    """Get private key from keystore file.

    :param file_path: keystore file path.
    :param password: password of keystore file.

    :return: private key
    """
    try:
        with open(file_path, 'rb') as file:
            private_key = extract_key_from_keyfile(file, password)
    except ValueError:
        print('check your password.')
        raise KeyStoreException
    except:
        print('check your keystore file.')
        raise KeyStoreException
    else:
        return private_key


class IcxSigner:
    """Class for make signature using private key."""

    def __init__(self, private_key: bytes):
        self._private_key = private_key
        self._private_key_object = PrivateKey(self._private_key)

    def sign_recoverable(self, msg_hash):
        """Make a recoverable signature using message hash data.
        We can extract public key from recoverable signature.

        :param msg_hash: Hash data of message. type(bytes)

        :return:
        type(tuple)
        type(bytes): 65 bytes data , type(int): recovery id
        """
        private_key_object = self._private_key_object
        recoverable_signature = private_key_object.ecdsa_sign_recoverable(msg_hash, raw=True)
        return private_key_object.ecdsa_recoverable_serialize(recoverable_signature)

    def sign(self, msg_hash) -> bytes:
        """Make base64-encoded string of recoverable signature data.
        :param msg_hash:

        :return: base64-encoded string of recoverable signature data
        """
        signature, recovery_id = self.sign_recoverable(msg_hash)
        recoverable_sig = bytes(bytearray(signature) + recovery_id.to_bytes(1, 'big'))
        return base64.b64encode(recoverable_sig)

    @property
    def public_key(self) -> bytes:
        return self._private_key_object.pubkey.serialize(compressed=False)

    @property
    def address(self) -> bytes:
        return hashlib.sha3_256(self.public_key[1:]).digest()[-20:]
