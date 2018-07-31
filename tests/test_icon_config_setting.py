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

import unittest
import json
import os
import shutil
import itertools
import re
from copy import deepcopy

from iconcommons.icon_config import IconConfig
from tbears.command.command import Command
from tbears.config.tbears_config import FN_CLI_CONF, tbears_cli_config
from tests.test_util import TEST_UTIL_DIRECTORY

IN_ICON_CONFIG_TEST_DIRECTORY = os.path.join(TEST_UTIL_DIRECTORY, 'test_icon_config/tbears_cli_config.json')

u = ['-u http://127.0.0.1:9000/api/v3_user_input', '']
t = ['-t tbears', '-t zip', '']
m = ['-m install', '-m update', '']
f = ['-f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', '']
o = ['-o cx0000000000000000000000000000000000000000', '']
k = ['-k keystore_user_input', '']
n = ['-n 0x3_user_input', '']
c = [f'-c {IN_ICON_CONFIG_TEST_DIRECTORY}']


def setting_cli(cli_tuple):
    cli = " ".join(cli_tuple)
    cli = re.sub(' +', ' ', cli)
    return cli


class TestIconConfig(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.parser = self.cmd.parser
        self.subparsers = self.cmd.subparsers

        self.tear_down_params = {'proj_unittest'}
        self.project = 'proj_unittest'
        self.command = 'deploy'

        # make config key list which is for check each config key and value.
        self.tbears_cli_config = deepcopy(tbears_cli_config)
        self.tbears_cli_config.update(self.tbears_cli_config['deploy'])
        del self.tbears_cli_config['deploy']
        self.config_option_list = [key for key in self.tbears_cli_config.keys()]

    def tearDown(self):
        # tear_down_params' key value(file or directory) is always relative path
        for path in self.tear_down_params:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                continue

    # -c: x, user input: X
    # base: default pass, overwrite: nothing
    def test_get_score_conf_not_set(self):
        os.mkdir(self.project)

        cmd = f'deploy {self.project}'
        parsed = self.parser.parse_args(cmd.split())

        actual_conf = self.cmd.cmdScore.get_score_conf(parsed.command, args=vars(parsed))
        expected_conf = self.tbears_cli_config

        for key in self.config_option_list:
            self.assertEqual(expected_conf[key], actual_conf[key], msg='failed key: ' + key)

        shutil.rmtree(self.project)

    # -c: O, user input: X
    # base: default pass, overwrite: -c
    def test_get_score_conf_set_c(self):
        with open(IN_ICON_CONFIG_TEST_DIRECTORY) as user_conf_path:
            expected_conf: dict = json.load(user_conf_path)
        expected_conf.update(expected_conf['deploy'])
        del expected_conf['deploy']

        os.mkdir(self.project)

        cmd = f'deploy {self.project} -c {IN_ICON_CONFIG_TEST_DIRECTORY}'
        parsed = self.parser.parse_args(cmd.split())

        actual_conf = self.cmd.cmdScore.get_score_conf(parsed.command, args=vars(parsed))

        for key in self.config_option_list:
            self.assertEqual(expected_conf[key], actual_conf[key])

        shutil.rmtree(self.project)

    # -c: x, user input: O
    # base: default pass, overwrite: user input
    def test_get_score_conf_set_user_input(self):
        os.mkdir(self.project)

        whole_possible_cli = [setting_cli(cli) for cli in itertools.product([self.command], [self.project], u, t, m, f, o, n)]

        default_conf = IconConfig(FN_CLI_CONF, tbears_cli_config)
        default_conf.update(default_conf['deploy'])
        del default_conf['deploy']

        for cli in whole_possible_cli:
            parsed = self.parser.parse_args(cli.split())
            actual_conf = self.cmd.cmdScore.get_score_conf(parsed.command, args=vars(parsed))

            expected_conf = deepcopy(default_conf)
            expected_conf.update({k: v for k, v in vars(parsed).items() if v is not None})

            # print('============================================cli=============================================')
            # print(cli)
            # print('actual_conf', actual_conf)
            # print('expected_conf', expected_conf)

            for key in self.config_option_list:
                # actual_conf[key] = 'raise_error'
                self.assertEqual(actual_conf[key], expected_conf[key], msg='failed cli: ' + cli)

        shutil.rmtree(self.project)

    # -c: O, user input: O
    # base: default pass, overwrite: -c and user input
    def test_get_score_conf_set_c_and_user_input(self):
        os.mkdir(self.project)

        whole_possible_cli = [setting_cli(cli) for cli in itertools.product([self.command], [self.project], u, t, m, f, o, n, c)]

        with open(IN_ICON_CONFIG_TEST_DIRECTORY) as user_conf_path:
            user_conf: dict = json.load(user_conf_path)
        user_conf.update(user_conf['deploy'])
        del user_conf['deploy']

        for cli in whole_possible_cli:
            parsed = self.parser.parse_args(cli.split())
            actual_conf = self.cmd.cmdScore.get_score_conf(parsed.command, args=vars(parsed))

            expected_conf = deepcopy(user_conf)
            expected_conf.update({k: v for k, v in vars(parsed).items() if v})

            # print('============================================cli=============================================')
            # print(cli)
            # print('actual_conf', actual_conf)
            # print('expected_conf', expected_conf)

            for key in self.config_option_list:
                # actual_conf[key] = 'raise_error'
                self.assertEqual(expected_conf[key], actual_conf[key], msg='failed cli: ' + cli)

        shutil.rmtree(self.project)



