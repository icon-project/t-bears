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
import time

from iconservice.base.address import is_icon_address_valid
from iconcommons import IconConfig

from tbears.config.tbears_config import FN_CLI_CONF, tbears_cli_config
from tbears.libs.icon_jsonrpc import IconClient, IconJsonrpc, put_signature_to_params
from tbears.libs.icx_signer import key_from_key_store, IcxSigner
from tbears.tbears_exception import TBearsCommandException
from tbears.util import is_valid_hash
from tbears.util.argparse_type import IconAddress, IconPath, hash_type
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
        parser = subparsers.add_parser('lastblock', help='Get last block\'s info')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_blockbyhash_parser(subparsers):
        parser = subparsers.add_parser('blockbyhash', help='Get last block\'s info')
        parser.add_argument('hash', type=hash_type, help='Hash of the block to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_blockbyheight_parser(subparsers):
        parser = subparsers.add_parser('blockbyheight', help='Get block\'s info using given block height')
        parser.add_argument('height', help='height of the block to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')
    @staticmethod
    def _add_txresult_parser(subparsers):
        parser = subparsers.add_parser('txresult', help='Get transaction result by transaction hash',
                                       description='Get transaction result by transaction hash')
        parser.add_argument('hash', type=hash_type, help='Hash of the transaction to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_transfer_parser(subparsers):
        parser = subparsers.add_parser('transfer', help='Transfer ICX coin.', description='Transfer ICX coin.')
        parser.add_argument('-f', '--from', type=IconAddress(), help='From address. Must use with dummy type.')
        parser.add_argument('to', type=IconAddress(), help='Recipient')
        parser.add_argument("value", type=float, help='Amount of ICX coin in loop to transfer (1 icx = 1e18 loop)')
        parser.add_argument('-k', '--key-store', type=IconPath(), dest='keyStore',
                            help='Keystore file path. Used to generate "from" address and transaction signature')
        parser.add_argument('-n', '--nid', help='Network ID (default: 0x3)')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default values for the properties '
                                 f'"keyStore", "uri" and "from". (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_keystore_parser(subparsers):
        parser = subparsers.add_parser('keystore',
                                       help='Create keystore file',
                                       description='Create keystore file in passed path.')
        parser.add_argument('path', type=IconPath('w'), help='path of keystore file.')

    @staticmethod
    def _add_balance_parser(subparsers):
        parser = subparsers.add_parser('balance',
                                       help='Get balance of given address',
                                       description='Get balance of given address')
        parser.add_argument('address', type=IconAddress(), help='Address to query the icx balance')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_totalsupply_parser(subparsers):
        parser = subparsers.add_parser('totalsupply', help='Query total supply of icx')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_scoreapi_parser(subparsers):
        parser = subparsers.add_parser('scoreapi', help='Get score\'s api using given score address')
        parser.add_argument('address', type=IconAddress('cx'), help='Score address to query score api')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath,
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_txbyhash_parser(subparsers):
        parser = subparsers.add_parser('txbyhash', help='Get transaction by transaction hash',
                                       description='Get transaction by transaction hash')
        parser.add_argument('hash', type=hash_type, help='Hash of the transaction to be queried.')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_sendtx_parser(subparsers):
        parser = subparsers.add_parser('sendtx', help='Request icx_sendTransaction with user input json file',
                                       description='Request icx_sendTransaction with user input json file')
        parser.add_argument('json_file', type=IconPath(), help='File path containing icx_sendTransaction content')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-k', '--key-store', type=IconPath(), help='Keystore file path. Used to generate "from"'
                                                                       'address and transaction signature',
                            dest='keyStore')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _add_call_parser(subparsers):
        parser = subparsers.add_parser('call', help='Request icx_call with user input json file.',
                                       description='Request icx_call with user input json file.')
        parser.add_argument('json_file', type=IconPath(), help='File path containing icx_call content')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'Configuration file path. This file defines the default value for '
                                 f'the "uri"(default: {FN_CLI_CONF})')

    @staticmethod
    def _validate_tx_hash(tx_hash):
        if not is_valid_hash(tx_hash):
            raise TBearsCommandException('invalid transaction hash')

    @staticmethod
    def _validate_block_hash(block_hash):
        if not is_valid_hash(block_hash):
            raise TBearsCommandException('invalid block hash')

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

    @staticmethod
    def _check_sendtx(conf: dict, password: str = None):
        if conf.get('keyStore', None):
            if not os.path.exists(conf['keyStore']):
                raise TBearsCommandException(f'There is no keystore file {conf["keyStore"]}')
            if not password:
                password = getpass.getpass("input your key store password: ")

        return password

    def lastblock(self, conf):
        """Query last block

        :param conf: lastblock command configuration
        :return: result of query
        """
        icon_client = IconClient(conf['uri'])

        response = icon_client.send(IconJsonrpc.getLastBlock())

        if "error" in response:
            print(json.dumps(response, indent=4))
        else:
            print(f'block info : {json.dumps(response, indent=4)}')

        return response

    def blockbyheight(self, conf):
        """Query block with given height

        :param conf: blockbyheight command configuration
        :return: result of query
        """
        icon_client = IconClient(conf['uri'])

        response = icon_client.send(IconJsonrpc.getBlockByHeight(conf['height']))

        if "error" in response:
            print(json.dumps(response, indent=4))
        else:
            print(f"block info : {json.dumps(response, indent=4)}")

        return response

    def blockbyhash(self, conf):
        """Query block with given hash

        :param conf: blockbyhash command configuration
        :return: result of query
        """
        self._validate_block_hash(conf['hash'])

        icon_client = IconClient(conf['uri'])

        response = icon_client.send(IconJsonrpc.getBlockByHash(conf['hash']))

        if "error" in response:
            print(json.dumps(response, indent=4))
        else:
            print(f"block info : {json.dumps(response, indent=4)}")

        return response

    def txbyhash(self, conf):
        """Query transaction using given transaction hash.

        :param conf: txbyhash command configuration.
        :return: result of query.
        """
        self._validate_tx_hash(conf['hash'])

        icon_client = IconClient(conf['uri'])

        response = icon_client.send(IconJsonrpc.getTransactionByHash(conf['hash']))

        if "error" in response:
            print(f"Can not get transaction \n{json.dumps(response, indent=4)}")
        else:
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

        if "error" in response:
            print(f"Can not get transaction result \n{json.dumps(response, indent=4)}")
        else:
            print(f"Transaction result: {json.dumps(response, indent=4)}")

        return response

    def transfer(self, conf: dict, password: str = None):
        """Transfer Icx Coin.

        :param conf: transfer command configuration.
        :param password: password of keystore
        :return: response of transfer.
        """
        # check value type(must be int), address and keystore file
        # if valid, return user input password
        password = self._check_transfer(conf, password)

        if password:
            transfer = IconJsonrpc.from_key_store(conf['keyStore'], password)
        else:
            transfer = IconJsonrpc.from_string(conf['from'])

        # make JSON-RPC 2.0 request standard format(dict type)
        request = transfer.sendTransaction(to=conf['to'],
                                           value=hex(int(conf['value'])),
                                           nid=conf['nid'])

        # request to rpcserver
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
        # check if same keystore file already exist, and if user input valid password
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

        if "error" in response:
            print(json.dumps(response, indent=4))
        else:
            print(f"balance : {response['result']}")
        return response

    @staticmethod
    def totalsupply(conf: dict):
        """Query total supply of icx

        :param conf: totalsupply command configuration
        """
        icon_client = IconClient(conf['uri'])

        response = icon_client.send(IconJsonrpc.getTotalSupply())

        if "error" in response:
            print(json.dumps(response, indent=4))
        else:
            print(f'Total supply of Icx: {response["result"]}')

        return response

    def scoreapi(self, conf):
        """Query score API of given score address.

        :param conf: scoreapi command configuration.
        :return: result of query.
        """
        self._check_scoreapi(conf)

        icon_client = IconClient(conf['uri'])
        response = icon_client.send(IconJsonrpc.getScoreApi(conf['address']))

        if "error" in response:
            print(f"Can not get {conf['address']}'s API\n{json.dumps(response, indent=4)}")
        else:
            print(f"SCORE API: {json.dumps(response['result'], indent=4)}")

        return response

    def sendtx(self, conf: dict, password: str = None):
        """Send transaction.

        :param conf: sendtx command configuration.
        :param password: password of keystore
        :return: response of transfer.
        """
        password = self._check_sendtx(conf, password)
        private_key = key_from_key_store(conf['keyStore'], password)
        signer = IcxSigner(private_key)
        icon_client = IconClient(conf['uri'])

        with open(conf['json_file'], 'r') as jf:
            payload = json.load(jf)

        payload['params']['from'] = f"hx{signer.address.hex()}"
        payload['params']['timestamp'] = hex(int(time.time() * 10 ** 6))
        put_signature_to_params(signer, payload['params'])
        response = icon_client.send(request=payload)

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
        icon_client = IconClient(conf['uri'])
        with open(conf['json_file'], 'r') as jf:
            payload = json.load(jf)

        response = icon_client.send(request=payload)

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
        conf = self.get_icon_conf(args.command, args= user_input)

        # run command
        getattr(self, args.command)(conf)

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
        conf = IconConfig(FN_CLI_CONF, tbears_cli_config)
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
