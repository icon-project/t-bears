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

from tbears.tbears_exception import TBearsCommandException
from tbears.util import (
    get_score_main_template, get_sample_token_contents, get_sample_crowd_sale_contents,
    get_package_json_dict, write_file, get_init_template
)
from tbears.config.tbears_config import tbears_config, deploy_config


class CommandUtil(object):
    def __init__(self, subparsers):
        self._add_init_parser(subparsers)
        self._add_samples_parser(subparsers)

    @staticmethod
    def _add_init_parser(subparsers) -> None:
        parser = subparsers.add_parser('init', help='Initialize tbears project',
                                       description='Initialize SCORE development environment.\n'
                                                   'Generate <project>.py and package.json in <project> directory. '
                                                   'The name of the score class is <score_class>.')
        parser.add_argument('project', help='Project name')
        parser.add_argument('score_class', help='SCORE class name')

    @staticmethod
    def _add_samples_parser(subparsers):
        subparsers.add_parser('samples',
                              help='Create two SCORE samples (standard_crowd_sale, standard_token)',
                              description='Create two SCORE samples (standard_crowd_sale, standard_token)')

    def run(self, args):
        if not hasattr(self, args.command):
            print(f"Wrong command {args.command}")
            return

        # run command
        getattr(self, args.command)(vars(args))

    def init(self, conf: dict):
        """Initialize the tbears service.

        :param conf: init command configuration
        """
        self._check_init(conf)

        self.__initialize_project(project=conf['project'],
                                  score_class=conf['score_class'],
                                  contents_func=get_score_main_template)

        print(f"Initialized tbears successfully")

    def samples(self, _conf: dict):
        """Generate two SCORE samples (standard_crowd_sale, standard_token)
        :param _conf: samples command configuration
        """
        self.__initialize_project(project="standard_token", score_class="StandardToken",
                                  contents_func=get_sample_token_contents)
        self.__initialize_project(project="standard_crowd_sale", score_class="StandardCrowdSale",
                                  contents_func=get_sample_crowd_sale_contents)

        print(f"Made samples successfully")

    def check_command(self, command):
        return hasattr(self, command)

    @staticmethod
    def _check_init(conf: dict):
        if conf['project'] == conf['score_class']:
            raise TBearsCommandException(f'<project> and <score_class> must be different.')
        if os.path.exists(f"./{conf['project']}"):
            raise TBearsCommandException(f'{conf["project"]} directory must be empty.')

    @staticmethod
    def __initialize_project(project: str, score_class: str, contents_func):
        """Initialize the tbears project

        :param project: name of tbears project.
        :param score_class: class name of SCORE.
        :param contents_func contents generator
        """
        package_json_dict = get_package_json_dict(project, score_class)
        package_json_contents = json.dumps(package_json_dict, indent=4)
        py_contents = contents_func(score_class)
        init_contents = get_init_template(project, score_class)

        write_file(project, f"{project}.py", py_contents)
        write_file(project, "package.json", package_json_contents)
        write_file(project, '__init__.py', init_contents)
        write_file(f'{project}/tests', f'test_{project}.py', '')
        write_file(f'{project}/tests', f'__init__.py', '')
        write_file('./', "tbears.json", json.dumps(tbears_config, indent=4))
        write_file('./', "deploy.json", json.dumps(deploy_config, indent=4))

    @staticmethod
    def get_init_args(project: str, score_class: str):
        return {
            'project': project,
            'score_class': score_class
        }
