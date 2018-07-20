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
from tbears.config.tbears_config import deploy_config
from tbears.util.icx_signer import key_from_key_store, IcxSigner
from tbears.libs.icon_client import IconClient
from tbears.libs.icon_json import get_icx_sendTransaction_deploy_payload
from tbears.util import make_install_json_payload, get_deploy_contents_by_path
from tbears.tbears_exception import TBearsDeleteTreeException, TBearsCommandException


class CommandScore(object):
    def __init__(self, subparsers):
        self._add_deploy_parser(subparsers)
        self._add_clear_parser(subparsers)

    @staticmethod
    def _add_deploy_parser(subparsers):
        parser = subparsers.add_parser('deploy', help='Deploy the SCORE',
                                       description='Deploy the SCORE in project')
        parser.add_argument('project', help='Project name')
        parser.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                            dest='uri')
        parser.add_argument('-t', '--type', help='Deploy SCORE type (default: tbears)',
                            choices=['tbears', 'icon'], dest='scoreType')
        parser.add_argument('-m', '--mode', help='Deploy mode (default: install)',
                            choices=['install', 'update'], dest='mode')
        parser.add_argument('-f', '--from', help='From address. i.e. SCORE owner address', dest='from')
        parser.add_argument('-o', '--to', help='To address. i.e. SCORE address', dest='to')
        parser.add_argument('-k', '--key-store', help='Key store file for SCORE owner', dest='keyStore')
        parser.add_argument('-n', '--nid', help='Network ID', dest='nid')
        parser.add_argument('-c', '--config', help='deploy config path (default: ./deploy.json)')

    @staticmethod
    def _add_clear_parser(subparsers):
        subparsers.add_parser('clear', help='Clear all SCORE deployed on tbears service',
                              description='Clear all SCORE deployed on local tbears service')

    def run(self, args):
        if not hasattr(self, args.command):
            raise TBearsCommandException(f"Invalid command {args.command}")

        # load configurations
        conf = IconConfig('./deploy.json', deploy_config)
        conf.load(user_input=vars(args))

        # run command
        getattr(self, args.command)(conf)

    def deploy(self, conf: dict, password: str = None) -> dict:
        """Deploy SCORE on the server.

        :param conf: deploy command configuration
        :param password: password for keystore file
        """
        if conf['scoreType'] == 'tbears' and not CommandServer.is_server_running():
            raise TBearsCommandException(f'Start tbears service first')

        password = self._check_deploy(conf, password)

        step_limit = int(conf.get('stepLimit', "0x1234000"), 16)
        if conf['mode'] == 'install':
            score_address = f'cx{"0"*40}'
        else:
            score_address = conf['to']
            is_icon_address_valid(score_address)

        if conf['scoreType'] == 'icon':
            signer = IcxSigner(key_from_key_store(conf['keyStore'], password))
            deploy_contents = get_deploy_contents_by_path(conf['project'])
            payload = get_icx_sendTransaction_deploy_payload(signer=signer,
                                                             contents=deploy_contents,
                                                             nid=conf['nid'],
                                                             to=score_address,
                                                             deploy_params=conf.get('scoreParams', {}),
                                                             step_limit=step_limit)
        else:
            if not is_icon_address_valid(conf['from']):
                raise TBearsCommandException(f'You entered invalid address')
            payload = make_install_json_payload(project=conf['project'],
                                                fr=conf['from'],
                                                to=score_address,
                                                nid=conf['nid'],
                                                data_params=conf.get('scoreParams', {}))

        icon_client = IconClient(conf['uri'])
        response = icon_client.send(payload)
        response_json = response.json()

        if 'result' in response_json:
            print('Send deploy request successfully.')
            tx_hash = response_json['result']
            print(f"transaction hash: {tx_hash}")
        else:
            print('Got an error response')
            print(response_json)

        # print(f"Deployed SCORE successfully")

        return response.json()

    @staticmethod
    def clear(_conf: dict):
        """Clear all SCORE deployed on tbears service

        :param _conf: deploy command configuration
        """
        if CommandServer.is_server_running():
            raise TBearsCommandException(f'You must stop tbears service to clear SCORE')

        try:
            if os.path.exists('./.score'):
                shutil.rmtree('./.score')
            if os.path.exists('./.statedb'):
                shutil.rmtree('./.statedb')
        except (PermissionError, NotADirectoryError) as e:
            raise TBearsDeleteTreeException(f"Can't delete SCORE fils. {e}")

        print(f"Cleared SCORE deployed on tbears successfully")

    @staticmethod
    def _check_deploy(conf: dict, password: str = None):
        if not os.path.isdir(conf['project']):
            raise TBearsCommandException(f'There is no project directory.({conf["project"]})')

        if conf['scoreType'] == 'icon':
            if conf.get('keyStore', None) is None:
                raise TBearsCommandException(f'If you want to deploy SCORE to ICON node, set --key-store option or '
                                             f'write "keyStore" value in configuration file.')
            else:
                if not os.path.exists(conf['keyStore']):
                    raise TBearsCommandException(f'There is no keystore file {conf["keyStore"]}')
                if not password:
                    password = getpass.getpass("input your key store password: ")

        if conf['mode'] == 'update' and conf.get('to', None) is None:
            raise TBearsCommandException(f'If you want to update SCORE, set --to option')

        if conf['scoreType'] == 'tbears':
            uri: str = conf.get('uri', "")
            if uri and uri.find('127.0.0.1') == -1 and uri.find('localhost') == -1:
                raise TBearsCommandException(f"TBears does not support deploying tbears SCORE to remote")

        return password

    def check_command(self, command):
        return hasattr(self, command)

    @staticmethod
    def get_deploy_conf(project: str):
        conf = IconConfig('./deploy.json', deploy_config)
        conf['project'] = project
        return conf
