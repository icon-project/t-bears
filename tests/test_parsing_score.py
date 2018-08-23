# Copyright 2018 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil

from tbears.command.command_score import CommandScore
from tbears.tbears_exception import TBearsCommandException
from tests.test_parsing_command import TestCommand
from tests.test_util import TEST_UTIL_DIRECTORY


class TestCommandScore(TestCommand):
    def setUp(self):
        super().setUp()
        self.tear_down_params = ['proj_unittest']

        self.project = 'proj_unittest'
        self.uri = 'http://127.0.0.1:9000/api/v3'
        self.arg_type = 'tbears'
        self.mode = "install"
        self.arg_from = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.to = "cx0000000000000000000000000000000000000000"
        self.keystore = os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')
        self.config_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')

    # Test if cli arguments are parsed correctly.
    def test_deploy_args_parsing(self):
        # Parsing test
        os.mkdir(self.project)
        cmd = f"deploy {self.project} -u {self.uri} -t {self.arg_type} -m {self.mode} -f {self.arg_from} " \
              f"-o {self.to} -k {self.keystore} -c {self.config_path} "
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'deploy')
        self.assertEqual(parsed.project, self.project)
        self.assertEqual(parsed.uri, self.uri)
        self.assertEqual(parsed.contentType, self.arg_type)
        self.assertEqual(parsed.mode, self.mode)
        self.assertEqual(parsed.to, self.to)
        self.assertEqual(parsed.keyStore, self.keystore)
        self.assertEqual(parsed.config, self.config_path)
        shutil.rmtree(self.project)

        # No project directory
        cmd = f'deploy {self.project}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        os.mkdir(self.project)

        # Invalid from address
        invalid_addr = 'hx1'
        cmd = f'deploy {self.project} -f {invalid_addr}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Too much argument
        cmd = f'deploy arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Insufficient argument
        cmd = f'deploy'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Wrong option
        cmd = f'deploy {self.project} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # More then 2 arguments in -t option
        cmd = f'deploy {self.project} -t icon tbears to_much -t option args'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Not supported type (only icon, tbears are available)
        cmd = f'deploy {self.project} -t not_supported_type'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Not supported mode (only install, update are available)
        cmd = f'deploy {self.project} -m not_supported_mode'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Invalid to address
        invalid_addr = 'hx1'
        cmd = f'deploy {self.project} -o {invalid_addr}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Keystore file does not exist
        cmd = f'deploy {self.project} -t zip -k ./keystore_not_exist'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # config file does not exist
        cmd = f'deploy {self.project} -c ./config_not_exist'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        shutil.rmtree(self.project)

    # Deploy method(deploy, _check_deploy) test. before deploy score,
    # Check if arguments satisfy requirements.
    # bug: when test this method in terminal, no error found, but in pycharm Run Test, it raise error
    def test_check_deploy_necessary_args(self):
        # # Deploy essential check
        # No project directory
        os.mkdir(self.project)
        cmd = f'deploy {self.project}'
        parsed = self.parser.parse_args(cmd.split())
        shutil.rmtree(self.project)
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        os.mkdir(self.project)

        # # Deploy to zip

        # Without keystore option
        cmd = f'deploy {self.project} -t zip'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # Keystore file does not exist
        no_keystore = './keystore_not_exist'
        cmd = f'deploy {self.project} -t zip -k {no_keystore}'
        self.touch(no_keystore)
        parsed = self.parser.parse_args(cmd.split())
        os.remove(no_keystore)
        self.assertRaises(SystemExit, self.parser.parse_args, vars(parsed))

        # Invaild password value
        # Even though input invaild password, _check_deploy method should return password
        # (this method doesn't check password value)
        cmd = f'deploy {self.project} -t zip -k {self.keystore}'
        user_input_password = "1234"
        expected_password = "1234"
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(CommandScore._check_deploy(vars(parsed), user_input_password), expected_password)

        # # Deploy to tbears

        # Correct command (when deploy to tbears, return value from _check_deploy method should None)
        cmd = f'deploy {self.project} -t tbears'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # Deploy tbears SCORE to remote(doesn't check actual -uri value)
        cmd = f'deploy {self.project} -t tbears -u http://1.2.3.4:9000/api/v3'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # Insufficient argument
        cmd = f'deploy {self.project} -m update'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        shutil.rmtree(self.project)

    def test_clear_args_parsing(self):
        # Parsing test
        cmd = f'clear'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'clear')

        # Too much argument
        cmd = f'clear arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())


