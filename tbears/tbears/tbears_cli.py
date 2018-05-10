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

import argparse
import sys

from .command import *


def main():
    parser = argparse.ArgumentParser(prog='tbears_cli.py', usage="""
    ==========================
    tbears version : 0.0.1
    ==========================
        tbears commands:
            init <project> <score_class> : generate <project>.py and package.json in <project> directory.
            your score class name will be <score_class>
            run <project> : run your score project.
            stop : stop your score.
        """)

    parser.add_argument('command', nargs='*', help='init, test, run, deploy, compress, install')

    args = parser.parse_args()

    if len(args.command) < 1:
        parser.print_help()
        sys.exit(ExitCode.COMMAND_IS_WRONG.value)

    command = args.command[0]

    result = None

    if command == 'init' and len(args.command) == 3:
        result = init(args.command[1], args.command[2])
    elif command == 'run' and len(args.command) == 2:
        result = run(args.command[1])
    elif command == 'stop':
        result = stop()
    else:
        parser.print_help()
        result = ExitCode.COMMAND_IS_WRONG.value

    sys.exit(result)
