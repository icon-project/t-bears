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
from tbears.tbears.command import *

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))


class TestTBears(unittest.TestCase):
    def setUp(self):
        self.path = './'

    @staticmethod
    def read_zipfile_as_byte(archive_path: 'str') -> 'bytes':
        with open(archive_path, 'rb') as f:
            byte_data = f.read()
            return byte_data

    def test_init(self):
        # Case when user entered a exists directory path for project init.
        os.mkdir('./tmp')
        ret1 = init('tmp', "TempScore")
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value, ret1)
        os.rmdir('./tmp')

        # Case when user entered a exists file path for project init.
        TestTBears.touch('./tmpfile')
        ret2 = init('./tmpfile', 'TestScore')
        self.assertEqual(ExitCode.PROJECT_PATH_IS_NOT_EMPTY_DIRECTORY.value, ret2)
        os.remove('./tmpfile')

        # Case when user entered a appropriate path for project init.
        project_name = 'tbear_test'
        ret3 = init(project_name, "TestScore")
        self.assertEqual(ExitCode.SUCCEEDED.value, ret3)
        with open(f'{project_name}/package.json', mode='r') as package_contents:
            package_json = json.loads(package_contents.read())
        main = package_json['main_file']
        self.assertEqual(project_name, main)
        shutil.rmtree(project_name)


if __name__ == "__main__":
    unittest.main()
