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

from tbears.command.command_score import CommandScore, check_project
from tbears.tbears_exception import TBearsCommandException
from tests.test_parsing_command import TestCommand
from tests.test_util import TEST_UTIL_DIRECTORY


class TestCommandScore(TestCommand):
    def setUp(self):
        super().setUp()
        self.tear_down_params = ['proj_unittest']

        self.project = 'proj_unittest'
        self.project_class = 'ProjUnittest'
        self.uri = 'http://127.0.0.1:9000/api/v3'
        self.mode = "install"
        self.arg_from = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.to = "cx0000000000000000000000000000000000000000"
        self.keystore = os.path.join(TEST_UTIL_DIRECTORY, 'test_keystore')
        self.config_path = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')

    # Test if cli arguments are parsed correctly.
    def test_deploy_args_parsing(self):
        # Parsing test
        os.mkdir(self.project)
        cmd = f"deploy {self.project} -u {self.uri} -m {self.mode} -f {self.arg_from} " \
              f"-o {self.to} -k {self.keystore} -c {self.config_path} "
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'deploy')
        self.assertEqual(parsed.project, self.project)
        self.assertEqual(parsed.uri, self.uri)
        self.assertEqual(parsed.mode, self.mode)
        self.assertEqual(parsed.to, self.to)
        self.assertEqual(parsed.keyStore, self.keystore)
        self.assertEqual(parsed.config, self.config_path)
        shutil.rmtree(self.project)

        # No project directory or project zip file
        cmd = f'deploy {self.project}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        os.mkdir(self.project)

        # Invalid from address
        invalid_addr = 'hx1'
        cmd = f'deploy {self.project} -f {invalid_addr}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Too many arguments
        cmd = f'deploy arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Insufficient argument
        cmd = f'deploy'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Wrong option
        cmd = f'deploy {self.project} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Not supported mode (only install, update are available)
        cmd = f'deploy {self.project} -m not_supported_mode'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Invalid to address
        invalid_addr = 'hx1'
        cmd = f'deploy {self.project} -o {invalid_addr}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Keystore file does not exist
        cmd = f'deploy {self.project} -k ./keystore_not_exist'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # config file does not exist
        cmd = f'deploy {self.project} -c ./config_not_exist'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        shutil.rmtree(self.project)

    # Deploy method (deploy, _check_deploy) test. before deploy score,
    # Check if arguments satisfy requirements.
    # bug: when test this method in terminal, no error found, but in pycharm Run Test, it raise error
    def test_check_deploy_necessary_args(self):
        # # Deploy essential check
        # No project directory
        cmd = f'deploy {self.project}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Keystore file does not exist
        no_keystore = './keystore_not_exist'
        cmd = f'deploy {self.project} -k {no_keystore}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        conf = self.cmd.cmdUtil.get_init_args(project=self.project, score_class=self.project_class)
        self.cmd.cmdUtil.init(conf)

        # Invalid password value
        # Even though input invalid password, _check_deploy method should return password
        # (this method doesn't check password value)
        cmd = f'deploy {self.project} -k {self.keystore}'
        user_input_password = "1234"
        expected_password = "1234"
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(CommandScore._check_deploy(vars(parsed), user_input_password), expected_password)

        # Insufficient argument
        cmd = f'deploy {self.project} -m update'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        shutil.rmtree(self.project)

    def test_check_deploy_project(self):
        conf = self.cmd.cmdUtil.get_init_args(project=self.project, score_class=self.project_class)
        self.cmd.cmdUtil.init(conf)

        project = f"{self.project}"

        # there is no __init__.py
        os.rename(f"{project}/__init__.py", "__init__.py.bak")
        self.assertRaises(TBearsCommandException, check_project, project)
        os.rename("__init__.py.bak", f"{project}/__init__.py")

        # there is no package.json
        os.rename(f"{project}/package.json", "package.json.bak")
        self.assertRaises(TBearsCommandException, check_project, project)

        # wrong package.json file
        self.touch(f"{project}/package.json")
        self.assertRaises(TBearsCommandException, check_project, project)
        os.rename("package.json.bak", f"{project}/package.json")

        # there is no main_module file
        os.rename(f"{project}/{project}.py", f"{project}.py.bak")
        self.assertRaises(TBearsCommandException, check_project, project)

        # working good
        os.rename(f"{project}.py.bak", f"{project}/{project}.py")
        self.assertEqual(check_project(project), 0)

        # do not allow '/' in main_module field
        os.mkdir(f"{project}/modify")
        os.rename(f"{project}/{project}.py", f"{project}/modify/{project}.py")
        with open(f"{project}/package.json", mode='r+') as file:
            package: dict = json.load(file)
            package['main_module'] = f"modify/{project}"
            file.seek(0)
            file.truncate()
            json.dump(package, file)
        self.assertRaises(TBearsCommandException, check_project, project)

        # allow '.' in main_module field
        with open(f"{project}/package.json", mode='r+') as file:
            package: dict = json.load(file)
            package['main_module'] = f"modify.{project}"
            file.seek(0)
            file.truncate()
            json.dump(package, file)
        self.assertEqual(check_project(project), 0)


    def test_clear_args_parsing(self):
        # Parsing test
        cmd = f'clear'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'clear')

        # Too many arguments
        cmd = f'clear arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())


