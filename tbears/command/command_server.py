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
import logging
import socket
from typing import Optional

from iconservice.logger import Logger as logging
from tbears.command import Command, ExitCode
from tbears.tbears_exception import TBearsWriteFileException
from tbears.util import (
    post, make_exit_json_payload, get_init_template, get_tbears_config_json, get_deploy_config_json,
    write_file, get_package_json_dict, get_score_main_template, get_sample_crowd_sale_contents,
    get_sample_token_contents)


TBEARS_CLI_TAG = 'tbears_cli'
TBEARS_CLI_ENV = '/tmp/.tbears.env'


class CommandServer(Command):
    @staticmethod
    def init(project: str, score_class: str) -> 'ExitCode':
        """Initialize the tbears service.

        :param project: name of tbears project.
        :param score_class: class name of SCORE.
        :return: ExitCode, Succeeded
        """
        return CommandServer.__initialize_project(project=project, score_class=score_class,
                                                  contents_func=get_score_main_template)

    @staticmethod
    def start(host: str = None, port: int = None, conf_file: str = None) -> None:
        """ Start tbears service

        :param host: address to host on
        :param port: listen port
        :param conf_file: configuration file path
        """
        # start jsonrpc_server for tbears
        CommandServer.__start_server(host=host, port=port, tbears_config_path=conf_file)

        # wait 2 sec
        time.sleep(2)

    @staticmethod
    def stop() -> 'ExitCode':
        """
        Stop tbears service
        :return: ExitCode, Succeeded
        """

        server = CommandServer.is_server_running()
        if server:
            CommandServer.__exit_request(server=server)
            # Wait until server socket is released
            time.sleep(2)
        else:
            print(f"Can't get tbear service Info.")
            return ExitCode.SERVER_INFO_ERROR

        # delete env file
        CommandServer.delete_server_conf()

        return ExitCode.SUCCEEDED

    @staticmethod
    def make_samples() -> 'ExitCode':
        ret = CommandServer.__initialize_project(project="standard_token", score_class="StandardToken",
                                                 contents_func=get_sample_token_contents)
        if ret is not ExitCode.SUCCEEDED:
            return ret

        return CommandServer.__initialize_project(project="standard_crowd_sale", score_class="StandardCrowdSale",
                                                  contents_func=get_sample_crowd_sale_contents)

    @staticmethod
    def test(project: str) -> int:
        if os.path.isdir(project) is False:
            print(f'check score path.')
            return ExitCode.SCORE_PATH_IS_NOT_A_DIRECTORY
        os.chdir(project)
        subprocess.Popen([sys.executable, '-m', 'unittest'])
        time.sleep(1)

        return ExitCode.SUCCEEDED

    @staticmethod
    def __initialize_project(project: str, score_class: str, contents_func) -> 'ExitCode':
        """Initialize the tbears project

        :param project: name of tbears project.
        :param score_class: class name of SCORE.
        :param source code contents
        :return: ExitCode, Succeeded
        """
        if project == score_class:
            print(f'<project> and <score_class> must be different.')
            return ExitCode.PROJECT_AND_CLASS_NAME_EQUAL
        if os.path.exists(f"./{project}"):
            logging.debug(f'{project} directory is not empty.', TBEARS_CLI_TAG)
            print(f'{project} directory is not empty.')
            return ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY

        package_json_dict = get_package_json_dict(project, score_class)
        package_json_contents = json.dumps(package_json_dict, indent=4)
        py_contents = contents_func(score_class)
        init_contents = get_init_template(project, score_class)

        try:
            write_file(project, f"{project}.py", py_contents)
            write_file(project, "package.json", package_json_contents)
            write_file(project, '__init__.py', init_contents)
            write_file(f'{project}/tests', f'test_{project}.py', '')
            write_file(f'{project}/tests', f'__init__.py', '')
            write_file('./', "tbears.json", get_tbears_config_json())
            write_file('./', "deploy.json", get_deploy_config_json())
        except TBearsWriteFileException:
            logging.debug("Except raised while writing files.", TBEARS_CLI_TAG)
            return ExitCode.WRITE_FILE_ERROR

        return ExitCode.SUCCEEDED

    @staticmethod
    def __start_server(host: str, port: int, tbears_config_path: str = './tbears.json'):
        logging.debug('start_server() start', TBEARS_CLI_TAG)

        root_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../'))

        root_path_directory_name = root_path[root_path.rfind('/') + 1:]
        python_module_string = f'{root_path_directory_name}.server.jsonrpc_server'

        # make params
        params = {'-a': host if port else None,
                  '-p': str(port) if port else None,
                  '-c': tbears_config_path}

        custom_argv = []
        for k, v in params.items():
            if v:
                custom_argv.append(k)
                custom_argv.append(v)

        # Run jsonrpc_server on background mode
        subprocess.Popen([sys.executable, '-m', python_module_string, *custom_argv], close_fds=True)

        logging.debug('start_server() end', TBEARS_CLI_TAG)

    @staticmethod
    def __exit_request(server: dict):
        """ Request for exiting SCORE on server.
        """
        project_dict = make_exit_json_payload()
        uri = f"http://127.0.0.1:{server['port']}/api/v3"
        post(uri, project_dict)

    @staticmethod
    def is_server_running() -> Optional[dict]:
        """ Check if server is running.
        tbears use 9000 port.
        :return: if server is running, return server Info. dict
        """
        server = CommandServer.get_server_conf()
        if server is None:
            logging.debug(f"Can't get server Info. from {TBEARS_CLI_ENV}", TBEARS_CLI_TAG)
            server = CommandServer.get_server_conf('./tbears.json')
            if server is None:
                server = {"port": 9000}

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', server.get('port', 9000)))
        sock.close()

        if result:
            logging.debug("socket is closed!", TBEARS_CLI_TAG)
            return None
        else:
            logging.debug("socket is opened!", TBEARS_CLI_TAG)
            return server

    @staticmethod
    def write_server_conf(host: str, port: int) -> None:
        conf = {
            "hostAddress": host,
            "port": port
        }
        logging.debug(f"Write server Info.({conf}) to {TBEARS_CLI_ENV}", TBEARS_CLI_TAG)
        CommandServer.write_conf(file_path=TBEARS_CLI_ENV, conf=conf)

    @staticmethod
    def get_server_conf(file_path: str= TBEARS_CLI_ENV) -> Optional[dict]:
        conf = Command.get_conf(file_path=file_path)
        if conf is None:
            logging.debug(f"Can't get server info", TBEARS_CLI_TAG)
            return None

        logging.debug(f"Get server info {conf}", TBEARS_CLI_TAG)
        return conf

    @staticmethod
    def delete_server_conf() -> None:
        if os.path.exists(TBEARS_CLI_ENV):
            os.remove(TBEARS_CLI_ENV)
