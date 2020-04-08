# Copyright 2018 ICON Foundation
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

import json
import os
import shutil

from tbears.command.command_util import CommandUtil
from tbears.config.tbears_config import FN_CLI_CONF, FN_SERVER_CONF
from tbears.tbears_exception import TBearsCommandException

from tests.test_parsing_command import TestCommand


class TestCommandUtil(TestCommand):
    def setUp(self):
        super().setUp()
        self.tear_down_params = ['proj_unittest', 'proj_unittest_dir']
        self.project = 'proj_unittest'
        self.score_class = 'TestClass'

    def tearDown(self):
        try:
            if os.path.exists(FN_CLI_CONF):
                os.remove(FN_CLI_CONF)
            if os.path.exists(FN_SERVER_CONF):
                os.remove(FN_SERVER_CONF)
            if os.path.exists('./tbears.log'):
                os.remove('./tbears.log')
        except:
            pass

    # Test if cli arguments are parsed correctly.
    def test_init_args_parsing(self):
        # Parsing test
        cmd = f'init {self.project} {self.score_class}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'init')
        self.assertEqual(parsed.project, self.project)
        self.assertEqual(parsed.score_class, self.score_class)

        # Insufficient argument
        cmd = f'init {self.project}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_init_necessary_and_correct_args(self):
        project_dir = 'proj_unittest_dir'

        # Correct project name and class name
        cmd = f'init {self.project} {self.score_class}'
        parsed = self.parser.parse_args(cmd.split())
        try:
            CommandUtil._check_init(vars(parsed))
        except:
            exception_raised = True
        else:
            exception_raised = False
        self.assertFalse(exception_raised)

        # Project and score_class are same
        cmd = f'init {self.project} {self.project}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandUtil._check_init, vars(parsed))

        # Input existing SCORE path when initializing the SCORE
        cmd = f'init {self.project} {self.score_class}'
        parsed = self.parser.parse_args(cmd.split())
        self.touch(self.project)
        self.assertRaises(SystemExit, self.parser.parse_args, vars(parsed))
        os.remove(self.project)

        # Input existing SCORE directory when initializing the SCORE.
        cmd = f'init {project_dir} {self.score_class}'
        parsed = self.parser.parse_args(cmd.split())
        os.mkdir(project_dir)
        self.assertRaises(SystemExit, self.parser.parse_args, vars(parsed))
        shutil.rmtree(project_dir)

        # check the value of "main_module" field
        cmd = f'init {self.project} {self.score_class}'
        parsed = self.parser.parse_args(cmd.split())
        self.cmd.cmdUtil.init(conf=vars(parsed))
        with open(f'{self.project}/package.json', mode='r') as package_contents:
            package_json = json.loads(package_contents.read())
        main = package_json['main_module']
        self.assertEqual(self.project, main)
        shutil.rmtree(self.project)

    def test_samples_args_parsing(self):
        # Parsing test
        cmd = f'samples'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'samples')

        # Too many arguments
        cmd = f'samples arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_genconf_args_parsing(self):
        # Parsing test
        cmd = f'genconf'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'genconf')

        # Too many arguments
        cmd = f'genconf arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
