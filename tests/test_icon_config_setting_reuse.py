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

from tbears.command.command_server import CommandServer
from tbears.command.command_wallet import CommandWallet
from tbears.command.command_score import CommandScore
from iconcommons.icon_config import IconConfig
from tbears.command.command import Command
from tbears.config.tbears_config import FN_CLI_CONF, FN_SERVER_CONF, tbears_cli_config, tbears_server_config
from tests.test_util import TEST_UTIL_DIRECTORY


IN_ICON_CONFIG_TEST_DIRECTORY = os.path.join(TEST_UTIL_DIRECTORY, 'test_icon_config')

# this variable is for reset tbears_cli_config data.
# after to tests, tbears_cli_config's options are changed and not refreshed.
# so need to be reset these data
# (if tbears support the interactive mode, tbears_cli_config should always refreshed automatically)
tbears_cli_config_reset = deepcopy(tbears_cli_config)
tbears_server_config_reset = deepcopy(tbears_server_config)

def setting_cli(cli_tuple):
    cli = " ".join(cli_tuple)
    cli = re.sub(' +', ' ', cli)
    return cli

# todo: rmdir

# this test can not check args parsing
# parsing should be checked on test_{command}_parsing
class CliTestUtil(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.parser = self.cmd.parser
        self.subparsers = self.cmd.subparsers
        self.verificationErrors = []

    tbears_server_config.update(deepcopy(tbears_server_config_reset))
    tbears_cli_config.update(deepcopy(tbears_cli_config_reset))

    def tearDown(self):
        for idx, error in enumerate(self.verificationErrors):
            print(str(idx) + '--------')
            print(error)
            print('')
        self.assertEqual([], self.verificationErrors)

    tbears_server_config.update(deepcopy(tbears_server_config_reset))
    tbears_cli_config.update(deepcopy(tbears_cli_config_reset))

    @staticmethod
    def make_config_option_list(command: str, config_name: str):
        # make config key list which is for check each config key and value.
        if config_name == 'cli':
            tbears_config = deepcopy(tbears_cli_config)
        elif config_name == 'server':
            tbears_config = deepcopy(tbears_server_config)

        if command in tbears_config:
            tbears_config.update(tbears_config[command])
            del tbears_config[command]

        config_option_list = [key for key in tbears_config.keys()]

        return config_option_list

    @staticmethod
    def make_whole_possible_cli(test_opts: dict):
        user_config = test_opts.get('user_config_opts', [])

        for idx, args in enumerate(test_opts['user_config_args']):
            user_config.insert(idx, [args])
        for idx, file in enumerate(test_opts['user_config_file']):
            user_config.insert(idx, [file])
        user_config.insert(0, [test_opts['command']])

        return [setting_cli(cli) for cli in itertools.product(*user_config)]

    def c_x_i_x(self, test_opts: dict):
        cli = self.make_whole_possible_cli(test_opts).pop()
        parsed = self.parser.parse_args(cli.split())
        actual_conf = test_opts['get_config_func'](parsed.command, args=vars(parsed))

        if test_opts['config_type'] == 'cli':
            expected_conf = deepcopy(tbears_cli_config)
        elif test_opts['config_type'] == 'server':
            expected_conf = deepcopy(tbears_server_config)

        if parsed.command in expected_conf:
            expected_conf.update(expected_conf[parsed.command])
            del expected_conf[parsed.command]

        print('============================================cli=============================================')
        print('cli: ', cli)
        print('expected_conf: ', expected_conf)
        print('actual_conf: ', actual_conf)

        config_option_list = self.make_config_option_list(command=parsed.command,
                                                          config_name=test_opts['config_type'])
        for key in config_option_list:
            self.assertEqual(expected_conf[key], actual_conf[key], msg= \
                'failed command: ' + test_opts[
                    'command'] + '\nfailed cli: ' + cli + '\nfailed key: ' + key + '\ndesc: ' + test_opts[
                    'description'] + '\n')

    def c_x_i_x_wrapper(self, test_command_list: list):
        for test_command in test_command_list:
            for dir in test_command['user_config_file']:
                os.mkdir(dir)

            self.c_x_i_x(test_command)

            for dir in test_command['user_config_file']:
                shutil.rmtree(dir)

    def test_c_x_i_x_case(self):
        test_deploy_opts = {
            'config_type': 'cli',
            'command': 'deploy',
            'user_config_file': ['test_project'],
            'user_config_args': [],
            'get_config_func': CommandScore.get_score_conf,
            'description': 'case: config: X , user input: x'
        }
        test_lastblock_opts = {
            'config_type': 'cli',
            'command': 'lastblock',
            'user_config_file': [],
            'user_config_args': [],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_blockbyhash_opts = {
            'config_type': 'cli',
            'command': 'blockbyhash',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_blockbyheight_opts = {
            'config_type': 'cli',
            'command': 'blockbyheight',
            'user_config_file': [],
            'user_config_args': ["0"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_txresult_opts = {
            'config_type': 'cli',
            'command': 'txresult',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_transfer_opts = {
            'config_type': 'cli',
            'command': 'transfer',
            'user_config_file': [],
            'user_config_args': ["cx0000000000000000000000000000000000000000", "1e18"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_balance_opts = {
            'config_type': 'cli',
            'command': 'balance',
            'user_config_file': [],
            'user_config_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_totalsupply_opts = {
            'config_type': 'cli',
            'command': 'totalsupply',
            'user_config_file': [],
            'user_config_args': [],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_scoreapi_opts = {
            'config_type': 'cli',
            'command': 'scoreapi',
            'user_config_file': [],
            'user_config_args': ["cxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_txbyhash_opts = {
            'config_type': 'cli',
            'command': 'txbyhash',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }

        test_start_opts = {
            'config_type': 'server',
            'command': 'start',
            'user_config_file': [],
            'user_config_args': [],
            'get_config_func': CommandServer.get_icon_conf,
            'description': 'config: X , user input: X'
        }

        whole_test = [test_deploy_opts,
                      test_lastblock_opts,
                      test_blockbyhash_opts,
                      test_blockbyheight_opts,
                      test_txresult_opts,
                      test_transfer_opts,
                      test_balance_opts,
                      test_totalsupply_opts,
                      test_scoreapi_opts,
                      test_txbyhash_opts,
                      test_start_opts]

        self.c_x_i_x_wrapper(whole_test)

    def c_o_i_x(self, test_opts: dict):
        cli = self.make_whole_possible_cli(test_opts).pop()
        parsed = self.parser.parse_args(cli.split())
        actual_conf = test_opts['get_config_func'](parsed.command, args=vars(parsed))

        with open(test_opts['user_path']) as user_conf_path:
            user_conf: dict = json.load(user_conf_path)
        if test_opts['command'] in user_conf:
            user_conf.update(user_conf[test_opts['command']])
            del user_conf[test_opts['command']]

        expected_conf = deepcopy(user_conf)

        if parsed.command in expected_conf:
            expected_conf.update(expected_conf[parsed.command])
            del expected_conf[parsed.command]

        print('============================================cli=============================================')
        print('cli: ', cli)
        print('expected_conf: ', expected_conf)
        print('actual_conf: ', actual_conf)

        config_option_list = self.make_config_option_list(command=parsed.command,
                                                          config_name=test_opts['config_type'])
        for key in config_option_list:
            self.assertEqual(expected_conf[key], actual_conf[key], msg= \
                'failed command: ' + test_opts[
                    'command'] + '\nfailed cli: ' + cli + '\nfailed key: ' + key + '\ndesc: ' + test_opts[
                    'description'] + '\n')

        tbears_server_config.update(deepcopy(tbears_server_config_reset))
        tbears_cli_config.update(deepcopy(tbears_cli_config_reset))

    def c_o_i_x_wrapper(self, test_command_list: list):
        for test_command in test_command_list:
            for dir in test_command['user_config_file']:
                os.mkdir(dir)

            self.c_o_i_x(test_command)

            for dir in test_command['user_config_file']:
                shutil.rmtree(dir)

    def test_c_o_i_x_case(self):
        c = [f'-c {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json")}']

        test_deploy_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'deploy',
            'user_config_file': ['test_project'],
            'user_config_args': [],
            'user_config_opts': [c],
            'get_config_func': CommandScore.get_score_conf,
            'description': 'config: O , user input: X'
        }
        test_lastblock_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'lastblock',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_blockbyhash_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'blockbyhash',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_blockbyheight_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'blockbyheight',
            'user_config_file': [],
            'user_config_args': ["0"],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_txresult_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'txresult',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }

        test_transfer_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'transfer',
            'user_config_file': [],
            'user_config_args': ["cx0000000000000000000000000000000000000000_config_path", "1e18"],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_balance_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'balance',
            'user_config_file': [],
            'user_config_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_totalsupply_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'totalsupply',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_scoreapi_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'scoreapi',
            'user_config_file': [],
            'user_config_args': ["cxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_txbyhash_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'txbyhash',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }

        c = [f'-c {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_server_config.json")}']

        test_start_opts = {
            'config_type': 'server',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_server_config.json"),
            'command': 'start',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [c],
            'get_config_func': CommandServer.get_icon_conf,
            'description': 'config: O , user input: X'
        }

        whole_test = [test_deploy_opts,
                      test_lastblock_opts,
                      test_blockbyhash_opts,
                      test_blockbyheight_opts,
                      test_txresult_opts,
                      test_transfer_opts,
                      test_balance_opts,
                      test_totalsupply_opts,
                      test_scoreapi_opts,
                      test_txbyhash_opts,
                      test_start_opts]

        self.c_o_i_x_wrapper(whole_test)

    def c_x_i_o(self, test_opts: dict):
        if test_opts['config_type'] == 'cli':
            default_conf = deepcopy(tbears_cli_config)
        elif test_opts['config_type'] == 'server':
            default_conf = deepcopy(tbears_server_config)

        if test_opts['command'] in default_conf:
            default_conf.update(default_conf[test_opts['command']])
            del default_conf[test_opts['command']]

        whole_possible_cli = self.make_whole_possible_cli(test_opts)

        for cli in whole_possible_cli:
            parsed = self.parser.parse_args(cli.split())

            # should be refactoring, get_score_conf methods has one more parameter(project param)
            actual_conf = test_opts['get_config_func'](parsed.command, args=vars(parsed))

            expected_conf = deepcopy(default_conf)
            expected_conf.update({k: v for k, v in vars(parsed).items() if v is not None})

            config_option_list = self.make_config_option_list(command=parsed.command,
                                                              config_name=test_opts['config_type'])

            #print('============================================cli=============================================')
            #print('cli: ', cli)
            #print('expected_conf: ', expected_conf)
            #print('actual_conf: ', actual_conf)

            for key in config_option_list:
                # actual_conf[key] = 'raise_error'

                try:
                    self.assertEqual(expected_conf[key], actual_conf[key], msg= \
                        'failed command: ' + test_opts[
                            'command'] + '\nfailed cli: ' + cli + '\nfailed key: ' + key + '\ndesc: ' + test_opts[
                            'description'] + '\n')
                except AssertionError as e:
                    self.verificationErrors.append(str(e))

            if test_opts['config_type'] == 'server':
                tbears_server_config.update(deepcopy(tbears_server_config_reset))
            else:
                tbears_cli_config.update(deepcopy(tbears_cli_config_reset))

    def c_x_i_o_wrapper(self, test_command_list: list):
        for test_command in test_command_list:
            for dir in test_command['user_config_file']:
                os.mkdir(dir)

            self.c_x_i_o(test_command)

            for dir in test_command['user_config_file']:
                shutil.rmtree(dir)

    def test_c_x_i_o_case(self):
        u = ['-u http://127.0.0.1:9000/api/v3_user_input', '']
        t = ['-t tbears', '-t zip', '']
        m = ['-m install', '-m update', '']
        f = ['-f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbb', '']
        o = ['-o cx0000000000000000000000000000000000000111', '']
        k = [f'-k {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_cli_config_keystore")}', '']
        n = ['-n 0x3_user_input', '']

        test_deploy_opts = {
            'config_type': 'cli',
            'command': 'deploy',
            'user_config_file': ['test_project'],
            'user_config_args': [],
            'user_config_opts': [u, t, m, f, o, k, n],
            'get_config_func': CommandScore.get_score_conf,
            'description': 'config: X , user input: O'
        }
        test_lastblock_opts = {
            'config_type': 'cli',
            'command': 'lastblock',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_blockbyhash_opts = {
            'config_type': 'cli',
            'command': 'blockbyhash',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_blockbyheight_opts = {
            'config_type': 'cli',
            'command': 'blockbyheight',
            'user_config_file': [],
            'user_config_args': ["0"],
            'user_config_opts': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_txresult_opts = {
            'config_type': 'cli',
            'command': 'txresult',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_transfer_opts = {
            'config_type': 'cli',
            'command': 'transfer',
            'user_config_file': [],
            'user_config_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab", "1e18"],
            'user_config_opts': [f, k, n, u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_balance_opts = {
            'config_type': 'cli',
            'command': 'balance',
            'user_config_file': [],
            'user_config_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'user_config_opts': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_totalsupply_opts = {
            'config_type': 'cli',
            'command': 'totalsupply',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_scoreapi_opts = {
            'config_type': 'cli',
            'command': 'scoreapi',
            'user_config_file': [],
            'user_config_args': ["cxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'user_config_opts': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_txbyhash_opts = {
            'config_type': 'cli',
            'command': 'txbyhash',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }

        a = ['-a 127.0.0.1', '']
        p = ['-p %d' % 10000, '']

        test_start_opts = {
            'config_type': 'server',
            'command': 'start',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [a, p],
            'get_config_func': CommandServer.get_icon_conf,
            'description': 'config: X , user input: O'
        }

        whole_test = [test_deploy_opts,
                      test_lastblock_opts,
                      test_blockbyhash_opts,
                      test_blockbyheight_opts,
                      test_txresult_opts,
                      test_transfer_opts,
                      test_balance_opts,
                      test_totalsupply_opts,
                      test_scoreapi_opts,
                      test_txbyhash_opts,
                      test_start_opts]

        self.c_x_i_o_wrapper(whole_test)

    # before start this method, check some requirements
    # 1. -c config
    # 2. all test_cli_opts key
    def c_o_i_o(self, test_opts: dict):
        with open(test_opts['user_path']) as user_conf_path:
            user_conf: dict = json.load(user_conf_path)
        if test_opts['command'] in user_conf:
            user_conf.update(user_conf[test_opts['command']])
            del user_conf[test_opts['command']]

        whole_possible_cli = self.make_whole_possible_cli(test_opts)

        for cli in whole_possible_cli:
            parsed = self.parser.parse_args(cli.split())

            # should be refactoring, get_score_conf methods has one more parameter(project param)
            actual_conf = test_opts['get_config_func'](parsed.command, args=vars(parsed))

            expected_conf = deepcopy(user_conf)
            expected_conf.update({k: v for k, v in vars(parsed).items() if v is not None})

            config_option_list = self.make_config_option_list(command=parsed.command, config_name=test_opts['config_type'])

            print('============================================cli=============================================')
            print('cli: ', cli)
            print('expected_conf: ', expected_conf)
            print('actual_conf: ', actual_conf)

            for key in config_option_list:
                # actual_conf[key] = 'raise_error'

                try:
                    self.assertEqual(expected_conf[key], actual_conf[key], msg= \
                        'failed command: ' + test_opts['command'] + '\nfailed cli: ' + cli + '\nfailed key: ' + key + '\ndesc: ' +test_opts['description'] + '\n')
                except AssertionError as e: self.verificationErrors.append(str(e))

            if test_opts['config_type'] == 'server':
                tbears_server_config.update(deepcopy(tbears_server_config_reset))
            else:
                tbears_cli_config.update(deepcopy(tbears_cli_config_reset))

    def c_o_i_o_wrapper(self, test_command_list: list):
        for test_command in test_command_list:
            for dir in test_command['user_config_file']:
                os.mkdir(dir)

            self.c_o_i_o(test_command)

            for dir in test_command['user_config_file']:
                shutil.rmtree(dir)

    def test_c_o_i_o_case(self):
        u = ['-u http://127.0.0.1:9000/api/v3_user_input', '']
        t = ['-t tbears', '-t zip', '']
        m = ['-m install', '-m update', '']
        f = ['-f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', '']
        o = ['-o cx0000000000000000000000000000000000000000', '']
        k = [f'-k {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_cli_config_keystore")}', '']
        n = ['-n 0x3_user_input', '']
        c = [f'-c {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json")}']

        test_deploy_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'deploy',
            'user_config_file': ['test_project'],
            'user_config_args': [],
            'user_config_opts': [u, t, m, f, o, k, n, c],
            'get_config_func': CommandScore.get_score_conf,
            'description': 'config: O , user input: O'
        }
        test_lastblock_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'lastblock',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }
        test_blockbyhash_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'blockbyhash',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }
        test_blockbyheight_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'blockbyheight',
            'user_config_file': [],
            'user_config_args': ["0"],
            'user_config_opts': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }
        test_txresult_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'txresult',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }
        test_transfer_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'transfer',
            'user_config_file': [],
            'user_config_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab", "1e18"],
            'user_config_opts': [f, k, n, u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }
        test_balance_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'balance',
            'user_config_file': [],
            'user_config_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'user_config_opts': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }
        test_totalsupply_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'totalsupply',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }
        test_scoreapi_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'scoreapi',
            'user_config_file': [],
            'user_config_args': ["cxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'user_config_opts': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }
        test_txbyhash_opts = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'txbyhash',
            'user_config_file': [],
            'user_config_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'user_config_opts': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        a = ['-a 127.0.0.1', '']
        p = ['-p %d' % 10000, '']
        c = [f'-c {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_server_config.json")}']

        test_start_opts = {
            'config_type': 'server',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_server_config.json"),
            'command': 'start',
            'user_config_file': [],
            'user_config_args': [],
            'user_config_opts': [a, p, c],
            'get_config_func': CommandServer.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        whole_test = [test_deploy_opts,
                      test_lastblock_opts,
                      test_blockbyhash_opts,
                      test_blockbyheight_opts,
                      test_txresult_opts,
                      test_transfer_opts,
                      test_balance_opts,
                      test_totalsupply_opts,
                      test_scoreapi_opts,
                      test_txbyhash_opts,
                      test_start_opts]

        self.c_o_i_o_wrapper(whole_test)


