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

from tbears.command.command import Command


# command package do
# 1. parsing user's input date
# 2. run something requested
# so we have to check both, first things to do is check parse correctly
class TestCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.parser = self.cmd.parser
        self.subparsers = self.cmd.subparsers

    @staticmethod
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)

    def tearDown(self):
        # tear_down_params' key value(file or directory) is always relative path
        for path in self.tear_down_params:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                continue





