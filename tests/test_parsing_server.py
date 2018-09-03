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

from tests.test_parsing_command import TestCommand
from tests.test_util import TEST_UTIL_DIRECTORY

class TestCommandServer(TestCommand):
    def tearDown(self):
        pass

    # Test if cli arguments are parced correctly.
    def test_start_args_parsing(self):
        hostAddress = '9.9.9.9'
        port = 5000
        config_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_server_config.json')

        # Parsing test
        cmd = f'start -a {hostAddress} -p {port} -c {config_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'start')
        self.assertEqual(str(parsed.hostAddress), hostAddress)
        self.assertEqual(int(parsed.port), port)
        self.assertEqual(parsed.config, config_path)

        # Too many arguments (start cli doesn't need argument)
        cmd = f'start wrongArgument'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Wrong option
        cmd = f'start -w wrongOption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Invalid --address type
        cmd = f'start --address type_is_to_be_ip_address'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Invalid --port type
        cmd = f'start --port type_to_be_int'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_stop_args_parsing(self):
        # Parsing test
        cmd = f'stop'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'stop')

        # Invalid argument (stop cli doesn't accept argument)
        cmd = f'stop wrongArgument'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Wrong option (stop cli has no option)
        cmd = f'stop -w wrongOption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

