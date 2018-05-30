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
from enum import IntEnum

from ..tbears_exception import TBearsWriteFileException, TBearsDeleteTreeException
from ..util import post, make_install_json_payload, make_exit_json_payload, \
    delete_score_info, get_init_template, get_sample_crowd_sale_contents
from ..util import write_file, get_package_json_dict, get_score_main_template

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class ExitCode(IntEnum):
    SUCCEEDED = 1
    COMMAND_IS_WRONG = 0
    SCORE_PATH_IS_NOT_A_DIRECTORY = 2
    PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY = 3
    WRITE_FILE_ERROR = 4
    DELETE_TREE_ERROR = 5
    SCORE_AlREADY_EXISTS = 6


def init_SCORE(project: str, score_class: str) -> int:
    """Initialize the SCORE.

    :param project: name of SCORE.
    :param score_class: class name of SCORE.
    :return: ExitCode, Succeeded
    """
    if os.path.exists(f"./{project}"):
        logging.debug(f'{project} directory is not empty.')
        return ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value

    package_json_dict = get_package_json_dict(project, score_class)
    package_json_contents = json.dumps(package_json_dict, indent=4)
    project_py_contents = get_score_main_template(score_class)
    init_contents = get_init_template(project, score_class)

    try:
        write_file(project, f"{project}.py", project_py_contents)
        write_file(project, "package.json", package_json_contents)
        write_file(project, '__init__.py', init_contents)
    except TBearsWriteFileException:
        logging.debug("Except raised while writing files.")
        return ExitCode.WRITE_FILE_ERROR.value

    return ExitCode.SUCCEEDED


def run_SCORE(project: str) -> tuple:
    """Run SCORE, embedding SCORE on the server.

    :param project: name of SCORE.
    :return: ExitCode, Succeeded
    """

    if not __is_server_running():
        __start_server()
        time.sleep(2)

    respond = __embed_SCORE_on_server(project)

    return ExitCode.SUCCEEDED, respond


def stop_SCORE() -> int:
    """
    Stop score process.
    :return: ExitCode, Succeeded
    """
    while __is_server_running():
        __exit_request()
        # Wait until server socket is released
        time.sleep(2)

    return ExitCode.SUCCEEDED


def clear_SCORE() -> int:
    """ Clear score directories (.db, .score)

    :return: ExitCode
    """
    stop_SCORE()

    try:
        delete_score_info()
    except TBearsDeleteTreeException:
        return ExitCode.DELETE_TREE_ERROR

    return ExitCode.SUCCEEDED


def make_SCORE_samples():

    tokentest_package_json_dict = get_package_json_dict("tokentest", "Tokentest")
    tokentest_package_json_contents = json.dumps(tokentest_package_json_dict, indent=4)
    tokentest_py_contents = get_score_main_template("Tokentest")
    tokentest_init_contents = get_init_template("tokentest", "Tokentest")

    crowdsale_package_json_dict = get_package_json_dict("sampleCrowdSale", "SampleCrowdSale")
    crowdsale_package_json_contents = json.dumps(crowdsale_package_json_dict, indent=4)
    crowdsale_py_contents = get_sample_crowd_sale_contents()
    crowdsale_init_contents = get_init_template("sampleCrowdSale", "SampleCrowdSale")
    try:
        write_file('./tokentest', 'tokentest.py', tokentest_py_contents)
        write_file('./tokentest', "package.json", tokentest_package_json_contents)
        write_file('./tokentest', '__init__.py', tokentest_init_contents)

        write_file('./sampleCrowdSale', "package.json", crowdsale_package_json_contents)
        write_file('./sampleCrowdSale', '__init__.py', crowdsale_init_contents)
        write_file('./sampleCrowdSale', "sampleCrowdSale.py", crowdsale_py_contents)

    except TBearsWriteFileException:
        logging.debug("Except raised while writing files.")
        return ExitCode.WRITE_FILE_ERROR.value

    return ExitCode.SUCCEEDED


def __start_server():
    logging.debug('start_server() start')

    root_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../'))

    path = os.path.join(root_path, 'server', 'jsonrpc_server.py')

    logging.info(f'path: {path}')

    # Run jsonrpc_server on background mode
    subprocess.Popen([sys.executable, path], close_fds=True)

    logging.debug('start_server() end')


def __embed_SCORE_on_server(project: str) -> dict:
    """ Request for embedding SCORE on server.
    :param project: Project directory name.
    """
    url = "http://localhost:9000/api/v3"
    project_dict = make_install_json_payload(project)
    response = post(url, project_dict)
    return response


def __exit_request():
    """ Request for exiting SCORE on server.
    """
    url = "http://localhost:9000/api/v3"
    project_dict = make_exit_json_payload()
    post(url, project_dict)


def __is_server_running():
    """ Check if server is running.
    tbears use 9000 port.
    :return: True means socket is opened.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 9000))
    sock.close()

    if result:
        logging.debug("socket is closed!")
    else:
        logging.debug("socket is opened!")

    return result is 0

