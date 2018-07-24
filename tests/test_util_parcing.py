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
import json
import shutil

from tbears.command.command import Command
from tbears.command.command_util import CommandUtil
from tbears.command.command_score import CommandScore
from tbears.tbears_exception import TBearsCommandException

from tests.test_command_parcing import TestCommand


class TestCommandUtil(TestCommand):
    def setUp(self):
        super().setUp()
        self.tearDownParams = {'test_keystore': 'file', 'proj_unittest': 'file', 'proj_unittest_dir': 'dir'}

    def test_init_args_parcing(self):
        # Set parcing data
        project = 'proj_unittest_file'
        score_class = 'TestClass'

        # Parcing
        cmd = f'init {project} {score_class}'
        parsed = self.parser.parse_args(cmd.split())
        # check each parced data is equal to project, score_class
        self.assertEqual(parsed.command, 'init')
        self.assertEqual(parsed.project, project)
        self.assertEqual(parsed.score_class, score_class)

        # # argument checking module
        # not enough argument
        cmd = f'init {project}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        #do not check class name(e.g. def, as..)

    def test_init(self):
        # sb. _check_init function check, but there is no test when wrong params put in to func, exception raised
        # sb. check_init check
        # 1) project name is equal to score_class
        # 2) if there is same project_name folder
        project = 'proj_unittest'
        project_dir = 'proj_unittest_dir'

        score_class = 'TestClass'

        # Success case: correct project name and class name
        cmd = f'init {project} {score_class}'
        parsed = self.parser.parse_args(cmd.split())
        try:
            CommandUtil._check_init(vars(parsed))
        except:
            exception_raised = True
        else:
            exception_raised = False
        self.assertFalse(exception_raised)

        # Failure case: project and score_class are same
        cmd = f'init {project} {project}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandUtil._check_init, vars(parsed))

        # Failure case: when entering the existing SCORE path for initializing the SCORE
        cmd = f'init {project} {score_class}'
        self.touch(project)
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandUtil._check_init, vars(parsed))
        os.remove(project)

        # Failure Case: entering the existing SCORE directory for initializing the SCORE.
        cmd = f'init {project_dir} {score_class}'
        os.mkdir(project_dir)
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandUtil._check_init, vars(parsed))
        shutil.rmtree(project_dir)

        # Success case: entering the right path for initializing the SCORE.
        cmd = f'init {project} {score_class}'
        parsed = self.parser.parse_args(cmd.split())
        self.cmd.cmdUtil.init(conf=vars(parsed))
        with open(f'{project}/package.json', mode='r') as package_contents:
            package_json = json.loads(package_contents.read())
        main = package_json['main_file']
        self.assertEqual(project, main)
        shutil.rmtree(project)

    def test_initialize_project(self):
        # if the requirements setisfy, make project into the root directory
        # make project using get_score_main_template method(util/__init__.py)
        # To-Do: make sure if this function initialize project exactly
        pass

    def test_samples(self):
        # sb. main parcing,
        # parsing
        cmd = f'samples'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'samples')

        # too much argument
        cmd = f'samples arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

'''
    def test_keystore_args_parcing(self):
        # 제안. keystore path라고 적게 하는 것은 불친절한 것 같습니다
        # 제안2. 비밀번호 입력양식이 잘못됬을 때 바로 비밀번호를 다시 입력할 수 있도록
        # 하는 것이 좋을 것 같습니다.
        path = 'test_keystore'
        password = 'qwer1234%'

        # parsing
        cmd = f'keystore {path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'keystore')
        self.assertEqual(parsed.path, path)

        # not enough argument
        cmd = f'keystore'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # too much argument
        cmd = f'keystore {path} too_much_args'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_keystore(self):
        path = 'test_keystore'
        password = 'qwer1234%'

        # success case: _check_keystore_keystore method returns password if exact params input
        cmd = f'keystore {path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(CommandUtil._check_keystore(vars(parsed),password),password)

        # path file exist
        cmd = f'keystore {path}'
        self.touch(path)
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandUtil._check_keystore, vars(parsed), password)
        os.remove(path)

        # invalid path: no directory exists
        # 'keystore' command doesn't make directory. so only exist path valid
        cmd = f'keystore ./no_exist_directory/{path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(Exception, self.cmd.cmdUtil.keystore, vars(parsed), password)

        # invalid password
        cmd = f'keystore {path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandUtil._check_keystore, vars(parsed), 'qwe')
'''