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

from .command import ExitCode
from .command import init_SCORE
from .command import run_SCORE
from .command import stop_SCORE
from .command import clear_SCORE


def main():
    parser = argparse.ArgumentParser(prog='tbears_cli.py', usage="""
    ==========================
    tbears version : 0.0.1
    ==========================
        tbears commands:
            init <project> <score_class> : Generate files, both <project>.py and package.json in <project> directory. The name of the score class is <score_class>.
            run <project> : Run the score.
            stop : Stop the score.
            clear : Delete the score, both .score and .db directory.
        """)

    parser.add_argument(
        'command',
        nargs='*',
        help='init, run, stop, clear')

    args = parser.parse_args()

    if len(args.command) < 1:
        parser.print_help()
        sys.exit(ExitCode.COMMAND_IS_WRONG.value)

    command = args.command[0]

    if command == 'init' and len(args.command) == 3:
        result = init_SCORE(args.command[1], args.command[2])
    elif command == 'run' and len(args.command) == 2:
        result, _ = run_SCORE(args.command[1])
    elif command == 'stop':
        result = stop_SCORE()
    elif command == 'clear':
        result = clear_SCORE()
        if result is 1:  # success
            print('Cleared the score successfully.')
    else:
        parser.print_help()
        result = ExitCode.COMMAND_IS_WRONG.value

    sys.exit(result)
