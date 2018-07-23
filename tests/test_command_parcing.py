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

"""
* 삭제 예정(개인 정리용)
command.py의 각 메서드별 역할, 하는 일
Command class는 파싱에 필요한 모든클래스를 세팅한다. 
_create_parser는 가장 기본이 되는 ArgumentParser를 생성하고, subparsers를 생성한다,
여기서는 Command 클래스에 일차적으로 parser, subparsers을 초기화 한다.
테스트 해볼 수 있는 부분: 우선순위 낮음

run method는 사용자가 프롬프트창에서 입력한 문자를 list형태로 받아(받았다고 가정)
parser를 이용하여 parsing, 입력한 명령어에 해당하는 command를 실행시킨다.
또한 각 command에서 exception발생시 에러에 대한 메시지를 출력해준다.
체크 사항
사실상 체크할 부분이 많지 않다. 파싱은 다른 외부 함수가 처리하고, exception에 대한
"""

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




