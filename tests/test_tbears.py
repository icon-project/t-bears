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

import io
import shutil
import unittest

from tbears import *

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))


class TestTBears(unittest.TestCase):
    def setUp(self):
        self.path = './'
        self.compress_test_path = os.path.join(DIRECTORY_PATH, '../')

    @staticmethod
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)

    @staticmethod
    def extract_files_gen(data: 'bytes'):
        with zipfile.ZipFile(io.BytesIO(data)) as memory_zip:
            for zip_info in memory_zip.infolist():
                with memory_zip.open(zip_info) as file:
                    file_path = zip_info.filename
                    root_directory_index = file_path.find("/")
                    path_uncovered_root_directory = file_path[root_directory_index + 1:]
                    file_name_start_index = path_uncovered_root_directory.rfind('/')
                    parent_directory = path_uncovered_root_directory[:file_name_start_index]

                    if path_uncovered_root_directory.find('__MACOSX') != -1:
                        continue
                    if path_uncovered_root_directory.find('__pycache__') != -1:
                        continue
                    if file_name_start_index == len(path_uncovered_root_directory) - 1:
                        # continue when 'file_path' is a directory.
                        continue
                    if path_uncovered_root_directory.find('/.') != -1:
                        # continue when 'file_path' is hidden directory or hidden file.
                        continue
                    parent_directory = path_uncovered_root_directory[:file_name_start_index]
                    if file_name_start_index == -1:
                        yield path_uncovered_root_directory, file, ''
                    else:
                        yield path_uncovered_root_directory, file, parent_directory

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

    def test_compress(self):
        project_name = 'tbear'
        ret1 = compress(project_name, self.compress_test_path)
        self.assertEqual(ExitCode.SUCCEEDED.value, ret1)
        self.assertTrue(os.path.isfile(f'./{project_name}.zip'))

        zip_file_info_gen = self.extract_files_gen(self.read_zipfile_as_byte(f'./{project_name}.zip'))
        compressed_list = [name for name, info, parent_dir in zip_file_info_gen]

        compress_contents = []
        for directory, dirs, filename in os.walk('./sampleTbears'):
            parent_directory_index = directory.rfind('/')
            parent_dir_name = directory[parent_directory_index + 1:]
            for file in filename:
                if parent_dir_name.find("__pycache__") != -1:
                    continue
                if parent_dir_name == 'sampleTbears':
                    compress_contents.append(file)
                else:
                    compress_contents.append(f'{parent_dir_name}/{file}')

        self.assertTrue(compress_contents.sort() == compressed_list.sort())
        os.remove('tbear.zip')


if __name__ == "__main__":
    unittest.main()
