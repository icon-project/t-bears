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
import os
import shutil
import getpass

from iconcommons.icon_config import IconConfig
from iconservice.base.address import is_icon_address_valid

from tbears.command.command_server import CommandServer
from tbears.config.tbears_config import FN_CLI_CONF, tbears_cli_config
from tbears.libs.icon_jsonrpc import IconJsonrpc, IconClient
from tbears.tbears_exception import TBearsDeleteTreeException, TBearsCommandException


class CommandScore(object):
    def __init__(self, subparsers):
        self._add_deploy_parser(subparsers)
        self._add_clear_parser(subparsers)

    @staticmethod
    def _add_deploy_parser(subparsers):
        parser = subparsers.add_parser('deploy', help='Deploy the SCORE', description='Deploy the SCORE')
        parser.add_argument('project', help='Project name')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                            dest='uri')
        parser.add_argument('-t', '--type', help='Deploy SCORE type (default: tbears)',
                            choices=['tbears', 'zip'], dest='contentType')
        parser.add_argument('-m', '--mode', help='Deploy mode (default: install)',
                            choices=['install', 'update'], dest='mode')
        parser.add_argument('-f', '--from', help='From address. i.e. SCORE owner address', dest='from')
        parser.add_argument('-o', '--to', help='To address. i.e. SCORE address', dest='to')
        parser.add_argument('-k', '--key-store', help='Keystore file path. Used to generate "from" address and '
                                                      'transaction signature', dest='keyStore')
        parser.add_argument('-n', '--nid', help='Network ID', dest='nid')
        parser.add_argument('-c', '--config', help=f'deploy config path (default: {FN_CLI_CONF})')

    @staticmethod
    def _add_clear_parser(subparsers):
        subparsers.add_parser('clear', help='Clear all SCOREs deployed on tbears service',
                              description='Clear all SCOREs deployed on local tbears service')

    def run(self, args):
        if not hasattr(self, args.command):
            raise TBearsCommandException(f"Invalid command {args.command}")

        # load configurations
        conf = self.get_score_conf(args.command, args=vars(args))

        # run command
        getattr(self, args.command)(conf)

    def deploy(self, conf: dict, password: str = None) -> dict:
        """Deploy SCORE on the server.

        :param conf: deploy command configuration
        :param password: password for keystore file
        """
        if conf['contentType'] == 'tbears' and not CommandServer.is_server_running():
            raise TBearsCommandException(f'Start tbears service first')

        password = self._check_deploy(conf, password)

        step_limit = int(conf.get('stepLimit', "0x1234000"), 16)

        if conf['mode'] == 'install':
            score_address = f'cx{"0"*40}'
        else:
            score_address = conf['to']

        if conf['contentType'] == 'zip':
            content_type = "application/zip"
            content = IconJsonrpc.gen_deploy_data_content(conf['project'])
        else:
            content_type = "application/tbears"
            content = os.path.abspath(conf['project'])

        if conf['keyStore']:
            deploy = IconJsonrpc.from_key_store(keystore=conf['keyStore'], password=password)
        else:
            deploy = IconJsonrpc.from_string(from_=conf['from'])

        # make JSON-RPC request
        request = deploy.sendTransaction(to=score_address,
                                         nid=int(conf['nid'], 16),
                                         step_limit=step_limit,
                                         data_type="deploy",
                                         data=IconJsonrpc.gen_deploy_data(
                                             params=conf.get('scoreParams', {}),
                                             content_type=content_type,
                                             content=content))

        icon_client = IconClient(conf['uri'])
        response = icon_client.send(request)

        if 'result' in response:
            print('Send deploy request successfully.')
            tx_hash = response['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Got an error response')
            print(response)

        return response

    @staticmethod
    def clear(_conf: dict):
        """Clear all SCORE deployed on tbears service

        :param _conf: clear command configuration
        """
        score_dir_info = CommandServer._get_server_conf()

        if CommandServer.is_server_running():
            raise TBearsCommandException(f'You must stop tbears service to clear SCORE')

        try:
            if os.path.exists(score_dir_info['scoreRootPath']):
                shutil.rmtree(score_dir_info['scoreRootPath'])
            if os.path.exists(score_dir_info['stateDbRootPath']):
                shutil.rmtree(score_dir_info['stateDbRootPath'])
        except (PermissionError, NotADirectoryError) as e:
            raise TBearsDeleteTreeException(f"Can't delete SCORE files. {e}")

        CommandServer._delete_server_conf()

        print(f"Cleared SCORE deployed on tbears successfully")

    @staticmethod
    def _check_deploy(conf: dict, password: str = None):
        if not os.path.isdir(conf['project']):
            raise TBearsCommandException(f'There is no project directory.({conf["project"]})')

        if conf['contentType'] == 'zip':
            if conf.get('keyStore', None) is None:
                raise TBearsCommandException(f'If you want to deploy SCORE to ICON node, set --key-store option or '
                                             f'write "keyStore" value in configuration file.')
            else:
                if not os.path.exists(conf['keyStore']):
                    raise TBearsCommandException(f'There is no keystore file {conf["keyStore"]}')
                if not password:
                    password = getpass.getpass("input your key store password: ")
        else:
            uri: str = conf.get('uri', "")
            if uri and uri.find('127.0.0.1') == -1:
                raise TBearsCommandException(f"TBears does not support deploying tbears SCORE to remote")

        if not conf['keyStore']:
            if not is_icon_address_valid(conf['from']):
                raise TBearsCommandException(f"You entered invalid 'from' address '{conf['from']}")

        if conf['mode'] == 'update':
            if conf.get('to', None) is None:
                raise TBearsCommandException(f'If you want to update SCORE, set --to option')
            elif not is_icon_address_valid(conf['to']):
                raise TBearsCommandException(f"You entered invalid 'to' address '{conf['to']}")

        return password

    def check_command(self, command):
        return hasattr(self, command)

    @staticmethod
    def get_score_conf(command: str, project: str = None, args: dict = None):
        conf = IconConfig(FN_CLI_CONF, tbears_cli_config)
        if args:
            conf.load(user_input=args)

        if project is not None:
            conf['project'] = project

        if command in conf:
            conf.update(conf[command])
            del conf[command]

        return conf
