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
import hashlib
import re

from eth_keyfile import create_keyfile_json
from secp256k1 import PrivateKey


def make_key_store_content(password):
    """ Make a content of key_store.
    :param password: Password including alphabet character, number, and special character.
    If the user doesn't give password with -p, then CLI will show the prompt and user need to type the password.
    :return:
    key_store_content(dict)
    """
    # create PrivateKey object and using this, make public key, address
    private_key_obj = PrivateKey()
    private_key = private_key_obj.private_key
    public_key = private_key_obj.pubkey.serialize(compressed=False)
    address = f'hx{address_from_public_key(public_key).hex()}'
    key_store_contents = create_keyfile_json(private_key, password.encode(), iterations=262144, kdf="scrypt")
    key_store_contents['coinType'] = 'icx'
    key_store_contents['address'] = address
    return key_store_contents


def get_public_key_from_private_key(private_key_obj) -> bytes:
    return private_key_obj.pubkey.serialize(compressed=False)


def address_from_public_key(public_key):
    return hashlib.sha3_256(public_key[1:]).digest()[-20:]


def validate_password(password) -> bool:
    """Verify the entered password.

    :param password: The password the user entered. type(str)
    :return: bool
    True: When the password is valid format
    False: When the password is invalid format
    """

    return bool(re.match(r'^(?=.*\d)(?=.*[a-zA-Z])(?=.*[!@#$%^&*()_+{}:<>?]).{8,}$', password))
