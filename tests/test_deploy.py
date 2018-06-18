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
import unittest
import zipfile

from tbears.util.in_memory_zip import InMemoryZip

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))
DEPLOY_TEST_DIRECTORY = os.path.join(DIRECTORY_PATH, 'test_deploy')


def zip_file_name_list(in_memory_zip: 'InMemoryZip') -> list:
    memory_zip = zipfile.ZipFile(in_memory_zip._in_memory)
    return [f'/{file_list.filename}' for file_list in memory_zip.infolist()]


class TestDeploy(unittest.TestCase):

    def test_in_memory_zip(self):
        mz = InMemoryZip()
        mz.zip_in_memory(DEPLOY_TEST_DIRECTORY)
        test_a_path = os.path.join(DEPLOY_TEST_DIRECTORY, 'test_a')
        test_b_path = os.path.join(DEPLOY_TEST_DIRECTORY, 'test_b')
        self.assertTrue(test_a_path in zip_file_name_list(mz))
        self.assertTrue(test_b_path in zip_file_name_list(mz))
