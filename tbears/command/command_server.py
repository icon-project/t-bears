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
import subprocess
import sys
import time
from ipaddress import ip_address
from typing import Optional

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger

from tbears.block_manager.block_manager import TBEARS_BLOCK_MANAGER
from tbears.config.tbears_config import FN_SERVER_CONF, tbears_server_config, TConfigKey, TBEARS_CLI_TAG
from tbears.tbears_exception import TBearsCommandException, TBearsWriteFileException
from tbears.tools.mainnet.sync import Sync
from tbears.util import write_file
from tbears.util.argparse_type import port_type, IconPath

BLOCKMANAGER_MODULE_NAME = 'tbears.block_manager'
TBEARS_CLI_ENV = '/tmp/.tbears.env'


class CommandServer(object):
    def __init__(self, subparsers):
        self._add_start_parser(subparsers)
        self._add_stop_parser(subparsers)
        self._add_sync_mainnet_parser(subparsers)

    @staticmethod
    def _add_start_parser(subparsers) -> None:
        parser = subparsers.add_parser('start', help='Start tbears service',
                                       description='Start tbears service')
        parser.add_argument('-a', '--address', type=ip_address, help='Address to host on (default: 127.0.0.1)', dest='hostAddress')
        parser.add_argument('-p', '--port', type=port_type, help='Port to listen on (default: 9000)')
        parser.add_argument('-c', '--config', type=IconPath(),
                            help=f'tbears configuration file path (default: {FN_SERVER_CONF})')

    @staticmethod
    def _add_stop_parser(subparsers) -> None:
        subparsers.add_parser('stop', help='Stop tbears service',
                              description='Stop all running SCOREs and tbears service')

    @staticmethod
    def _add_sync_mainnet_parser(subparsers) -> None:
        parser = subparsers.add_parser('sync_mainnet', help='Synchronize revision and governance SCORE with the mainnet',
                                       description='Synchronize revision and governance SCORE with the mainnet')

    def run(self, args):
        if not hasattr(self, args.command):
            raise TBearsCommandException(f"Invalid command {args.command}")

        # load configurations
        user_input = vars(args)
        conf = self.get_icon_conf(args.command, args=user_input)

        Logger.info(f"Run '{args.command}' command with config: {conf}", TBEARS_CLI_TAG)

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

        if self._check_revision() < 0:
            print(f"WARNING: Too low revision. To sync with the mainnet, run sync_mainnet command.")

        print(f'Started tbears service successfully')

    def stop(self, _conf: dict):
        """ Stop tbears service
        Start iconservice, tbears_block_manager, iconrpcserver

        :param _conf: stop command configuration
        """
        if not self.is_service_running():
            print(f'tbears service is not running')
            return

        # stop iconrpcserver
        subprocess.run(['iconrpcserver', 'stop'], stdout=subprocess.DEVNULL)

        # stop tbears_block_manager
        subprocess.run(['pkill', '-f', TBEARS_BLOCK_MANAGER], stdout=subprocess.DEVNULL)

        # stop iconservice
        subprocess.run(['iconservice', 'stop', '-c', f'{TBEARS_CLI_ENV}'], stdout=subprocess.DEVNULL)

        time.sleep(2)

        print(f'Stopped tbears service successfully')

    def sync_mainnet(self, _conf: dict):
        """ Sync revision and governance SCORE with the mainnet

        :param conf:
        :return: None
        """
        if self.get_server_conf() is not None or self.is_service_running():
            raise TBearsCommandException(f'You must stop T-Bears service and clear SCORE to run sync_mainnet command')

        # copy mainnet DB
        dir_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(dir_path, f"../data/mainnet.tar.gz")
        subprocess.run(['tar', 'xzvf', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f'Synchronized successfully revision and governance SCORE with the mainnet')

    def check_command(self, command):
        return hasattr(self, command)

    @staticmethod
    def _start_iconservice(conf: dict, config_path: str):
        subprocess.run(['iconservice', 'start', '-c', f'{config_path}'], stdout=subprocess.DEVNULL)

    @staticmethod
    def _start_iconrpcserver(conf: dict, config_path: str):
        subprocess.run(['iconrpcserver', 'start', '-tbears', '-c', f'{config_path}'], stdout=subprocess.DEVNULL)

    @staticmethod
    def _start_blockmanager(conf: dict):
        # make params
        params = {'-ch': conf.get(TConfigKey.CHANNEL, None),
                  '-at': conf.get(TConfigKey.AMQP_TARGET, None),
                  '-ak': conf.get(TConfigKey.AMQP_KEY, None),
                  '-c': conf.get('config', None)}

        custom_argv = []
        for k, v in params.items():
            if v:
                custom_argv.append(k)
                custom_argv.append(v)

        # Run block_manager in background mode
        subprocess.Popen([sys.executable, '-m', BLOCKMANAGER_MODULE_NAME, *custom_argv], close_fds=True)

    @staticmethod
    def is_service_running(name: str = TBEARS_BLOCK_MANAGER) -> bool:
        """ Check if server is running.
        :return: True or False
        """
        cmdlines = CommandServer._get_process_command_list(name.encode('utf-8'))
        if cmdlines:
            return True
        return False

    @staticmethod
    def _get_process_command_list(prefix: bytes) -> list:
        if os.path.exists('/proc'):
            cmd_lines = []
            pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
            for pid in pids:
                try:
                    cmdpath = os.path.join('/proc', pid, 'cmdline')
                    with open(cmdpath, 'rb') as fd:
                        cmdline = fd.read().rstrip(b'\x00')
                        if cmdline.startswith(prefix):
                            cmd_lines.append(cmdline.decode())
                except IOError:
                    continue
        else:
            result = subprocess.run(['ps', '-eo', 'command'], stdout=subprocess.PIPE)
            cmd_lines = [cmdline.decode().rstrip()
                         for cmdline in result.stdout.split(b'\n')
                         if cmdline.startswith(prefix)]
        return cmd_lines

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
            TConfigKey.CHANNEL: conf.get(TConfigKey.CHANNEL, None),           # to stop iconservice
            TConfigKey.AMQP_TARGET: conf.get(TConfigKey.AMQP_TARGET, None),   # to stop iconservice
            TConfigKey.AMQP_KEY: conf.get(TConfigKey.AMQP_KEY, None)          # to stop iconservice
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
    def get_server_conf(file_path: str = TBEARS_CLI_ENV) -> Optional[dict]:
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

    @staticmethod
    def _check_revision() -> int:
        sync = Sync()
        return sync.check_revision()
