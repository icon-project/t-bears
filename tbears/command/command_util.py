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

import IPython

from tbears.tbears_exception import TBearsCommandException
from tbears.util import (
    get_score_template, get_package_json_dict, write_file, PROJECT_ROOT_PATH
)
from tbears.config.tbears_config import FN_SERVER_CONF, FN_CLI_CONF, tbears_server_config, tbears_cli_config,\
    make_server_config, FN_KEYSTORE_TEST1, keystore_test1
from tbears.util.argparse_type import IconPath


class CommandUtil(object):
    def __init__(self, subparsers):
        self._add_init_parser(subparsers)
        self._add_samples_parser(subparsers)
        self._add_genconf_parser(subparsers)
        self._add_console_parser(subparsers)

    @staticmethod
    def _add_init_parser(subparsers) -> None:
        parser = subparsers.add_parser('init', help='Initialize tbears project',
                                       description='Initialize SCORE development environment.\n'
                                                   'Generate <project>.py, package.json and test code in <project>'
                                                   ' directory. '
                                                   'The name of the score class is <scoreClass>.')
        parser.add_argument('project', type=IconPath('w'), help='Project name')
        parser.add_argument('score_class', help='SCORE class name', metavar='scoreClass')

    @staticmethod
    def _add_samples_parser(subparsers):
        subparsers.add_parser('samples', help='This command has been deprecated since v1.1.0',
                              description='This command has been deprecated since v1.1.0')

    @staticmethod
    def _add_genconf_parser(subparser):
        subparser.add_parser('genconf', help=f'Generate tbears config files. ({FN_SERVER_CONF[2:]}, {FN_CLI_CONF[2:]} '
                                             f'and {FN_KEYSTORE_TEST1[2:]})',
                             description=f'Generate tbears config files. ({FN_SERVER_CONF[2:]}, {FN_CLI_CONF[2:]} '
                                         f'and {FN_KEYSTORE_TEST1[2:]})')

    @staticmethod
    def _add_console_parser(subparsers):
        subparsers.add_parser('console',
                              help='Get into tbears interactive mode by embedding IPython',
                              description='Get into tbears interactive mode by embedding IPython')

    def run(self, args):
        if not hasattr(self, args.command):
            print(f"Wrong command {args.command}")
            return

        # run command
        return getattr(self, args.command)(vars(args))

    def init(self, conf: dict):
        """Initialize the tbears service.

        :param conf: init command configuration
        """
        self._check_init(conf)

        # initialize score project package. score class is set using main template.
        # you can check main template at util/__init__/get_score_main_template method
        self.__initialize_project(project=conf['project'],
                                  score_class=conf['score_class'],
                                  contents_func=get_score_template)

        # generate configuration files
        self.__gen_conf_file()

        print(f"Initialized tbears successfully")

    def samples(self, _conf: dict):
        """ Show the information about the sample SCORE
        :param _conf: samples command configuration
        """
        print("The samples command has been deprecated since v1.1.0")
        print("You can check out and download the sample SCORE at https://github.com/icon-project/samples")

    def genconf(self, _conf: dict):
        """Generate tbears config files. (tbears_server_config.json, tbears_cli_config.json, keystore_test1)"""
        result = self.__gen_conf_file()

        if result:
            print(f"Made {', '.join(result)} successfully")
        else:
            print(f"There were configuration files already.")

    def check_command(self, command):
        return hasattr(self, command)

    @staticmethod
    def _check_init(conf: dict):
        if conf['project'] == conf['score_class']:
            raise TBearsCommandException(f'<project> and <score_class> must be different.')

    @staticmethod
    def __initialize_project(project: str, score_class: str, contents_func):
        """Initialize the tbears project

        :param project: name of tbears project.
        :param score_class: class name of SCORE.
        :param contents_func contents generator
        """
        # make package.json data
        package_json_dict = get_package_json_dict(project, score_class)
        package_json_contents = json.dumps(package_json_dict, indent=4)

        # when command is init, make score template.
        # when command is samples, make standard_crowd_sale or standard_token
        py_contents, test_contents = contents_func(score_class)

        write_file(project, f"{project}.py", py_contents)
        write_file(project, "package.json", package_json_contents)
        write_file(project, '__init__.py', '')
        if len(test_contents):
            write_file(f'{project}/tests', f'test_{project}.py', test_contents)
            write_file(f'{project}/tests', f'__init__.py', '')

    @staticmethod
    def __gen_conf_file() -> list:
        result = []

        if os.path.exists(FN_CLI_CONF) is False:
            result.append(FN_CLI_CONF[2:])
            write_file('./', FN_CLI_CONF, json.dumps(tbears_cli_config, indent=4))

        if os.path.exists(FN_SERVER_CONF) is False:
            result.append(FN_SERVER_CONF[2:])
            server_config_json = make_server_config(tbears_server_config)
            write_file('./', FN_SERVER_CONF, json.dumps(server_config_json, indent=4))

        if os.path.exists(FN_KEYSTORE_TEST1) is False:
            result.append(FN_KEYSTORE_TEST1[2:])
            write_file('./', FN_KEYSTORE_TEST1, json.dumps(keystore_test1, indent=4))

        return result

    @staticmethod
    def get_init_args(project: str, score_class: str):
        return {
            'project': project,
            'score_class': score_class
        }

    def console(self, conf):
        """Get into tbears interactive mode by embedding ipython"""
        IPython.start_ipython(['--profile', 'tbears', '--ipython-dir', f'{PROJECT_ROOT_PATH}/tbears'])
