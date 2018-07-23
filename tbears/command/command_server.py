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
import sys
import subprocess
import time
from typing import Optional
from ipaddress import ip_address

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger
from tbears.tbears_exception import TBearsCommandException, TBearsWriteFileException
from tbears.util import post, make_exit_json_payload, write_file
from tbears.config.tbears_config import FN_SERVER_CONF, tbears_server_config


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
        parser.add_argument('-a', '--address', help='Address to host on (default: 0.0.0.0)', type=ip_address)
        parser.add_argument('-p', '--port', help='Port to host on (default: 9000)', type=int, dest='port')
        parser.add_argument('-c', '--config', help=f'tbears configuration file path (default: {FN_SERVER_CONF})')

    @staticmethod
    def _add_stop_parser(subparsers) -> None:
        subparsers.add_parser('stop', help='Stop tbears service',
                              description='Stop all running SCOREs and tbears service')

    def run(self, args):
        if not hasattr(self, args.command):
            raise TBearsCommandException(f"Invalid command {args.command}")

        # load configurations
        conf = IconConfig(FN_SERVER_CONF, tbears_server_config)
        conf.load(user_input=vars(args))

        # run command
        getattr(self, args.command)(conf)

    @staticmethod
    def start(conf: dict):
        """ Start tbears service

        :param conf: start command configuration
        """
        if CommandServer.is_server_running():
            raise TBearsCommandException(f"Tbears service was started already")

        # start jsonrpc_server for tbears
        CommandServer.__start_server(conf)

        # wait 2 sec
        time.sleep(2)

        print(f'Started tbear service successfully')

    @staticmethod
    def stop(_conf: dict):
        """ Stop tbears service
        :param _conf: stop command configuration
        """
        if CommandServer.is_server_running():
            CommandServer.__exit_request()
            # Wait until server socket is released
            time.sleep(2)

            # delete env file
            CommandServer.__delete_server_conf()

            print(f'Stopped tbear service successfully')
        else:
            print(f'tbear service is not running')

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
        server = CommandServer.__get_server_conf()
        if server is None:
            Logger.debug(f"Can't get server Info. from {TBEARS_CLI_ENV}", TBEARS_CLI_TAG)
            server = CommandServer.__get_server_conf(FN_SERVER_CONF)
            if not server:
                server = {'port': 9000}

        post(f"http://127.0.0.1:{server['port']}/api/v3", make_exit_json_payload())

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
    def write_server_conf(host: str, port: int) -> None:
        conf = {
            "hostAddress": host,
            "port": port
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
    def __get_server_conf(file_path: str= TBEARS_CLI_ENV) -> Optional[dict]:
        try:
            with open(f'{file_path}') as f:
                conf = json.load(f)
        except Exception as e:
            Logger.debug(f"Can't read server configuration({file_path}. {e}")
            return None

        Logger.debug(f"Get server info {conf}", TBEARS_CLI_TAG)
        return conf

    @staticmethod
    def __delete_server_conf() -> None:
        if os.path.exists(TBEARS_CLI_ENV):
            os.remove(TBEARS_CLI_ENV)
