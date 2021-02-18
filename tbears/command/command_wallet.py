# -*- coding: utf-8 -*-
# Copyright 2018 ICON Foundation
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
import copy
import getpass
import json
import os
from time import time

from iconcommons import IconConfig
from iconcommons.logger.logger import Logger
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import TransactionBuilder, CallTransactionBuilder, DeployTransactionBuilder, \
    MessageTransactionBuilder, DepositTransactionBuilder
from iconsdk.exception import KeyStoreException, DataTypeException
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.utils.hexadecimal import add_0x_prefix
from iconsdk.utils.convert_type import convert_hex_str_to_int, convert_bytes_to_hex_str
from iconsdk.utils.templates import BLOCK_0_3_VERSION
from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.address import is_icon_address_valid

from tbears.config.tbears_config import FN_CLI_CONF, tbears_cli_config, keystore_test1, TBEARS_CLI_TAG
from tbears.tbears_exception import TBearsCommandException, JsonContentsException
from tbears.util.arg_parser import uri_parser
from tbears.util.argparse_type import IconAddress, IconPath, hash_type, non_negative_num_type, loop
from tbears.util.keystore_manager import validate_password
from tbears.util.transaction_logger import call_with_logger, send_transaction_with_logger


class CommandWallet:
    def __init__(self, subparsers):
        self._add_txresult_parser(subparsers)
        self._add_transfer_parser(subparsers)
        self._add_keystore_parser(subparsers)
        self._add_keyinfo_parser(subparsers)
        self._add_balance_parser(subparsers)
        self._add_totalsupply_parser(subparsers)
        self._add_scoreapi_parser(subparsers)
        self._add_txbyhash_parser(subparsers)
        self._add_lastblock_parser(subparsers)
        self._add_blockbyhash_parser(subparsers)
        self._add_blockbyheight_parser(subparsers)
        self._add_sendtx_parser(subparsers)
        self._add_call_parser(subparsers)
        self._add_block_parser(subparsers)

    @staticmethod
    def _add_block_parser(subparsers):
        parser = subparsers.add_parser('block',
                                       help="Get block info using given argument."
                                            "Only one of `number` and `hash` arguments can be passed.")
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-i', '--id', dest='hash', type=hash_type, help='Hash of the block to be queried.')
        parser.add_argument('-n', '--number', dest='number', type=non_negative_num_type,
                            help='Height of the block to be queried.')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF}). This command returns the block as it was stored.')

    @staticmethod
    def _add_lastblock_parser(subparsers):
        parser = subparsers.add_parser('lastblock', help='Get last block\'s info', description='Get last block\'s info')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF}). This command returns the block in v0.1a format')

    @staticmethod
    def _add_blockbyhash_parser(subparsers):
        parser = subparsers.add_parser('blockbyhash', help='Get block info using given block hash',
                                       description='Get block info using given block hash')
        parser.add_argument('hash', type=hash_type, help='Hash of the block to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF}). This command returns the block in v0.1a format')

    @staticmethod
    def _add_blockbyheight_parser(subparsers):
        parser = subparsers.add_parser('blockbyheight', help='Get block info using given block height',
                                       description='Get block info using given block height')
        parser.add_argument('height', type=non_negative_num_type, help='height of the block to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF}). This command returns the block in v0.1a format')

    @staticmethod
    def _add_txresult_parser(subparsers):
        parser = subparsers.add_parser('txresult', help='Get transaction result by transaction hash',
                                       description='Get transaction result by transaction hash')
        parser.add_argument('hash', type=hash_type, help='Hash of the transaction to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_transfer_parser(subparsers):
        parser = subparsers.add_parser('transfer', help='Transfer ICX coin.', description='Transfer ICX coin.')
        parser.add_argument('-f', '--from', type=IconAddress(), help='From address.')
        parser.add_argument('to', type=IconAddress(), help='Recipient')
        parser.add_argument("value", type=loop, help='Amount of ICX coin in loop to transfer (1 icx = 1e18 loop)')
        parser.add_argument('-k', '--key-store', type=IconPath(), dest='keyStore',
                            help='Keystore file path. Used to generate "from" address and transaction signature')
        parser.add_argument('-n', '--nid', help='Network ID (default: 0x3)')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-p', '--password', help='Keystore file\'s password', dest='password')
        parser.add_argument('-s', '--step-limit', dest='stepLimit', type=non_negative_num_type, help='Step limit')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default values for '
                                 f'"keyStore", "uri", "from" and "stepLimit". (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_keystore_parser(subparsers):
        parser = subparsers.add_parser('keystore',
                                       help='Create a keystore file in the specified path',
                                       description='Create keystore file in the specified path. Generate privatekey, '
                                                   'publickey pair.')
        parser.add_argument('path', type=IconPath('w'), help='Path of keystore file.')
        parser.add_argument('-p', '--password', help='Keystore file\'s password', dest='password')

    @staticmethod
    def _add_keyinfo_parser(subparsers):
        parser = subparsers.add_parser('keyinfo',
                                       help='Show a keystore information in the specified path',
                                       description="Show a keystore information(address, privateKey, publicKey) "                                                
                                                   "in the specified path. If you want to get privateKey, "
                                                   "input --private-key option"
                                       )
        parser.add_argument('path', type=IconPath(), help='Path of keystore file.')
        parser.add_argument('-p', '--password', help='Keystore file\'s password', dest='password')
        parser.add_argument('--private-key', help='option that whether show privateKey', action='store_true',
                            dest='privateKey')

    @staticmethod
    def _add_balance_parser(subparsers):
        parser = subparsers.add_parser('balance',
                                       help='Get balance of given address in loop unit',
                                       description='Get balance of given address in loop unit')
        parser.add_argument('address', type=IconAddress(), help='Address to query the ICX balance')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_totalsupply_parser(subparsers):
        parser = subparsers.add_parser('totalsupply', help='Query total supply of ICX in loop unit',
                                       description='Query total supply of ICX in loop unit')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_scoreapi_parser(subparsers):
        parser = subparsers.add_parser('scoreapi', help='Get SCORE\'s API using given SCORE address',
                                       description='Get SCORE\'s API using given SCORE address')
        parser.add_argument('address', type=IconAddress('cx'), help='SCORE address to query the API')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath,
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_txbyhash_parser(subparsers):
        parser = subparsers.add_parser('txbyhash', help='Get transaction by transaction hash',
                                       description='Get transaction by transaction hash')
        parser.add_argument('hash', type=hash_type, help='Hash of the transaction to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_sendtx_parser(subparsers):
        parser = subparsers.add_parser('sendtx', help='Request icx_sendTransaction with the specified json file and '
                                                      'keystore file. If keystore file is not given, tbears sends a '
                                                      'request as it is in the json file.',
                                       description='Request icx_sendTransaction with the specified json file and '
                                                   'keystore file. If keystore file is not given, tbears sends a '
                                                   'request as it is in the json file.')
        parser.add_argument('json_file', type=IconPath(), help='File path containing icx_sendTransaction content')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-n', '--nid', help='Network ID (default: 0x3)')
        parser.add_argument('-k', '--key-store', dest='keyStore', type=IconPath(),
                            help='Keystore file path. Used to generate "from" address and transaction signature')
        parser.add_argument('-p', '--password', help='Keystore file\'s password', dest='password')
        parser.add_argument('-s', '--step-limit', dest='stepLimit', type=non_negative_num_type, help='Step limit')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default values for '
                            f'"keyStore", "uri", "from" and "stepLimit". (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_call_parser(subparsers):
        parser = subparsers.add_parser('call', help='Request icx_call with the specified json file.',
                                       description='Request icx_call with the specified json file.')
        parser.add_argument('json_file', type=IconPath(), help='File path containing icx_call content')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

    @staticmethod
    def _check_transfer(conf: dict, password: str = None):
        if not is_icon_address_valid(conf['to']):
            raise TBearsCommandException(f'You entered invalid address')

        if conf['to'] == keystore_test1['address']:
            uri: str = conf['uri']
            index = uri.find('127.0.0.1')
            if index == -1 or uri[index + len('127.0.0.1')] != ':':
                raise TBearsCommandException(f'Do not transfer to "test1" account')

        if conf.get('keyStore', None):
            if not password:
                password = getpass.getpass("Input your keystore password: ")

        return password

    @staticmethod
    def _check_keystore(password: str):
        if not password:
            password = getpass.getpass("Input your keystore password: ")
            password_retype = getpass.getpass("Retype your keystore password: ")

            if password != password_retype:
                raise TBearsCommandException("Sorry, passwords do not match. Failed to make keystore file")

        if not validate_password(password):
            raise TBearsCommandException("Password must be at least 8 characters long including alphabet, number, "
                                         "and special character.")
        return password

    @staticmethod
    def _check_keyinfo(password: str):
        if not password:
            password = getpass.getpass("Input your keystore password: ")

        return password

    @staticmethod
    def _check_sendtx(conf: dict, password: str = None):
        if conf.get('keyStore', None):
            if not os.path.exists(conf['keyStore']):
                raise TBearsCommandException(f'There is no keystore file {conf["keyStore"]}')
            if not password:
                password = getpass.getpass("Input your keystore password: ")
        else:
            if not is_icon_address_valid(conf['from']):
                raise TBearsCommandException(f'invalid address: {conf["from"]}')

        return password

    def block(self, conf):
        """Query block with given parameter(height or hash)

        :param conf: block command configuration
        :return: result of query
        """
        uri, version = uri_parser(conf['uri'])
        icon_service, response = IconService(HTTPProvider(uri, version)), None
        hash, number = conf.get('hash'), conf.get('number')
        if hash is not None and number is not None:
            raise TBearsCommandException("Only one of id and number can be passed.")
        if hash is not None:
            response = icon_service.get_block(hash, True, BLOCK_0_3_VERSION)
        if number is not None:
            response = icon_service.get_block(convert_hex_str_to_int(number), True, BLOCK_0_3_VERSION)
        if response is None:
            raise TBearsCommandException("You have to specify block height or block hash")

        if "error" in response:
            print(json.dumps(response, indent=4))
        else:
            print(f"block info : {json.dumps(response, indent=4)}")

        return response

    def lastblock(self, conf):
        """Query last block

        :param conf: lastblock command configuration
        :return: result of query
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        response = icon_service.get_block("latest", True)

        if "error" in response:
            print(json.dumps(response, indent=4))
        else:
            print(f"block info : {json.dumps(response, indent=4)}")

        return response

    def blockbyheight(self, conf):
        """Query block with given height

        :param conf: blockbyheight command configuration
        :return: result of query
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        response = icon_service.get_block(convert_hex_str_to_int(conf['height']), True)

        if "error" in response:
            print('Got an error response')
            print(json.dumps(response, indent=4))
        else:
            print(f"block info : {json.dumps(response, indent=4)}")

        return response

    def blockbyhash(self, conf):
        """Query block with given hash

        :param conf: blockbyhash command configuration
        :return: result of query
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        response = icon_service.get_block(conf['hash'], True)

        if "error" in response:
            print('Got an error response')
            print(json.dumps(response, indent=4))
        else:
            print(f"block info : {json.dumps(response, indent=4)}")

        return response

    def txbyhash(self, conf):
        """Query transaction using given transaction hash.

        :param conf: txbyhash command configuration.
        :return: result of query.
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        response = icon_service.get_transaction(conf['hash'], True)

        if "error" in response:
            print('Got an error response')
            print(f"Can not get transaction \n{json.dumps(response, indent=4)}")
        else:
            print(f"Transaction : {json.dumps(response, indent=4)}")

        return response

    def txresult(self, conf):
        """Query transaction result using given transaction hash.

        :param conf: txresult command configuration.
        :return: result of query.
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        response = icon_service.get_transaction_result(conf['hash'], True)

        if "error" in response:
            print('Got an error response')
            print(f"Can not get transaction \n{json.dumps(response, indent=4)}")
        else:
            print(f"Transaction : {json.dumps(response, indent=4)}")

        return response

    def transfer(self, conf: dict) -> dict:
        """Transfer ICX Coin.

        :param conf: transfer command configuration.
        :return: response of transfer.
        """
        # check value type (must be int), address and keystore file
        # if valid, return user input password
        password = conf.get('password', None)
        password = self._check_transfer(conf, password)

        if password:
            try:
                wallet = KeyWallet.load(conf['keyStore'], password)
                from_ = wallet.get_address()

            except KeyStoreException as e:
                print(e.args[0])
                return None
        else:
            # make dummy wallet
            wallet = KeyWallet.create()
            from_ = conf['from']

        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        transaction = TransactionBuilder() \
            .from_(from_) \
            .to(conf['to']) \
            .value(int(conf['value'])) \
            .nid(convert_hex_str_to_int(conf['nid'])) \
            .timestamp(int(time() * 10 ** 6)) \
            .build()

        if 'stepLimit' not in conf:
            step_limit = icon_service.estimate_step(transaction)
        else:
            step_limit = convert_hex_str_to_int(conf['stepLimit'])

        transaction.step_limit = step_limit

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, wallet)

        if not password:
            signed_transaction.signed_transaction_dict['signature'] = 'sig'

        # Sends transaction and return response
        response = send_transaction_with_logger(icon_service, signed_transaction, uri)

        if 'result' in response:
            print('Send transfer request successfully.')
            tx_hash = response['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Got an error response')
            print(json.dumps(response, indent=4))

        return response

    def keystore(self, conf: dict):
        """Create a keystore file with the specified path and password.

        :param conf: keystore command configuration
        """
        # check if the given keystore file already exists, and if user input is a valid password
        password = conf.get('password', None)
        password = self._check_keystore(password)

        key_store_content = KeyWallet.create()
        key_store_content.store(conf['path'], password)

        print(f"Made keystore file successfully")

    def keyinfo(self, conf: dict):
        """Show a keystore information with the the specified path and password.

        :param conf: keyinfo command configuration
        """
        password = conf.get('password', None)
        password = self._check_keyinfo(password)

        try:
            wallet = KeyWallet.load(conf['path'], password)

            key_info = {
                "address": wallet.get_address(),
                "publicKey": convert_bytes_to_hex_str(wallet.public_key)
            }

            if conf['privateKey']:
                key_info['privateKey'] = add_0x_prefix(wallet.get_private_key())

            print(json.dumps(key_info, indent=4))

            return key_info

        except KeyStoreException as e:
            print(e.args[0])

    def balance(self, conf: dict):
        """Query icx balance of given address

        :param conf: balance command configuration.
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        response = icon_service.get_balance(conf['address'], True)

        if "error" in response:
            print('Got an error response')
            print(json.dumps(response, indent=4))
        else:
            print(f"balance in hex: {response['result']}")
            print(f"balance in decimal: {int(response['result'], 16)}")

        return response

    @staticmethod
    def totalsupply(conf: dict):
        """Query total supply of ICX

        :param conf: totalsupply command configuration
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        response = icon_service.get_total_supply(True)

        if "error" in response:
            print('Got an error response')
            print(json.dumps(response, indent=4))
        else:
            print(f'Total supply of ICX in hex: {response["result"]}')
            print(f'Total supply of ICX in decimal: {int(response["result"], 16)}')

        return response

    def scoreapi(self, conf):
        """Query score API of given score address.

        :param conf: scoreapi command configuration.
        :return: result of query.
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        response = icon_service.get_score_api(conf['address'], True)

        if "error" in response:
            print('Got an error response')
            print(f"Can not get {conf['address']}'s API\n{json.dumps(response, indent=4)}")
        else:
            print(f"SCORE API: {json.dumps(response['result'], indent=4)}")

        return response

    def sendtx(self, conf: dict):
        """Send transaction.

        :param conf: sendtx command configuration.
        :return: response of transfer.
        """
        with open(conf['json_file'], 'r') as jf:
            payload = json.load(jf)

        password = conf.get('password', None)
        password = self._check_sendtx(conf, password)
        params = payload['params']

        if password and conf.get('keyStore'):
            try:
                wallet = KeyWallet.load(conf['keyStore'], password)
                params['from'] = wallet.get_address()

            except KeyStoreException as e:
                print(e.args[0])
                return None
        else:
            # make dummy wallet
            wallet = KeyWallet.create()

        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        transaction = self.get_transaction(conf, params)
        if 'stepLimit' not in conf:
            step_limit = icon_service.estimate_step(transaction)
        else:
            step_limit = convert_hex_str_to_int(conf['stepLimit'])

        transaction.step_limit = step_limit

        signed_transaction = SignedTransaction(transaction, wallet)

        if not password:
            signed_transaction.signed_transaction_dict['signature'] = 'sig'

        # Sends transaction
        response = send_transaction_with_logger(icon_service, signed_transaction, uri)

        if 'result' in response:
            print('Send transaction request successfully.')
            tx_hash = response['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Got an error response')
            print(json.dumps(response, indent=4))

        return response

    @staticmethod
    def call(conf):
        """Request icx_call

        :param conf: call command configuration.
        :return: response of icx_call
        """
        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        with open(conf['json_file'], 'r') as jf:
            payload = json.load(jf)

        call = CallBuilder()\
            .from_(conf['from'])\
            .to(payload['params']['to'])\
            .method(payload['params']['data']['method'])\
            .params(payload['params']['data'].get('params', None))\
            .build()

        response = call_with_logger(icon_service, call, uri)

        if 'error' in response:
            print(json.dumps(response, indent=4))
        else:
            print(f'response : {json.dumps(response, indent=4)}')

        return response

    def check_command(self, command):
        return hasattr(self, command)

    def run(self, args):
        if not hasattr(self, args.command):
            raise TBearsCommandException(f"Invalid command {args.command}")

        user_input = vars(args)
        conf = self.get_icon_conf(args.command, args=user_input)

        Logger.info(f"Run '{args.command}' command with config: {conf}", TBEARS_CLI_TAG)

        # run command
        return getattr(self, args.command)(conf)

    @staticmethod
    def get_icon_conf(command: str, args: dict = None) -> dict:
        """Load config file using IconConfig instance
        config file is loaded as below priority
        system config -> default config -> user config -> user input config(higher priority)

        :param command: command name (e.g. balance)
        :param args: user input command (converted to dictionary type)
        :return: command configuration
        """
        # load configurations
        conf = IconConfig(FN_CLI_CONF, copy.deepcopy(tbears_cli_config))
        # load config file
        conf.load(config_path=args.get('config', None) if args else None)

        # move command config
        if command in conf:
            conf.update_conf(conf[command])
            del conf[command]

        # load user argument
        if args:
            conf.update_conf(args)

        return conf

    @staticmethod
    def get_transaction(conf: dict, params: dict):
        data_type = params.get('dataType')
        params_data = params.get('data', {})

        try:
            transaction_params = {
                "from_": params['from'],
                "to": params['to'],
                "nid": convert_hex_str_to_int(conf['nid']),
                "value": convert_hex_str_to_int(params.get('value', "0x0"))
            }

            if data_type is None:
                transaction_builder = TransactionBuilder(**transaction_params)
            elif data_type == "call":
                transaction_params['method'] = params_data.get('method')
                transaction_params['params'] = params_data.get('params')
                transaction_builder = CallTransactionBuilder(**transaction_params)
            elif data_type == "deploy":
                transaction_params['content'] = params_data.get('content')
                transaction_params['content_type'] = params_data.get('contentType')
                transaction_params['params'] = params_data.get('params')
                transaction_builder = DeployTransactionBuilder(**params)
            elif data_type == "message":
                transaction_params['data'] = params_data
                transaction_builder = MessageTransactionBuilder(**transaction_params)
            elif data_type == "deposit":
                transaction_params['action'] = params_data.get('action')
                transaction_params['id'] = params_data.get('id')
                transaction_builder = DepositTransactionBuilder(**transaction_params)
            else:
                raise JsonContentsException("Invalid dataType")
            transaction = transaction_builder.build()
        except KeyError:
            raise JsonContentsException("Invalid json content. check json contents")
        except TypeError:
            raise JsonContentsException("Invalid json content. check keys")
        except DataTypeException:
            raise JsonContentsException("Invalid json content. check values")
        else:
            return transaction
