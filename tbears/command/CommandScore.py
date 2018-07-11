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
import json
import os
import shutil
from typing import Optional

from tbears.command import Command, ExitCode
from tbears.default_conf import tbears_conf
from tbears.util.icx_signer import key_from_key_store, IcxSigner
from tbears.util.libs.icon_client import IconClient
from tbears.util.libs.icon_json import get_icx_sendTransaction_deploy_payload
from tbears.util import make_install_json_payload
from tbears.tbears_exception import (
    TBearsDeleteTreeException, KeyStoreException, FillDeployPaylodException, IconClientException,
)


class CommandScore(Command):
    @staticmethod
    def deploy(project: str, conf: dict, password: str = None) -> object:
        """Deploy SCORE on the server.

        :param project: Project which you want to deploy.
        :param conf: deploy configuration
        :param password: password of keystore file.
        :return:
        """
        try:
            step_limit = int(conf.get('stepLimit', "0x12345"), 16)
            if conf['mode'] == 'install':
                score_address = f'cx{"0"*40}'
            else:
                score_address = conf['to']

            if conf['scoreType'] == 'icon':
                if password is None:
                    raise FillDeployPaylodException
                signer = IcxSigner(key_from_key_store(conf['keyStore'], password))
                payload = get_icx_sendTransaction_deploy_payload(signer=signer,
                                                                 path=project,
                                                                 to=score_address,
                                                                 deploy_params=conf.get('scoreParams', {}),
                                                                 step_limit=step_limit)
            else:
                payload = make_install_json_payload(project=project, fr=conf['from'], to=score_address,
                                                    deploy_params=conf.get('scoreParams', {}))

            icon_client = IconClient(conf['uri'])
            response = icon_client.send(payload)

        except KeyError:
            print(f"Can't get value from conf")
            return ExitCode.CONFIG_FILE_ERROR, None
        except KeyStoreException:
            print(f"Can't get key from keystore")
            return ExitCode.KEY_STORE_ERROR, None
        except FillDeployPaylodException:
            print(f"Can't get deploy payload")
            return ExitCode.DEPLOY_ERROR, None
        except IconClientException as e:
            print(f"ICON client error {e}")
            return ExitCode.ICON_CLIENT_ERROR, None
        else:
            return ExitCode.SUCCEEDED, response

    @staticmethod
    def clear() -> int:
        """Clear all SCORE deployed on tbears service

        :return: ExitCode
        """
        try:
            CommandScore.__delete_score_info()
        except TBearsDeleteTreeException:
            return ExitCode.DELETE_TREE_ERROR

        return ExitCode.SUCCEEDED

    @staticmethod
    def __delete_score_info():
        """ Delete .score directory and db directory.

        :return:
        """
        try:
            if os.path.exists('./.score'):
                shutil.rmtree('./.score')
            if os.path.exists('./.db'):
                shutil.rmtree('./.db')
        except PermissionError:
            raise TBearsDeleteTreeException
        except NotADirectoryError:
            raise TBearsDeleteTreeException

    @staticmethod
    def get_conf(file_path: str = None) -> Optional[dict]:
        try:
            with open(f'{file_path}') as f:
                conf = json.load(f)
        except:
            conf = tbears_conf.deploy_config

        return conf.get('deploy', None)
