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
import shutil
import unittest

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger

from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.utils.convert_type import convert_hex_str_to_int
from iconsdk.wallet.wallet import KeyWallet

from iconservice.base.address import is_icon_address_valid

from tbears.command.command_server import CommandServer
from tbears.config.tbears_config import FN_CLI_CONF, tbears_cli_config, TBEARS_CLI_TAG
from tbears.libs.icon_jsonrpc import IconJsonrpc, IconClient, get_enough_step
from tbears.tbears_exception import TBearsDeleteTreeException, TBearsCommandException
from tbears.util.arg_parser import uri_parser
from tbears.util.argparse_type import IconAddress, IconPath, non_negative_num_type
from tbears.util.log_decorator import tx_logger_deco


class CommandScore(object):
    def __init__(self, subparsers):
        self._add_deploy_parser(subparsers)
        self._add_clear_parser(subparsers)
        self._add_test_parser(subparsers)

    @staticmethod
    def _add_deploy_parser(subparsers):
        parser = subparsers.add_parser('deploy', help='Deploy the SCORE', description='Deploy the SCORE')
        parser.add_argument('project', type=IconPath(), help='Project directory path or zip file path')
        parser.add_argument('-u', '--node-uri', dest='uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)')
        parser.add_argument('-t', '--type', choices=['tbears', 'zip'], dest='contentType',
                            help='This option has been deprecated since v1.0.5. Deploy command supports zip type only')
        parser.add_argument('-m', '--mode', choices=['install', 'update'], help='Deploy mode (default: install)')
        # --from option only accept eoa address ('hx')
        parser.add_argument('-f', '--from', type=IconAddress('hx'), help='From address. i.e. SCORE owner address')
        # --to option is used only when update score, so eoa address ('hx') need to be denied
        parser.add_argument('-o', '--to', type=IconAddress('cx'), help='To address. i.e. SCORE address')
        # IconPath's 'r' argument means 'read file'
        parser.add_argument('-k', '--key-store', type=IconPath('r'), dest='keyStore',
                            help='Keystore file path. Used to generate "from" address and transaction signature')
        parser.add_argument('-n', '--nid', type=non_negative_num_type, help='Network ID')
        parser.add_argument('-p', '--password', help='keystore file\'s password', dest='password')
        parser.add_argument('-s', '--step-limit', dest='stepLimit', type=non_negative_num_type, help='Step limit')
        parser.add_argument('-c', '--config', type=IconPath(), help=f'deploy config path (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_clear_parser(subparsers):
        subparsers.add_parser('clear', help='Clear all SCOREs deployed on tbears service',
                              description='Clear all SCOREs deployed on local tbears service')

    @staticmethod
    def _add_test_parser(subparsers):
        parser = subparsers.add_parser('test', help='Run the unittest in the project',
                                       description='Run the unittest in the project')
        parser.add_argument('project', type=IconPath('d'), help='Project directory path')

    def run(self, args):
        if not hasattr(self, args.command):
            raise TBearsCommandException(f"Invalid command {args.command}")

        # load configurations
        conf = self.get_icon_conf(args.command, args=vars(args))

        Logger.info(f"Run '{args.command}' command with config: {conf}", TBEARS_CLI_TAG)

        # run command
        return getattr(self, args.command)(conf)

    def deploy(self, conf: dict) -> dict:
        """Deploy SCORE on the server.
        :param conf: deploy command configuration
        """
        # check keystore, and get password from user's terminal input
        password = conf.get('password', None)
        password = self._check_deploy(conf, password)

        if conf['mode'] == 'install':
            score_address = f'cx{"0"*40}'
        else:
            score_address = conf['to']

        if password:
            response = self.deploy_with_keystore(conf, password, score_address)
        else:
            response = self.deploy_without_keystore(conf, score_address)

        if 'error' in response:
            print('Got an error response')
            print(json.dumps(response, indent=4))
        else:
            print('Send deploy request successfully.')
            tx_hash = response['result']
            print(f'If you want to check SCORE deployed successfully, execute txresult command')
            print(f"transaction hash: {tx_hash}")

        return response

    def deploy_with_keystore(self, conf: dict, password: str, score_address: str) -> dict:

        uri, version = uri_parser(conf['uri'])
        icon_service = IconService(HTTPProvider(uri, version))
        wallet = KeyWallet.load(conf['keyStore'], password)

        # make zip and convert to hexadecimal string data (start with 0x) and return
        content = gen_deploy_data_content(conf['project'])

        deploy_transaction = DeployTransactionBuilder() \
            .from_(wallet.get_address()) \
            .to(score_address) \
            .nid(convert_hex_str_to_int(conf['nid']))\
            .content_type("application/zip") \
            .content(content) \
            .build()

        if 'stepLimit' not in conf:
            step_limit = icon_service.estimate_step(deploy_transaction)
        else:
            step_limit = convert_hex_str_to_int(conf['stepLimit'])

        deploy_transaction.step_limit = step_limit

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(deploy_transaction, wallet)

        # Sends transaction and return response
        send_transaction = tx_logger_deco(icon_service.send_transaction,
                                          conf['uri'],
                                          signed_transaction.signed_transaction_dict)
        return send_transaction(signed_transaction, True)

    def deploy_without_keystore(self, conf: dict, score_address: str) -> dict:

        # make zip and convert to hexadecimal string data (start with 0x) and return
        content = gen_deploy_data_content(conf['project'])
        content = f"0x{content.hex()}"

        # make IconJsonrpc instance which is used for making request (with signature)
        deploy = IconJsonrpc.from_string(from_=conf['from'])

        # make JSON-RPC 2.0 request standard format
        request = deploy.sendTransaction(to=score_address,
                                         nid=conf['nid'],
                                         step_limit=conf.get('stepLimit', None),
                                         data_type="deploy",
                                         data=IconJsonrpc.gen_deploy_data(
                                             params=conf.get('scoreParams', {}),
                                             content_type="application/zip",
                                             content=content))

        if 'stepLimit' not in conf:
            step_limit = get_enough_step(request, conf['uri'])
            request['params']['stepLimit'] = hex(step_limit)
            deploy.put_signature(request['params'])

        # send request to the rpc server
        icon_client = IconClient(conf['uri'])

        # return response
        return icon_client.send(request)

    @staticmethod
    def clear(_conf: dict):
        """Clear all SCORE deployed on tbears service

        :param _conf: clear command configuration
        """
        # referenced data's path is /tmp/.tbears.env (temporary config data)
        score_dir_info = CommandServer.get_server_conf()

        if score_dir_info is None:
            raise TBearsDeleteTreeException("Already clean.")

        if CommandServer.is_service_running():
            raise TBearsCommandException(f'You must stop tbears service to clear SCORE')

        # delete whole score data
        try:
            if os.path.exists(score_dir_info['scoreRootPath']):
                shutil.rmtree(score_dir_info['scoreRootPath'])
            if os.path.exists(score_dir_info['stateDbRootPath']):
                shutil.rmtree(score_dir_info['stateDbRootPath'])
            CommandServer._delete_server_conf()
        except (PermissionError, NotADirectoryError) as e:
            raise TBearsDeleteTreeException(f"Can't delete SCORE files. {e}")

        # delete temporary config data (path: /tmp/.tbears.env)
        CommandServer._delete_server_conf()

        print(f"Cleared SCORE deployed on tbears successfully")

    @staticmethod
    def test(conf: dict):
        loader = unittest.TestLoader()
        start_dir = conf['project']
        top_dir = os.path.abspath(os.path.join(start_dir, '..'))
        suite = loader.discover(start_dir, top_level_dir=top_dir)

        runner = unittest.TextTestRunner()
        runner.run(suite)

    @staticmethod
    def _check_deploy(conf: dict, password: str = None):
        """Check keystore presence, and get password from user's terminal input (not validate password)
        password is an optional parameter for unit tests purposes

        :param conf: command configuration
        :param password: password for unit tests (optional)
        :return: password for keystore file
        """
        # check if keystore exist. if exist, get password from user input
        if not conf['keyStore']:
            if not is_icon_address_valid(conf['from']):
                raise TBearsCommandException(f"You entered invalid 'from' address '{conf['from']}")
        else:
            if not password:
                password = getpass.getpass("Input your keystore password: ")

        # in case of update mode, validate -to option
        if conf['mode'] == 'update':
            if conf.get('to', None) is None:
                raise TBearsCommandException(f'If you want to update SCORE, set --to option')
            elif not is_icon_address_valid(conf['to']):
                raise TBearsCommandException(f"You entered invalid 'to' address '{conf['to']}")

        # check project directory
        check_project(conf.get('project', ""))

        return password

    def check_command(self, command):
        return hasattr(self, command)

    @staticmethod
    def get_icon_conf(command: str, project: str = None, args: dict = None):
        """Load config file using IconConfig instance
        config file is loaded as below priority
        system config -> default config -> user config -> user input config (higher priority)

        :param command: command name (e.g. deploy)
        :param project: project name (in case of deploy)
        :param args: user input command (converted to dictionary type)
        :return: command configuration
        """
        # load default configurations
        conf = IconConfig(FN_CLI_CONF, copy.deepcopy(tbears_cli_config))
        # move command config
        if command in conf:
            conf.update_conf(conf[command])
            del conf[command]

        if project is not None:
            conf['project'] = project

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

def check_project(project_path: str) -> int:
    if os.path.isdir(project_path):
        # there is no __init__.py
        if not os.path.exists(f"{project_path}/__init__.py"):
            raise TBearsCommandException(f'There is no __init__.py in project directory')

        # there is no package.json
        if not os.path.exists(f"{project_path}/package.json"):
            raise TBearsCommandException(f'There is no package.json in project directory')

        with open(f"{project_path}/package.json", mode='r') as file:
            try:
                package: dict = json.load(file)
            except Exception as e:
                raise TBearsCommandException(f'package.json has wrong format. {e}')

            # wrong package.json file
            if 'version' not in package or 'main_score' not in package:
                raise TBearsCommandException(f'package.json has wrong format.')

            # check the validity of main_module
            main_module: str = package.get('main_module')
            if not isinstance(main_module, str):
                try:
                    # this will be deprecated soon
                    main_module: str = package['main_file']
                except KeyError:
                    raise TBearsCommandException(f'package.json should have main_module field.')

            if main_module.startswith('.') or main_module.find('/') != -1:
                raise TBearsCommandException(f'Invalid main_module field: {main_module}')

            main_file = main_module.replace('.', '/') + '.py'
            if not os.path.exists(f"{project_path}/{main_file}"):
                raise TBearsCommandException(f"There is no '{project_path}/{main_file}'")

    return 0

