# -*- coding: utf-8 -*-
# Copyright 2018 ICON Foundation
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
import sys
import argparse

from typing import Optional

from tbears.command.command_wallet import CommandWallet
from tbears.tbears_exception import TBearsBaseException, TBearsExceptionCode
from tbears.command.command_server import CommandServer
from tbears.command.command_score import CommandScore
from tbears.command.command_util import CommandUtil
from tbears.util import get_tbears_version


class TbearsParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f'error: {message}\n\n')
        self.print_help()
        sys.exit(2)


class Command(object):
    def __init__(self):
        self.version = get_tbears_version()
        self._create_parser()
        self.cmdServer = CommandServer(self.subparsers)
        self.cmdScore = CommandScore(self.subparsers)
        self.cmdUtil = CommandUtil(self.subparsers)
        self.cmdWallet = CommandWallet(self.subparsers)

    def _create_parser(self):
        parser = TbearsParser(prog='tbears', description=f'tbears v{self.version} arguments')
        parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
        subparsers = parser.add_subparsers(title='Available commands', metavar='command',
                                           description=f'If you want to see help message of commands, '
                                                       f'use "tbears command -h"')
        subparsers.required = True
        subparsers.dest = 'command'

        self.parser = parser
        self.subparsers = subparsers

        return parser

    def run(self, sys_args) -> Optional:
        # sys_args is list of commands splitted by space
        # e.g. tbears deploy project -k keystore => ['deploy', 'project', '-k', 'keystore']
        try:
            # parse_args return the populated namespace
            # e.g. Namespace (command='deploy', config=None, keyStore='keystore' ...)
            args = self.parser.parse_args(args=sys_args)
            if self.cmdServer.check_command(args.command):
                result = self.cmdServer.run(args)
            elif self.cmdScore.check_command(args.command):
                result = self.cmdScore.run(args)
            elif self.cmdUtil.check_command(args.command):
                result = self.cmdUtil.run(args)
            elif self.cmdWallet.check_command(args.command):
                result = self.cmdWallet.run(args)
        except TBearsBaseException as e:
            print(f"{e}")
            return e.code.value
        except Exception as e:
            print(f"Exception: {e}")
            return TBearsExceptionCode.COMMAND_ERROR.value
        else:
            return result
