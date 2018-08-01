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
import json
import os
import sys
import subprocess
import time
from typing import Optional
from ipaddress import ip_address

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger
from tbears.tbears_exception import TBearsCommandException, TBearsWriteFileException
from tbears.util import write_file
from tbears.util.argparse_type import port_type, IconPath
from tbears.config.tbears_config import FN_SERVER_CONF, tbears_server_config
from tbears.libs.icon_jsonrpc import IconClient


TBEARS_CLI_ENV = '/tmp/.tbears.env'
SERVER_MODULE_NAME = 'tbears.server.jsonrpc_server'
TBEARS_CLI_TAG = 'tbears_cli'


class CommandServer(object):
    def __init__(self, subparsers):
        self._add_start_parser(subparsers)
        self._add_stop_parser(subparsers)

    @staticmethod
    def _add_start_parser(subparsers) -> None:
        parser = subparsers.add_parser('start', help='Start tbears serivce',
                                       description='Start tbears service')
        parser.add_argument('-a', '--address', type=ip_address, help='Address to host on (default: 0.0.0.0)', dest='hostAddress')
        parser.add_argument('-p', '--port', type=port_type, help='Port to host on (default: 9000)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'tbears configuration file path (default: {FN_SERVER_CONF})')

    @staticmethod
    def _add_stop_parser(subparsers) -> None:
        subparsers.add_parser('stop', help='Stop tbears service',
                              description='Stop all running SCOREs and tbears service')

    def run(self, args):
        if not hasattr(self, args.command):
            raise TBearsCommandException(f"Invalid command {args.command}")

        # load configurations
        user_input = vars(args)
        conf = self.get_icon_conf(args.command, args=user_input)

        # run command
        return getattr(self, args.command)(conf)

    @staticmethod
    def get_icon_conf(command: str, args: dict = None) -> dict:
        """Load config file using IconConfig instance
        config file is loaded as below priority
        system config -> default config -> user config -> user input config(higher priority)

        :param command: command name (e.g. start)
        :param args: user input command (converted to dictionary type)
        :return: command configuration
        """
        # load configurations
        conf = IconConfig(FN_SERVER_CONF, tbears_server_config)

        conf.load(config_path=args.get('config', None) if args else None)

        # move command config
        if command in conf:
            conf.update_conf(conf[command])
            del conf[command]

        # load user argument
        if args:
            conf.update_conf(args)

        return conf

    def start(self, conf: dict):
        """ Start tbears service

        :param conf: start command configuration
        """
        if self.is_server_running():
            raise TBearsCommandException(f"tbears service was started already")

        # start jsonrpc_server for tbears
        self.__start_server(conf)

        # wait 2 sec
        time.sleep(2)

        print(f'Started tbears service successfully')

    def stop(self, _conf: dict):
        """ Stop tbears service
        :param _conf: stop command configuration
        """
        if self.is_server_running():
            self.__exit_request()
            # Wait until server socket is released
            time.sleep(2)

            print(f'Stopped tbears service successfully')
        else:
            print(f'tbears service is not running')

    def check_command(self, command):
        return hasattr(self, command)

    @staticmethod
    def __start_server(conf: dict):
        Logger.debug('start_server() start', TBEARS_CLI_TAG)

        # make params
        params = {'-a': str(conf.get('hostAddress', None)),
                  '-p': str(conf.get('port', None)),
                  '-c': conf.get('config', None)}

        custom_argv = []
        for k, v in params.items():
            if v:
                custom_argv.append(k)
                custom_argv.append(v)

        # Run jsonrpc_server on background mode
        subprocess.Popen([sys.executable, '-m', SERVER_MODULE_NAME, *custom_argv], close_fds=True)

        Logger.debug('start_server() end', TBEARS_CLI_TAG)

    @staticmethod
    def __exit_request():
        """ Request for exiting SCORE on server.
        """
        # get server config data from /tmp/.tbears.env
        server = CommandServer._get_server_conf()
        if server is None:
            Logger.debug(f"Can't get server Info. from {TBEARS_CLI_ENV}", TBEARS_CLI_TAG)
            server = CommandServer._get_server_conf(FN_SERVER_CONF)
            if not server:
                server = {'port': 9000}

        server_exit = IconClient(uri=f"http://127.0.0.1:{server['port']}/api/v3")
        request = {"jsonrpc": "2.0", "method": "server_exit", "id": 99999}
        server_exit.send(request=request)

    @staticmethod
    def is_server_running(name: str = SERVER_MODULE_NAME) -> bool:
        """ Check if server is running.
        :return: True or False
        """
        # Return a list of processes matching 'name'.
        command = f"ps -ef | grep {name} | grep -v grep"
        result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
        if result.returncode == 1:
            return False
        return True

    @staticmethod
    def write_server_conf(host: str, port: int, score_root, score_db_root) -> None:
        conf = {
            "hostAddress": host,
            "port": port,
            "scoreRootPath": os.path.abspath(score_root),
            "stateDbRootPath": os.path.abspath(score_db_root)
        }
        Logger.debug(f"Write server Info.({conf}) to {TBEARS_CLI_ENV}", TBEARS_CLI_TAG)
        file_path = TBEARS_CLI_ENV
        file_name = file_path[file_path.rfind('/') + 1:]
        parent_directory = file_path[:file_path.rfind('/')]
        try:
            write_file(parent_directory=parent_directory, file_name=file_name, contents=json.dumps(conf),
                       overwrite=True)
        except Exception as e:
            print(f"Can't write conf to file. {e}")
        except TBearsWriteFileException as e:
            print(f"{e}")

    @staticmethod
    def _get_server_conf(file_path: str= TBEARS_CLI_ENV) -> Optional[dict]:
        try:
            with open(f'{file_path}') as f:
                conf = json.load(f)
        except Exception as e:
            Logger.debug(f"Can't read server configuration({file_path}. {e}")
            return None

        Logger.debug(f"Get server info {conf}", TBEARS_CLI_TAG)
        return conf

    @staticmethod
    def _delete_server_conf() -> None:
        if os.path.exists(TBEARS_CLI_ENV):
            os.remove(TBEARS_CLI_ENV)
