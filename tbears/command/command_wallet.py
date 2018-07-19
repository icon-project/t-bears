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

from tbears.command.command_server import CommandServer
from tbears.config.tbears_config import deploy_config
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
        self._add_send_parser(subparsers)
        self._add_keystore_parser(subparsers)

    @staticmethod
    def _add_result_parser(subparsers):
        parser = subparsers.add_parser('result', help='Query transaction result')
        parser.add_argument('hash', help='Hash of the transaction to be queried.')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                            dest='uri')
        parser.add_argument('-c', '--config', help='config path. used to designate uri(default: ./deploy.json)')

    @staticmethod
    def _add_send_parser(subparsers):
        parser = subparsers.add_parser('send', help='Send <value>icx to <to>.')
        parser.add_argument('-f', '--from', help='From address. can be used in tbears mode.', dest='from')
        parser.add_argument('to', help='Recipient')
        parser.add_argument("value", type=float, help='Amount to transfer')
        parser.add_argument('-t', '--type', choices=['dummy', 'real'],
                            help='dummy type can be used only in tbears mode.(default: dummy)', dest='txType')
        parser.add_argument('-k', '--key-store', help='Sender\'s key store file', dest='keyStore')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                            dest='uri')
        parser.add_argument('-c', '--config', help='deploy config path (default: ./deploy.json)')

    @staticmethod
    def _add_keystore_parser(subparsers):
        parser = subparsers.add_parser('keystore',
                                       help='Create keystore file',
                                       description='Create keystore file in passed path.')
        parser.add_argument('path', help='path of keystore file.')

    @staticmethod
    def _check_result(conf: dict):
        if not is_tx_hash(conf['hash']):
            raise TBearsCommandException(f'invalid transaction hash')

    @staticmethod
    def _check_send(conf: dict, password: str=None):
        if not is_icon_address_valid(conf['to']):
            raise TBearsCommandException(f'You entered invalid address')

        if conf['txType'] == 'dummy':
            return None

        # txType is 'real'
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
            raise TBearsCommandException("Passwords must be at least 8 characters long including alphabet, number, "
                                         "and special character.")
        return password

    @staticmethod
    def result(conf):
        icon_client = IconClient(conf['uri'])
        get_tx_result_payload = get_icx_getTransactionResult_payload(conf['hash'])

        response = icon_client.send(get_tx_result_payload)
        response_json = response.json()
        print(f"Transaction result: {response_json}")

        return response_json

    def send(self, conf: dict, password: str=None):
        icon_client = IconClient(conf['uri'])
        password = self._check_send(conf, password)
        origin_value = conf['value']
        loop_value = hex(int(origin_value * 10 ** 18))

        if password:
            sender_signer = IcxSigner(key_from_key_store(conf['keyStore'], password))
            send_tx_payload = get_icx_sendTransaction_payload(sender_signer, conf['to'], loop_value)
        else:
            is_icon_address_valid(conf['from'])
            sender = conf['from']
            send_tx_payload = get_dummy_icx_sendTransaction_payload(sender, conf['to'], loop_value)

        response = icon_client.send(send_tx_payload)
        response_json = response.json()

        if 'result' in response_json:
            print('Send request successfully.')
            tx_hash = response_json['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Send request failed')
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
        conf = IconConfig('./deploy.json', deploy_config)
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
        conf = IconConfig('./deploy.json', deploy_config)
        conf['hash'] = tx_hash
        return conf

    @staticmethod
    def get_send_config(key_path: str, to: str, value: int) -> dict:
        conf = IconConfig('./deploy.json', deploy_config)
        conf['keyStore'] = key_path
        conf['to'] = to
        conf['value'] = value
        return conf
