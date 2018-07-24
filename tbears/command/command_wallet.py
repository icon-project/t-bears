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
import getpass
import json
import os

from iconcommons import IconConfig
from iconservice.base.address import is_icon_address_valid

from tbears.config.tbears_config import FN_CLI_CONF, tbears_cli_config
from tbears.libs.icon_client import IconClient
from tbears.libs.icon_json import get_icx_getTransactionResult_payload, get_icx_sendTransaction_payload, \
    get_dummy_icx_sendTransaction_payload
from tbears.tbears_exception import TBearsCommandException
from tbears.util import is_tx_hash, IcxSigner
from tbears.util.icx_signer import key_from_key_store
from tbears.util.keystore_manager import validate_password, make_key_store_content


class CommandWallet:
    def __init__(self, subparsers):
        self._add_result_parser(subparsers)
        self._add_transfer_parser(subparsers)
        self._add_keystore_parser(subparsers)

    @staticmethod
    def _add_result_parser(subparsers):
        parser = subparsers.add_parser('txresult', help='Get transaction result by transaction hash',
                                       description='Get transaction result by transaction hash')
        parser.add_argument('hash', help='Hash of the transaction to be queried.')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                            dest='uri')
        parser.add_argument('-c', '--config', help=f'Configuration file path. This file defines the default value for '
                                                   f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_transfer_parser(subparsers):
        parser = subparsers.add_parser('transfer', help='Transfer ICX coin.', description='Transfer ICX coin.')
        parser.add_argument('-f', '--from', help='From address. Must use with dummy type.', dest='from')
        parser.add_argument('to', help='Recipient')
        parser.add_argument("value", type=float, help='Amount of ICX coin in loop to transfer (1 icx = 1e18 loop)')
        parser.add_argument('-k', '--key-store', help='Keystore file path. Used to generate "from" address and '
                                                      'transaction signature', dest='keyStore')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                            dest='uri')
        parser.add_argument('-c', '--config',
                            help=f'Configuration file path. This file defines the default values for the properties '
                                 f'"keyStore", "uri" and "from". (default: {FN_CLI_CONF})')
        parser.add_argument('-n', '--nid', help='Network ID (default: 0x3)', dest='nid')

    @staticmethod
    def _add_keystore_parser(subparsers):
        parser = subparsers.add_parser('keystore',
                                       help='Create keystore file',
                                       description='Create keystore file in passed path.')
        parser.add_argument('path', help='path of keystore file.')

    @staticmethod
    def _check_txresult(conf: dict):
        if not is_tx_hash(conf['hash']):
            raise TBearsCommandException(f'invalid transaction hash')

    @staticmethod
    def _check_transfer(conf: dict, password: str=None):
        if not is_icon_address_valid(conf['to']):
            raise TBearsCommandException(f'You entered invalid address')

        # value must be a integer value
        if conf['value'] != float(int(conf['value'])):
            raise TBearsCommandException(f'You entered invalid value {conf["value"]}')

        if conf.get('keyStore', None):
            if not os.path.exists(conf['keyStore']):
                raise TBearsCommandException(f'There is no keystore file {conf["keyStore"]}')
            if not password:
                password = getpass.getpass("input your key store password: ")

        return password

    @staticmethod
    def _check_keystore(conf: dict, password: str):
        if os.path.exists(conf['path']):
            raise TBearsCommandException(f'{conf["path"]} must be empty')

        if not password:
            password = getpass.getpass("input your key store password: ")
        if not validate_password(password):
            raise TBearsCommandException("Password must be at least 8 characters long including alphabet, number, "
                                         "and special character.")
        return password

    @staticmethod
    def txresult(conf):
        icon_client = IconClient(conf['uri'])
        get_tx_result_payload = get_icx_getTransactionResult_payload(conf['hash'])

        response = icon_client.send(get_tx_result_payload)
        response_json = response.json()
        print(f"Transaction result: {json.dumps(response_json, indent=4)}")

        return response_json

    def transfer(self, conf: dict, password: str=None):
        icon_client = IconClient(conf['uri'])
        password = self._check_transfer(conf, password)
        nid = conf['nid']

        if password:
            sender_signer = IcxSigner(key_from_key_store(conf['keyStore'], password))
            transfer_tx_payload = get_icx_sendTransaction_payload(sender_signer, conf['to'],
                                                                  hex(int(conf['value'])), nid)
        else:
            if not is_icon_address_valid(conf['from']):
                raise TBearsCommandException(f'You entered invalid address')
            sender = conf['from']
            transfer_tx_payload = get_dummy_icx_sendTransaction_payload(sender, conf['to'],
                                                                        hex(int(conf['value'])), nid)

        response = icon_client.send(transfer_tx_payload)
        response_json = response.json()

        if 'result' in response_json:
            print('Send transfer request successfully.')
            tx_hash = response_json['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Got an error response')
            print(response_json)

        return response_json

    def keystore(self, conf: dict, password: str = None):
        """Make keystore file with passed path and password.

        :param conf: keystore command configuration
        :param password: password for keystore file
        """
        password = self._check_keystore(conf, password)

        key_store_content = make_key_store_content(password)

        with open(conf['path'], mode='wb') as ks:
            ks.write(json.dumps(key_store_content).encode())

        print(f"Made keystore file successfully")

    def check_command(self, command):
        return hasattr(self, command)

    def run(self, args):
        if not hasattr(self, args.command):
            raise TBearsCommandException(f"Invalid command {args.command}")

        # load configurations
        conf = IconConfig(FN_CLI_CONF, tbears_cli_config)
        conf.load(user_input=vars(args))

        # run command
        getattr(self, args.command)(conf)

    @staticmethod
    def get_keystore_args(path: str):
        return {
            'path': path
        }

    @staticmethod
    def get_result_config(tx_hash: str):
        conf = IconConfig(FN_CLI_CONF, tbears_cli_config)
        conf['hash'] = tx_hash
        return conf

    @staticmethod
    def get_transfer_config(key_path: str, to: str, value: float) -> dict:
        conf = IconConfig(FN_CLI_CONF, tbears_cli_config)
        conf['keyStore'] = key_path
        conf['to'] = to
        conf['value'] = value
        return conf
