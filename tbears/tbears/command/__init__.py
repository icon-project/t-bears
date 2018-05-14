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
import shutil
import subprocess
import time
import zipfile
import logging
from enum import IntEnum

from ..tbears_exception import TBearsWriteFileException
from ..util import post, make_install_json_payload, make_exit_json_payload
from ..util import write_file, get_package_json_dict, get_score_main_template


class ExitCode(IntEnum):
    SUCCEEDED = 1
    COMMAND_IS_WRONG = 0
    SCORE_PATH_IS_NOT_A_DIRECTORY = 2
    PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY = 3
    WRITE_FILE_ERROR = 4


def init(project: str, score_class: str) -> int:
    """ Initialize SCORE project.

    :param project: your score name.
    :param score_class: Your score class name.
    :return:
    """
    print("init called")
    if os.path.exists(f"./{project}"):
        print(f'{project} directory is not empty.')
        return ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value
    package_json_dict = get_package_json_dict(project, score_class)
    package_json_contents = json.dumps(package_json_dict, indent=4)
    project_py_contents = get_score_main_template(score_class)
    try:
        write_file(project, f"{project}.py", project_py_contents)
        write_file(project, "package.json", package_json_contents)
    except TBearsWriteFileException:
        print("Except raised while writing files.")
        return ExitCode.WRITE_FILE_ERROR.value

    return ExitCode.SUCCEEDED


def run(project: str) -> int:
    """ Run score.

    :param project: score name.
    :return:
    """
    stop()

    start_server()
    time.sleep(2)
    install_request(project)

    return ExitCode.SUCCEEDED


def start_server() -> None:
    logging.debug('start_server() start')

    tbears_root_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../'))
    path = os.path.join(tbears_root_path, 'server', 'jsonrpc_server.py')

    logging.info(f'path: {path}')
    # Run jsonrpc_server on background mode
    subprocess.Popen([sys.executable, path], close_fds=True)

    logging.debug('start_server() end')


def install_request(project: str):
    """ Request install score.
    :param project: Project directory name.
    """
    url = "http://localhost:9000/api/v2"
    project_dict = make_install_json_payload(project)
    post(url, project_dict)


def stop() -> int:
    """ Stop score process.

    :return:
    """
    stop_server()
    delete_score_info()
    return ExitCode.SUCCEEDED


def stop_server():
    exit_request()
    # Wait until server socket is released
    time.sleep(2)


def exit_request():
    """ Request install score.
    :param project: Project directory name.
    """
    url = "http://localhost:9000/api/v2"
    project_dict = make_exit_json_payload()
    try:
        post(url, project_dict)
    except:
        pass


def compress(project: str, score_path: str) -> int:
    """ Compress the SCORE.

    :param project: project name. will archive <project>.zip
    :param score_path: SCORE path(directory).
    :return:
    """
    if not os.path.isdir(score_path):
        return ExitCode.SCORE_PATH_IS_NOT_A_DIRECTORY.value
    for current_dir, _, files in os.walk(score_path):
        for file in files:
            if current_dir.find('__pycache__') != -1:
                continue
            if os.path.islink(f'{current_dir}/{file}'):
                continue
            with zipfile.ZipFile(f'./{project}.zip', mode='a') as score_zip:
                score_zip.write(f'{current_dir}/{file}')

    return ExitCode.SUCCEEDED


def delete_score_info():
    """Delete .score directory and db directory.

    :return:
    """
    if os.path.exists('./.score'):
        shutil.rmtree('./.score')
    if os.path.exists('./.db'):
        shutil.rmtree('./.db')
