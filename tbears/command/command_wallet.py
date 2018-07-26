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
from tbears.libs.icon_jsonrpc import IconClient, IconJsonrpc
from tbears.tbears_exception import TBearsCommandException
from tbears.util import is_tx_hash
from tbears.util.keystore_manager import validate_password, make_key_store_content


class CommandWallet:
    def __init__(self, subparsers):
        self._add_txresult_parser(subparsers)
        self._add_transfer_parser(subparsers)
        self._add_keystore_parser(subparsers)
        self._add_balance_parser(subparsers)
        self._add_totalsup_parser(subparsers)
        self._add_scoreapi_parser(subparsers)
        self._add_gettx_parser(subparsers)

    @staticmethod
    def _add_txresult_parser(subparsers):
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
    def _add_balance_parser(subparsers):
        parser = subparsers.add_parser('balance',
                                       help='Get balance of given address',
                                       description='Get balance of given address')
        parser.add_argument('address', help='Address to query the icx balance')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3', dest='uri')

    @staticmethod
    def _add_totalsup_parser(subparsers):
        parser = subparsers.add_parser('totalsup', help='Query total supply of icx')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3', dest='uri')

    @staticmethod
    def _add_scoreapi_parser(subparsers):
        parser = subparsers.add_parser('scoreapi', help='Get score\'s api using given score address')
        parser.add_argument('address', help='Score address to query score api')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3', dest='uri')

    @staticmethod
    def _add_gettx_parser(subparsers):
        parser = subparsers.add_parser('gettx', help='Get transaction by transaction hash',
                                       description='Get transaction by transaction hash')
        parser.add_argument('hash', help='Hash of the transaction to be queried.')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                            dest='uri')
        parser.add_argument('-c', '--config', help=f'Configuration file path. This file defines the default value for '
                                                   f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _validate_tx_hash(tx_hash):
        if not is_tx_hash(tx_hash):
            raise TBearsCommandException(f'invalid transaction hash')

    @staticmethod
    def _check_transfer(conf: dict, password: str = None):
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
        else:
            if not is_icon_address_valid(conf['from']):
                raise TBearsCommandException(f'You entered invalid address')

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
    def _check_balance(conf: dict):
        if not is_icon_address_valid(conf['address']):
            raise TBearsCommandException(f'You entered invalid address')

    @staticmethod
    def _check_scoreapi(conf: dict):
        if not (is_icon_address_valid(conf['address']) and conf['address'].startswith('cx')):
            raise TBearsCommandException(f'You entered invalid score address')

    def gettx(self, conf):
        """Query transaction using given transaction hash.

        :param conf: txresult command configuration.
        :return: result of query.
        """
        self._validate_tx_hash(conf['hash'])
        icon_client = IconClient(conf['uri'])

        response = icon_client.send(IconJsonrpc.getTransactionByHash(conf['hash']))
        print(f"Transaction: {json.dumps(response, indent=4)}")

        return response

    def txresult(self, conf):
        """Query transaction result using given transaction hash.

        :param conf: txresult command configuration.
        :return: result of query.
        """
        self._validate_tx_hash(conf['hash'])
        icon_client = IconClient(conf['uri'])

        response = icon_client.send(IconJsonrpc.getTransactionResult(conf['hash']))
        print(f"Transaction result: {json.dumps(response, indent=4)}")

        return response

    def transfer(self, conf: dict, password: str = None):
        """Transfer Icx Coin.

        :param conf: transfer command configuration.
        :param password: password of keystore
        :return: response of transfer.
        """
        password = self._check_transfer(conf, password)

        if password:
            transfer = IconJsonrpc.from_key_store(conf['keyStore'], password)
        else:
            transfer = IconJsonrpc.from_string(conf['from'])

        request = transfer.sendTransaction(to=conf['to'],
                                           value=int(conf['value']),
                                           nid=int(conf['nid'], 16))

        icon_client = IconClient(conf['uri'])
        response = icon_client.send(request=request)

        if 'result' in response:
            print('Send transfer request successfully.')
            tx_hash = response['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Got an error response')
            print(json.dumps(response, indent=4))

        return response

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

    def balance(self, conf: dict):
        """Query icx balance of given address

        :param conf: balance command configuration.
        """
        self._check_balance(conf)

        icon_client = IconClient(conf['uri'])
        response = icon_client.send(IconJsonrpc.getBalance(conf['address']))

        print(f'balance : {response["result"]}')
        return response

    @staticmethod
    def totalsup(conf: dict):
        """Query total supply of icx

        :param conf: totalsup command configuration
        """
        icon_client = IconClient(conf['uri'])
        response = icon_client.send(IconJsonrpc.getTotalSupply())

        print(f'Total supply  of Icx: {response["result"]}')

        return response

    def scoreapi(self, conf):
        """Query score API of given score address.

        :param conf: scoreapi command configuration.
        :return: result of query.
        """
        self._check_scoreapi(conf)
        icon_client = IconClient(conf['uri'])
        response = icon_client.send(IconJsonrpc.getScoreApi(conf['address']))

        print(f'scoreAPI: {response["result"]}')

        return response

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
