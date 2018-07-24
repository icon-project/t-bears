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
from tbears.command.command_util import CommandUtil
from tbears.command.command_score import CommandScore
from tbears.tbears_exception import TBearsCommandException

# command package do
# 1. parcing user's input date
# 2. run something requested
# so we have to check both, first things to do is check parce correctly
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
        for path, format in self.tearDownParams.items():
            if os.path.isfile(path) or os.path.isdir(path):
                os.remove(path) if format == 'file' else shutil.rmtree(path)




