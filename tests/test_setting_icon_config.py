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
from tbears.command.command import Command
from tbears.config.tbears_config import FN_CLI_CONF, FN_SERVER_CONF, tbears_cli_config, tbears_server_config
from tests.test_util import TEST_UTIL_DIRECTORY


IN_ICON_CONFIG_TEST_DIRECTORY = os.path.join(TEST_UTIL_DIRECTORY, 'test_icon_config')

# this variable is for reset tbears_cli_config data.
# after to tests, tbears_cli_config's options are changed and not refreshed.
# so need to be reset these data
# (if tbears support the interactive mode, tbears_cli_config should always refreshed automatically)


def get_config_reset(config_path, default_conf: dict):
    try:
        with open(config_path) as f:
            conf: dict = json.load(f)
    except:
        return deepcopy(default_conf)
    else:
        return deepcopy(conf)


tbears_cli_config_reset = get_config_reset(FN_CLI_CONF, tbears_cli_config)
tbears_server_config_reset = get_config_reset(FN_SERVER_CONF, tbears_server_config)


def setting_cli(cli_tuple):
    cli = " ".join(cli_tuple)
    cli = re.sub(' +', ' ', cli)
    return cli


def rm_file_dir(rm_list: list):
    for path in rm_list:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            continue


# this test can not check args parsing
# parsing should be checked on test_{command}_parsing
class TestCliTestUtil(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.parser = self.cmd.parser
        self.subparsers = self.cmd.subparsers
        self.tear_down_params = []
        self.verificationErrors = []

    def tearDown(self):
        rm_file_dir(self.tear_down_params)
        for idx, error in enumerate(self.verificationErrors):
            print('============ error number: '+str(idx)+' =====================')
            print(error)
            print(' ')
        self.assertEqual([], self.verificationErrors)

        tbears_server_config.update(deepcopy(tbears_server_config_reset))
        tbears_cli_config.update(deepcopy(tbears_cli_config_reset))

    @staticmethod
    def make_config_option_list(parsed_args: dict, config_name: str):
        # make config key list which is for check each config key and value.
        if config_name == 'cli':
            tbears_config = deepcopy(tbears_cli_config_reset)
        elif config_name == 'server':
            tbears_config = deepcopy(tbears_server_config_reset)

        command = parsed_args.get('command', None)

        if command in tbears_config:
            tbears_config.update(tbears_config[command])
            del tbears_config[command]
        tbears_config.update({k: v for k, v in parsed_args.items() if v is not None})
        config_option_list = [key for key in tbears_config.keys()]

        return config_option_list

    @staticmethod
    def make_whole_possible_cli(test_opts: dict):
        user_config = test_opts.get('optional_args', [])

        for idx, args in enumerate(test_opts['positional_args']):
            user_config.insert(idx, [args])
        for idx, file in enumerate(test_opts['positional_files']):
            user_config.insert(idx, [file])
        user_config.insert(0, [test_opts['command']])

        return [setting_cli(cli) for cli in itertools.product(*user_config)]

    @staticmethod
    def check_test_opts(test_opts: dict):
        config_type = test_opts.get('config_type', None)
        if config_type is None or (config_type != 'cli' and config_type != 'server'):
            raise Exception('invalid config_type')

        if test_opts.get('command', None) is None or test_opts.get('description', None) is None:
            raise Exception('invalid command or description')

        if test_opts.get('get_config_func', None) is None or not callable(test_opts['get_config_func']):
            raise Exception('invalid get_config_func')

    def config_setting_test_module(self, test_opts: dict):
        self.check_test_opts(test_opts)
        # check if user config path is set or not
        if test_opts.get('user_path', None):
            with open(test_opts['user_path']) as user_conf_path:
                default_conf: dict = json.load(user_conf_path)
        else:
            if test_opts['config_type'] == 'cli':
                default_conf = deepcopy(tbears_cli_config_reset)
            elif test_opts['config_type'] == 'server':
                default_conf = deepcopy(tbears_server_config_reset)

        if test_opts['command'] in default_conf:
            default_conf.update(default_conf[test_opts['command']])
            del default_conf[test_opts['command']]

        whole_possible_cli = self.make_whole_possible_cli(test_opts)

        for cli in whole_possible_cli:
            parsed = self.parser.parse_args(cli.split())

            # should be refactoring, get_icon_conf methods has one more parameter (project param)
            actual_conf = test_opts['get_config_func'](parsed.command, args=vars(parsed))

            expected_conf = deepcopy(default_conf)
            expected_conf.update({k: v for k, v in vars(parsed).items() if v is not None})

            config_option_list = self.make_config_option_list(parsed_args=vars(parsed),
                                                              config_name=test_opts['config_type'])

            #print('============================================cli=============================================')
            #print('* cli: ', cli)
            #print('* expected_conf: ', expected_conf)
            #print('* actual_conf:   ', actual_conf)

            for key in config_option_list:
                # actual_conf['command'] = 'raise_error'
                try:
                    self.assertEqual(expected_conf[key], actual_conf[key],
                                     msg='\nfailed command: ' + test_opts['command'] +
                                         '\nfailed cli:     ' + cli +
                                         '\nfailed key:     ' + key +
                                         '\ncase:           ' + test_opts['description'] + '\n')
                except AssertionError as e:
                    self.verificationErrors.append(str(e))

        if test_opts['config_type'] == 'cli':
            tbears_cli_config.update(deepcopy(tbears_cli_config_reset))
        elif test_opts['config_type'] == 'server':
            tbears_server_config.update(deepcopy(tbears_server_config_reset))

    def config_setting_test_module_wrapper(self, test_command_list: list):
        for test_command in test_command_list:
            for dir in test_command['positional_files']:
                # todo: should check whether if file or dir, and make adequately
                os.mkdir(dir)
                self.tear_down_params.append(dir)

            self.config_setting_test_module(test_command)

            rm_file_dir(self.tear_down_params)
            self.tear_down_params.clear()

    def test_command_score_config_setting(self):
        u = ['-u http://127.0.0.1:9000/api/v3_user_input', '']
        m = ['-m install', '-m update', '']
        f = ['-f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', '']
        o = ['-o cx0000000000000000000000000000000000000000', '']
        k = [f'-k {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_cli_config_keystore")}', '']
        n = ['-n 0x3_user_input', '']
        c = [f'-c {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json")}']

        # deploy
        test_deploy_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'deploy',
            'positional_files': ['test_project'],
            'positional_args': [],
            'get_config_func': CommandScore.get_icon_conf,
            'description': 'case: config: X , user input: x'
        }
        test_deploy_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'deploy',
            'positional_files': ['test_project'],
            'positional_args': [],
            'optional_args': [c],
            'get_config_func': CommandScore.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_deploy_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'deploy',
            'positional_files': ['test_project'],
            'positional_args': [],
            'optional_args': [u, m, f, o, k, n],
            'get_config_func': CommandScore.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_deploy_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'deploy',
            'positional_files': ['test_project'],
            'positional_args': [],
            'optional_args': [u, m, f, o, k, n, c],
            'get_config_func': CommandScore.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        deploy_test = [test_deploy_opts_c_x_i_x,
                       test_deploy_opts_c_o_i_x,
                       test_deploy_opts_c_x_i_o,
                       test_deploy_opts_c_o_i_o]

        self.config_setting_test_module_wrapper(deploy_test)

    def test_command_wallet_config_setting(self):
        u = ['-u http://127.0.0.1:9000/api/v3_user_input', '']
        f = ['-f hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', '']
        k = [f'-k {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_cli_config_keystore")}', '']
        n = ['-n 0x3_user_input', '']
        c = [f'-c {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json")}']

        # lastblock
        test_lastblock_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'lastblock',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_lastblock_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'lastblock',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_lastblock_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'lastblock',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_lastblock_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'lastblock',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        lastblock_test = [test_lastblock_opts_c_x_i_x,
                          test_lastblock_opts_c_o_i_x,
                          test_lastblock_opts_c_x_i_o,
                          test_lastblock_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(lastblock_test)

        # blockbyhash
        test_blockbyhash_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'blockbyhash',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_blockbyhash_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'blockbyhash',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_blockbyhash_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'blockbyhash',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_blockbyhash_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'blockbyhash',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        blockbyhash_test = [test_blockbyhash_opts_c_x_i_x,
                            test_blockbyhash_opts_c_o_i_x,
                            test_blockbyhash_opts_c_x_i_o,
                            test_blockbyhash_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(blockbyhash_test)

        # blockbyheight
        test_blockbyheight_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'blockbyheight',
            'positional_files': [],
            'positional_args': ["0"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_blockbyheight_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'blockbyheight',
            'positional_files': [],
            'positional_args': ["0"],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_blockbyheight_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'blockbyheight',
            'positional_files': [],
            'positional_args': ["0"],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_blockbyheight_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'blockbyheight',
            'positional_files': [],
            'positional_args': ["0"],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        blockbyheight_test = [test_blockbyheight_opts_c_x_i_x,
                              test_blockbyheight_opts_c_o_i_x,
                              test_blockbyheight_opts_c_x_i_o,
                              test_blockbyheight_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(blockbyheight_test)

        # txresult
        test_txresult_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'txresult',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_txresult_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'txresult',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_txresult_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'txresult',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_txresult_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'txresult',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        txresult_test = [test_txresult_opts_c_x_i_x,
                         test_txresult_opts_c_o_i_x,
                         test_txresult_opts_c_x_i_o,
                         test_txresult_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(txresult_test)

        # transfer
        test_transfer_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'transfer',
            'positional_files': [],
            'positional_args': ["cx0000000000000000000000000000000000000000", "1e18"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_transfer_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'transfer',
            'positional_files': [],
            'positional_args': ["cx0000000000000000000000000000000000000000", "1e18"],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_transfer_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'transfer',
            'positional_files': [],
            'positional_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab", "1e18"],
            'optional_args': [f, k, n, u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_transfer_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'transfer',
            'positional_files': [],
            'positional_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab", "1e18"],
            'optional_args': [f, k, n, u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        transfer_test = [test_transfer_opts_c_x_i_x,
                         test_transfer_opts_c_o_i_x,
                         test_transfer_opts_c_x_i_o,
                         test_transfer_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(transfer_test)

        # balance
        test_balance_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'balance',
            'positional_files': [],
            'positional_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_balance_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'balance',
            'positional_files': [],
            'positional_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_balance_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'balance',
            'positional_files': [],
            'positional_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_balance_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'balance',
            'positional_files': [],
            'positional_args': ["hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        balance_test = [test_balance_opts_c_x_i_x,
                        test_balance_opts_c_o_i_x,
                        test_balance_opts_c_x_i_o,
                        test_balance_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(balance_test)

        # totalsupply
        test_totalsupply_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'totalsupply',
            'positional_files': [],
            'positional_args': [],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_totalsupply_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'totalsupply',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_totalsupply_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'totalsupply',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_totalsupply_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'totalsupply',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        totalsupply_test = [test_totalsupply_opts_c_x_i_x,
                            test_totalsupply_opts_c_o_i_x,
                            test_totalsupply_opts_c_x_i_o,
                            test_totalsupply_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(totalsupply_test)

        # scoreapi
        test_scoreapi_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'scoreapi',
            'positional_files': [],
            'positional_args': ["cxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_scoreapi_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'scoreapi',
            'positional_files': [],
            'positional_args': ["cxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_scoreapi_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'scoreapi',
            'positional_files': [],
            'positional_args': ["cxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_scoreapi_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'scoreapi',
            'positional_files': [],
            'positional_args': ["cxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        scoreapi_test = [test_scoreapi_opts_c_x_i_x,
                         test_scoreapi_opts_c_o_i_x,
                         test_scoreapi_opts_c_x_i_o,
                         test_scoreapi_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(scoreapi_test)

        # txbyhash
        test_txbyhash_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'txbyhash',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_txbyhash_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'txbyhash',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_txbyhash_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'txbyhash',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_txbyhash_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'txbyhash',
            'positional_files': [],
            'positional_args': ["0x990fb821e0499fe2c62b6e7e3259d7ddc594f3f83e85879ade9ed8379375f2ef"],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        txbyhash_test = [test_txbyhash_opts_c_x_i_x,
                         test_txbyhash_opts_c_o_i_x,
                         test_txbyhash_opts_c_x_i_o,
                         test_txbyhash_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(txbyhash_test)

        # sendtx
        test_sendtx_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'sendtx',
            'positional_files': [],
            'positional_args': [os.path.join(TEST_UTIL_DIRECTORY, 'send.json')],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_sendtx_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'sendtx',
            'positional_files': [],
            'positional_args': [os.path.join(TEST_UTIL_DIRECTORY, 'send.json')],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_sendtx_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'sendtx',
            'positional_files': [],
            'positional_args': [os.path.join(TEST_UTIL_DIRECTORY, 'send.json')],
            'optional_args': [k, u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_sendtx_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'sendtx',
            'positional_files': [],
            'positional_args': [os.path.join(TEST_UTIL_DIRECTORY, 'send.json')],
            'optional_args': [k, u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        sendtx_test = [test_sendtx_opts_c_o_i_o,
                       test_sendtx_opts_c_o_i_x,
                       test_sendtx_opts_c_x_i_o,
                       test_sendtx_opts_c_x_i_x]
        self.config_setting_test_module_wrapper(sendtx_test)

        # call
        test_call_opts_c_x_i_x = {
            'config_type': 'cli',
            'command': 'call',
            'positional_files': [],
            'positional_args': [os.path.join(TEST_UTIL_DIRECTORY, 'call.json')],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_call_opts_c_o_i_x = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'call',
            'positional_files': [],
            'positional_args': [os.path.join(TEST_UTIL_DIRECTORY, 'call.json')],
            'optional_args': [c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_call_opts_c_x_i_o = {
            'config_type': 'cli',
            'command': 'call',
            'positional_files': [],
            'positional_args': [os.path.join(TEST_UTIL_DIRECTORY, 'call.json')],
            'optional_args': [u],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_call_opts_c_o_i_o = {
            'config_type': 'cli',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_cli_config.json"),
            'command': 'call',
            'positional_files': [],
            'positional_args': [os.path.join(TEST_UTIL_DIRECTORY, 'call.json')],
            'optional_args': [u, c],
            'get_config_func': CommandWallet.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        call_test = [test_call_opts_c_o_i_o,
                     test_call_opts_c_o_i_x,
                     test_call_opts_c_x_i_o,
                     test_call_opts_c_x_i_x]
        self.config_setting_test_module_wrapper(call_test)

    def test_command_server_config_setting(self):
        a = ['-a 127.0.0.1', '']
        p = ['-p %d' % 10000, '']
        c = [f'-c {os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_server_config.json")}']

        # start_opts
        test_start_opts_c_x_i_x = {
            'config_type': 'server',
            'command': 'start',
            'positional_files': [],
            'positional_args': [],
            'get_config_func': CommandServer.get_icon_conf,
            'description': 'config: X , user input: X'
        }
        test_start_opts_c_o_i_x = {
            'config_type': 'server',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_server_config.json"),
            'command': 'start',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [c],
            'get_config_func': CommandServer.get_icon_conf,
            'description': 'config: O , user input: X'
        }
        test_start_opts_c_x_i_o = {
            'config_type': 'server',
            'command': 'start',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [a, p],
            'get_config_func': CommandServer.get_icon_conf,
            'description': 'config: X , user input: O'
        }
        test_start_opts_c_o_i_o = {
            'config_type': 'server',
            'user_path': os.path.join(IN_ICON_CONFIG_TEST_DIRECTORY, "test_tbears_server_config.json"),
            'command': 'start',
            'positional_files': [],
            'positional_args': [],
            'optional_args': [a, p, c],
            'get_config_func': CommandServer.get_icon_conf,
            'description': 'config: O , user input: O'
        }

        start_test = [test_start_opts_c_x_i_x,
                      test_start_opts_c_o_i_x,
                      test_start_opts_c_x_i_o,
                      test_start_opts_c_o_i_o]
        self.config_setting_test_module_wrapper(start_test)


