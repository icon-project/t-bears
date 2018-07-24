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

import unittest
import os
import shutil
import json
import socket

from tbears.command.command import Command
from tbears.command.command_util import CommandUtil
from tbears.command.command_score import CommandScore
from tbears.tbears_exception import TBearsCommandException

# from tbears.config.tbears_config import TBearsConfig
from tbears.util.icx_signer import key_from_key_store

from tests.test_command_parcing import TestCommand


class TestCommandServer(TestCommand):
    # override super().tearDown method
    def tearDown(self):
        pass

    def test_start_args_parcing(self):
        address = '0.0.0.0'
        port = 9000
        config_path = './tbears'

        # parsing
        cmd = f'start -a {address} -p {port} -c {config_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'start')
        self.assertEqual(str(parsed.address), address)
        self.assertEqual(parsed.port, port)
        self.assertEqual(parsed.config, config_path)

        # invalid argument
        cmd = f'start wrongArgument'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        # invalid options
        cmd = f'start --w wrongOption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'start --address type_is_to_be_ip_address'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'start --port type_to_be_int'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_start_server(self):
        # check if server is already running, raise error
        # To-Do: using mock, test the inside custom_argv logic
        pass

    def test_stop_args_parcing(self):
        # parsing
        cmd = f'stop'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'stop')

        # invalid argument
        cmd = f'stop wrongArgument'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'stop -w wrongOption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_stop(self):
        pass

    def test_is_server_running(self):
        # check if server is already running on current process, return False
        # as this test require server running, it will be tested on server test
        pass

    def test_write_server_conf(self):
        #need two case, True, False
        #check raise exception error
        pass





