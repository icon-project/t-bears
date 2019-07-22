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

from iconcommons import IconConfig
from iconcommons.logger.logger import Logger
from iconsdk.builder.transaction_builder import TransactionBuilder, CallTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.utils.convert_type import convert_hex_str_to_int
from iconsdk.wallet.wallet import KeyWallet

from iconservice.base.address import is_icon_address_valid

from time import time

from tbears.config.tbears_config import FN_CLI_CONF, tbears_cli_config, keystore_test1, TBEARS_CLI_TAG
from tbears.libs.icon_jsonrpc import IconClient, IconJsonrpc, get_enough_step, get_default_step
from tbears.tbears_exception import TBearsCommandException
from tbears.util import jsonrpc_params_to_pep_style
from tbears.util.arg_parser import uri_parser
from tbears.util.argparse_type import IconAddress, IconPath, hash_type, non_negative_num_type
from tbears.util.log_decorator import call_logger_deco, tx_logger_deco
from tbears.util.keystore_manager import validate_password, make_key_store_content



class CommandWallet:
    def __init__(self, subparsers):
        self._add_txresult_parser(subparsers)
        self._add_transfer_parser(subparsers)
        self._add_keystore_parser(subparsers)
        self._add_balance_parser(subparsers)
        self._add_totalsupply_parser(subparsers)
        self._add_scoreapi_parser(subparsers)
        self._add_txbyhash_parser(subparsers)
        self._add_lastblock_parser(subparsers)
        self._add_blockbyhash_parser(subparsers)
        self._add_blockbyheight_parser(subparsers)
        self._add_sendtx_parser(subparsers)
        self._add_call_parser(subparsers)

    @staticmethod
    def _add_lastblock_parser(subparsers):
        parser = subparsers.add_parser('lastblock', help='Get last block\'s info', description='Get last block\'s info')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_blockbyhash_parser(subparsers):
        parser = subparsers.add_parser('blockbyhash', help='Get block info using given block hash',
                                       description='Get block info using given block hash')
        parser.add_argument('hash', type=hash_type, help='Hash of the block to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_blockbyheight_parser(subparsers):
        parser = subparsers.add_parser('blockbyheight', help='Get block info using given block height',
                                       description='Get block info using given block height')
        parser.add_argument('height', type=non_negative_num_type, help='height of the block to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'"uri" (default: {FN_CLI_CONF})')

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
        parser.add_argument("value", type=float, help='Amount of ICX coin in loop to transfer (1 icx = 1e18 loop)')
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
                                                   'publickey pair using secp256k1 library.')
        parser.add_argument('path', type=IconPath('w'), help='Path of keystore file.')
        parser.add_argument('-p', '--password', help='Keystore file\'s password', dest='password')

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

        # value must be a integer value
        if conf['value'] != float(int(conf['value'])):
            raise TBearsCommandException(f'You entered invalid value {conf["value"]}')

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
            response = self.transfer_with_wallet(conf, password)
        else:
            response = self.transfer_without_wallet(conf)

        if 'result' in response:
            print('Send transfer request successfully.')
            tx_hash = response['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Got an error response')
            print(json.dumps(response, indent=4))

        return response

    def transfer_with_wallet(self, conf: dict, password: str) -> dict:

        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        wallet = KeyWallet.load(conf['keyStore'], password)

        transaction = TransactionBuilder()\
            .from_(wallet.get_address())\
            .to(conf['to'])\
            .value(int(conf['value']))\
            .nid(convert_hex_str_to_int(conf['nid'])) \
            .timestamp(int(time() * 10 ** 6))\
            .build()

        if 'stepLimit' not in conf:
            step_limit = icon_service.estimate_step(transaction)
        else:
            step_limit = convert_hex_str_to_int(conf['stepLimit'])

        transaction.step_limit = step_limit

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, wallet)

        # Sends transaction and return response
        send_transaction = tx_logger_deco(icon_service.send_transaction,
                                          conf['uri'],
                                          signed_transaction.signed_transaction_dict)
        return send_transaction(signed_transaction, True)

    def transfer_without_wallet(self, conf: dict) -> dict:

        if conf.get('stepLimit', None) is None:
            step_limit = hex(get_default_step(conf['uri']))
        else:
            step_limit = conf['stepLimit']

        transfer = IconJsonrpc.from_string(conf['from'])

        # make JSON-RPC 2.0 request standard format (dict type)
        request = transfer.sendTransaction(to=conf['to'],
                                           value=hex(int(conf['value'])),
                                           nid=conf['nid'],
                                           step_limit=step_limit)

        # send request to the rpc server
        icon_client = IconClient(conf['uri'])

        # return response
        return icon_client.send(request=request)

    def keystore(self, conf: dict):
        """Create a keystore file with the specified path and password.

        :param conf: keystore command configuration
        """
        # check if the given keystore file already exists, and if user input is a valid password
        password = conf.get('password', None)
        password = self._check_keystore(password)

        key_store_content = make_key_store_content(password)

        with open(conf['path'], mode='wb') as ks:
            ks.write(json.dumps(key_store_content).encode())

        print(f"Made keystore file successfully")

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

        if password:
            response = self.sendtx_with_keystore(conf, password, params, payload)
        else:
            response = self.sendtx_without_keystore(conf, params, payload)

        if 'result' in response:
            print('Send transaction request successfully.')
            tx_hash = response['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Got an error response')
            print(json.dumps(response, indent=4))

        return response

    def sendtx_with_keystore(self, conf: dict, password: str, params: dict, payload: dict) -> dict:

        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))

        wallet = KeyWallet.load(conf['keyStore'], password)

        transaction = CallTransactionBuilder()\
            .from_(wallet.get_address())\
            .to(params['to'])\
            .nid(convert_hex_str_to_int(conf['nid']))\
            .method(payload['method'])\
            .params(params)\
            .build()

        if 'stepLimit' not in conf:
            step_limit = icon_service.estimate_step(transaction)
        else:
            step_limit = convert_hex_str_to_int(conf['stepLimit'])

        transaction.step_limit = step_limit

        signed_transaction = SignedTransaction(transaction, wallet)

        # Sends transaction
        send_transaction = tx_logger_deco(icon_service.send_transaction,
                                          conf['uri'],
                                          signed_transaction.signed_transaction_dict)
        return send_transaction(signed_transaction, True)

    def sendtx_without_keystore(self, conf: dict, params: dict, payload: dict) -> dict:
        sendtx = IconJsonrpc.from_string(payload['params']['from'])
        params['from'] = None

        jsonrpc_params_to_pep_style(params)
        payload = sendtx.sendTransaction(**params)

        uri = conf['uri']
        step_limit = payload['params']['stepLimit']

        if step_limit is None:
            step_limit = conf.get('stepLimit', None)

            if step_limit is None:
                step_limit = get_enough_step(payload, uri)
            else:
                step_limit = int(step_limit, 16)

            payload['params']['stepLimit'] = hex(step_limit)
            sendtx.put_signature(payload['params'])

        # send request to the rpc server
        icon_client = IconClient(uri)
        # return response
        return icon_client.send(request=payload)

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

        call_func = call_logger_deco(icon_service.call, conf['uri'], call)
        response = call_func(call, True)

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