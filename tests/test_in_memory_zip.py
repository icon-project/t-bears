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
import hashlib
import os
import shutil
import unittest
import zipfile

from tbears.util.in_memory_zip import InMemoryZip
from tests.test_util import IN_MEMORY_ZIP_TEST_DIRECTORY


def zip_file_name_list(in_memory_zip: 'InMemoryZip') -> list:
    memory_zip = zipfile.ZipFile(in_memory_zip._in_memory)
    return [f'/{file_list.filename}' for file_list in memory_zip.infolist()]


class TestInMemoryZip(unittest.TestCase):

    def test_in_memory_zip(self):
        mz = InMemoryZip()
        mz.zip_in_memory(IN_MEMORY_ZIP_TEST_DIRECTORY)

        test_a_path = os.path.join(IN_MEMORY_ZIP_TEST_DIRECTORY, 'test_a')
        test_b_path = os.path.join(IN_MEMORY_ZIP_TEST_DIRECTORY, 'test_b')
        self.assertTrue(test_a_path in zip_file_name_list(mz))
        self.assertTrue(test_b_path in zip_file_name_list(mz))

        in_memory_zip_contents = []
        real_contents = []

        with zipfile.ZipFile(mz._in_memory) as mzf:
            mzf.extractall('test_in_memory_zip')

        with zipfile.ZipFile('testt.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(IN_MEMORY_ZIP_TEST_DIRECTORY):
                for file in files:
                    zf.write(os.path.join(root, file))

        with open('testt.zip', mode='rb') as zf:
            zip_content = zf.read()

        self.assertTrue(zip_content == mz._in_memory.getvalue())

        for root, dirs, files in os.walk('test_in_memory_zip'):
            for file in files:
                with open(f'{root}/{file}', mode='rb') as f:
                    in_memory_zip_contents.append(hashlib.sha3_256(f.read()).digest())

        for root, dirs, files in os.walk(IN_MEMORY_ZIP_TEST_DIRECTORY):
            for file in files:
                with open(f'{root}/{file}', mode='rb') as f:
                    real_contents.append(hashlib.sha3_256(f.read()).digest())

        self.assertEqual(in_memory_zip_contents, real_contents)

        if os.path.exists("test_in_memory_zip"):
            shutil.rmtree('test_in_memory_zip')

        if os.path.exists('testt.zip'):
            os.remove('testt.zip')
