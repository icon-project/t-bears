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
import os

from tbears.command.command_wallet import CommandWallet
from tbears.tbears_exception import TBearsCommandException

from tests.test_command_parsing import TestCommand

class TestWalletParsing(TestCommand):
    def setUp(self):
        super().setUp()
        self.tear_down_params = {'unit_test_keystore': 'file'}
        self.keystore_path = 'unit_test_keystore'
        self.keystore_password = 'qwer1234%'

    def test_keystore_args_parsing(self):
        # Parsing test
        cmd = f'keystore {self.keystore_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'keystore')
        self.assertEqual(parsed.path, self.keystore_path)

        # Not enough argument
        cmd = f'keystore'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Too much argument
        cmd = f'keystore {self.keystore_path} too_much_args'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_keystore_correct_argument(self):
        # Correct command and environment(same file doesn't exists)
        expected_password = self.keystore_password
        cmd = f'keystore {self.keystore_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(CommandWallet._check_keystore(vars(parsed), self.keystore_password), expected_password)

        # File already exist
        cmd = f'keystore {self.keystore_path}'
        self.touch(self.keystore_path)
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandWallet._check_keystore, vars(parsed), self.keystore_password)
        os.remove(self.keystore_path)

        # Invalid path: no directory exists
        # 'keystore' command doesn't make directory. so only exist path valid
        cmd = f'keystore ./no_exist_directory/{self.keystore_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(Exception, self.cmd.cmdWallet.keystore, vars(parsed), self.keystore_password)
