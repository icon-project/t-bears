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
    private_key_obj = PrivateKey()
    private_key = private_key_obj.private_key
    public_key = private_key_obj.pubkey.serialize(compressed=False)
    address = f'hx{address_from_public_key(public_key).hex()}'
    key_store_contents = create_keyfile_json(private_key, password.encode(), iterations=262144)
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
