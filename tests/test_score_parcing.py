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

from tbears.tbears_exception import TBearsBaseException, TBearsExceptionCode
from tbears.command.command import Command
from tbears.command.command_util import CommandUtil
from tbears.command.command_score import CommandScore
from tbears.tbears_exception import TBearsCommandException
# from tbears.config.tbears_config import TBearsConfig

from tests.test_command_parcing import TestCommand

class TestCommandScore(TestCommand):
    def setUp(self):
        super().setUp()
        self.tearDownParams = {'proj_unittest': 'dir'}

        # need to be checked from the team
        self.project = 'proj_unittest'
        self.uri = 'http://127.0.0.1:9000/api/v3'
        self.arg_type = 'tbears'
        self.mode = "install"
        self.arg_from = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.to = "cx0000000000000000000000000000000000000000"
        self.keystore = './keystore'
        self.config_path = './deploy'


    # test valid cli argument in this test function, just check whether vaild argument or not
    def test_deploy_args_parcing(self):
        """
        * 삭제 예정(개인 정리용)
        run
        1. 해당 command object가 command를 가지고 있는지 체크
        -> 알맞은 command를 전달받았는 지 check(deploy, clear)
        success:
        deploy, clear 받았을 떄 ok 발생하는 지
        eception:
        알맞지 않은 code 받았을 때 exception 발생시키는 지

        2. config load
        deploy의 경우 config 파일이 필요함, config 파일을 loading 해주는 것이 run에서 진행하는 역할
        -> config file 따로 테스트 진행 필요

        3. command에 해당하는 function 실행(deploy, clear)
        -> command쪽에 모두 빼자
        """

        # parsing
        cmd = f'deploy {self.project} -u {self.uri} -t {self.arg_type} -m {self.mode} -f {self.arg_from} -o {self.to} -k {self.keystore} -c {self.config_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'deploy')
        self.assertEqual(parsed.project, self.project)
        self.assertEqual(parsed.uri, self.uri)
        self.assertEqual(parsed.scoreType, self.arg_type)
        self.assertEqual(parsed.mode, self.mode)
        self.assertEqual(parsed.to, self.to)
        self.assertEqual(parsed.keyStore, self.keystore)
        self.assertEqual(parsed.config, self.config_path)

        # to much argument
        cmd = f'deploy arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        # leack argument
        cmd = f'deploy'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'deploy {self.project} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'deploy {self.project} -t not_supported_type'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'deploy {self.project} -m not_supported_mode'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'deploy {self.project} -t icon tbears to_much -t option args'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        # check the specific case of setting deploy

    # argument checking module(_check_deploy) test, before deploy score,
    # check setisfy requirements
    def test_check_deploy(self):
        """
        전반적인 deploy를 실행시키기 전에 행해지는 모든 문제 체크
        1. project에 해당하는 파일이 존재하는 지 체크
        2. icon인 경우
        - 1)keyStore keystore 옵션 줬는지 확인
          2)keystore file 줬는 지 확인
          3)keystore가 실제 패스에 있는지 확인
          4)password 입력 여부 체크(passward 자체 체크는 안함)
        3. mode check: update인데 to가 None인 경우 여기서 체크
        4. tbears인 경우
        - tbears 상태임에도 불구하고 uri에 값이 있는 경우 에러 체크

        """
        project = 'proj_unittest'
        uri = 'http://127.0.0.1:9000/api/v3'
        to = "cx0000000000000000000000000000000000000000"
        keystore = './keystore'

        # # deploy essential check
        # no project directory
        cmd = f'deploy {project}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # make project directory
        os.mkdir(project)

        # # deploy to icon
        # icon type need keystore option
        cmd = f'deploy {project} -t icon'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # keystore file does not exist
        # sb. 제안: -h에서 keystore file 위치를 입력하라고 명시해주면 좋을 것 같습니다.
        cmd = f'deploy {project} -t icon -k ./no_exist'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # check return password, actually, after check all requirements, _check_deploy return password
        # this function doesn't vaild password value, just return user's input
        cmd = f'deploy {project} -t icon -k {keystore}'
        user_input_password = "1234"
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(CommandScore._check_deploy(vars(parsed),user_input_password), "1234")

        # # deploy to tbears
        # deploy tbears SCORE to remote(doesn't check actual -uri value)
        cmd = f'deploy {project} -t tbears -u http://1.2.3.4:9000/api/v3'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # check return, as tbears mode doesn't accept user's input, return value always None
        cmd = f'deploy {project} -t tbears'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(CommandScore._check_deploy(vars(parsed)), None)

        # update succecced check

        # update mode need to option
        cmd = f'deploy {project} -m update'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # delete project directory
        shutil.rmtree(project)

    def test_deploy(self):
        """
        deploy: Deploy Score on the server
        dict 형태의 config 데이터 받음 -> 여기서 config 데이터의 유효성 검증을 할 필요는 없음
        1. tbears 실행되고 있는지 테스트
        2. _check_deploy를 이용하여 password check -> method 따로 빠져있으니 이것부터 테스트
        3. 각 옵션 체크하여 옵션에 해당하는 값 전달
        1) mode(install, deploy)에 따른 score addr(to) 세팅
        2) scoreType에 따라 payload 세팅
            - icon인 경우 get_icx_sendTransaction_deploy_payload
            - tbears인 경우(else - None or tbears) make_install_json_payload
        3) uri에 맞추어 send
        4) response로 결과를 얻음

        deploy에서 테스트 할 것
        install, update에 따라
        """
        pass

    def test_clear_args_parcing(self):
        # parsing clear
        cmd = f'clear'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'clear')

    def test_clear(self):
        # too much argument
        cmd = f'clear arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

