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
import json
import os
import socket
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
from tbears.config.tbears_config import FN_SERVER_CONF, tbears_server_config, ConfigKey
from tbears.block_manager.block_manager import TBEARS_BLOCK_MANAGER


BLOCKMANAGER_MODULE_NAME = 'tbears.block_manager'
TBEARS_CLI_ENV = '/tmp/.tbears.env'
TBEARS_CLI_TAG = 'tbears_cli'


class CommandServer(object):
    def __init__(self, subparsers):
        self._add_start_parser(subparsers)
        self._add_stop_parser(subparsers)

    @staticmethod
    def _add_start_parser(subparsers) -> None:
        parser = subparsers.add_parser('start', help='Start tbears service',
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
        system config -> default config -> user config -> user input config (higher priority)

        :param command: command name (e.g. start)
        :param args: user input command (converted to dictionary type)
        :return: command configuration
        """
        # load configurations
        conf = IconConfig(FN_SERVER_CONF, copy.deepcopy(tbears_server_config))
        # load config file
        conf.load(config_path=args.get('config', None) if args else None)

        # move command config
        if command in conf:
            conf.update_conf(conf[command])
            del conf[command]

        # load user argument
        if args:
            conf.update_conf(args)

        # add default configuration file
        if args.get('config', None) is None:
            if os.path.exists(FN_SERVER_CONF):
                conf['config'] = FN_SERVER_CONF

        return conf

    def start(self, conf: dict):
        """ Start tbears service
        Start iconservice, tbears_block_manager, iconrpcserver

        :param conf: start command configuration
        """
        if self.is_service_running():
            raise TBearsCommandException(f"tbears service was started already")

        if self.is_port_available(conf) is False:
            raise TBearsCommandException(f"port {conf['port']} already in use. use other port.")

        # write temporary configuration file
        temp_conf = './temp_conf.json'
        with open(temp_conf, mode='w') as file:
            file.write(json.dumps(conf))

        # run iconservice
        self._start_iconservice(conf, temp_conf)

        # start tbears_block_manager
        self._start_blockmanager(conf)

        # start iconrpcserver
        self._start_iconrpcserver(conf, temp_conf)
        time.sleep(3)

        # remove temporary configuration file
        os.remove(temp_conf)

        # write server configuration
        self.write_server_conf(conf)

        print(f'Started tbears service successfully')

    def stop(self, _conf: dict):
        """ Stop tbears service
        Start iconservice, tbears_block_manager, iconrpcserver

        :param _conf: stop command configuration
        """
        if not self.is_service_running():
            print(f'tbears service is not running')
            return

        with open(os.devnull, 'w') as devnull:
            # stop iconrpcserver
            subprocess.run('iconrpcserver stop', shell=True, stdout=devnull)

            # stop tbears_block_manager
            subprocess.run(f'pkill -f tbears_block_manager', shell=True)

            # stop iconservice
            subprocess.run(f'iconservice stop -c {TBEARS_CLI_ENV}', shell=True, stdout=devnull)

            time.sleep(2)

        print(f'Stopped tbears service successfully')

    def check_command(self, command):
        return hasattr(self, command)

    @staticmethod
    def _start_iconservice(conf: dict, config_path: str):
        cmd = f"iconservice start -c {config_path}"

        with open(os.devnull, 'w') as devnull:
            subprocess.run(cmd, shell=True, stdout=devnull)

    @staticmethod
    def _start_iconrpcserver(conf: dict, config_path: str):
        cmd = f"iconrpcserver start -tbears -c {config_path}"

        with open(os.devnull, 'w') as devnull:
            subprocess.run(cmd, shell=True, stdout=devnull)

    @staticmethod
    def _start_blockmanager(conf: dict):
        # make params
        params = {'-ch': conf.get(ConfigKey.CHANNEL, None),
                  '-at': conf.get(ConfigKey.AMQP_TARGET, None),
                  '-ak': conf.get(ConfigKey.AMQP_KEY, None),
                  '-c': conf.get('config', None)
                  }

        custom_argv = []
        for k, v in params.items():
            if v:
                custom_argv.append(k)
                custom_argv.append(v)

        # Run block_manager background mode
        subprocess.Popen([sys.executable, '-m', BLOCKMANAGER_MODULE_NAME, *custom_argv], close_fds=True)

    @staticmethod
    def is_service_running(name: str = TBEARS_BLOCK_MANAGER) -> bool:
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
    def is_port_available(conf):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if socket is connected, the result code is 0 (false).
        result = sock.connect_ex(('127.0.0.1', conf['port']))
        sock.close()
        return result != 0

    @staticmethod
    def write_server_conf(conf: dict):
        write_conf = {
            "hostAddress": conf['hostAddress'],
            "port": conf['port'],
            "scoreRootPath": conf['scoreRootPath'],
            "stateDbRootPath": conf['stateDbRootPath'],
            ConfigKey.CHANNEL: conf.get(ConfigKey.CHANNEL, None),           # to stop iconservice
            ConfigKey.AMQP_TARGET: conf.get(ConfigKey.AMQP_TARGET, None),   # to stop iconservice
            ConfigKey.AMQP_KEY: conf.get(ConfigKey.AMQP_KEY, None)          # to stop iconservice
        }
        Logger.debug(f"Write server Info.({conf}) to {TBEARS_CLI_ENV}", TBEARS_CLI_TAG)
        file_path = TBEARS_CLI_ENV
        file_name = file_path[file_path.rfind('/') + 1:]
        parent_directory = file_path[:file_path.rfind('/')]
        try:
            write_file(parent_directory=parent_directory, file_name=file_name, contents=json.dumps(write_conf),
                       overwrite=True)
        except Exception as e:
            print(f"Can't write conf to file. {e}")
        except TBearsWriteFileException as e:
            print(f"{e}")

    @staticmethod
    def get_server_conf(file_path: str= TBEARS_CLI_ENV) -> Optional[dict]:
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
