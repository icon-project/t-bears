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

import tbears
from .command import ExitCode, make_SCORE_samples
from .command import init_SCORE
from .command import run_SCORE
from .command import stop_SCORE
from .command import clear_SCORE


def main():
    parser = argparse.ArgumentParser(prog='tbears_cli.py', usage=f"""
==========================
tbears version : v{tbears.__version__}
==========================
tbears commands:
    init <project> <score_class> : Generate files, both <project>.py and package.json in <project> directory. The name of the score class is <score_class>.
    run <project> : Run the score.
    stop : Stop the score.
    clear : Delete the score, both .score and .db directory.
    samples : Create two score samples (sampleCrowdSale, tokentest)
        """)

    parser.add_argument(
        'command',
        nargs='*',
        help='init, run, stop, clear')
    parser.add_argument(
        '--install', dest='install', help='install config json path'
    )
    parser.add_argument(
        '--update', dest='update', help='update config json path'
    )

    args = parser.parse_args()

    if len(args.command) < 1:
        parser.print_help()
        sys.exit(ExitCode.COMMAND_IS_WRONG.value)

    command = args.command[0]

    options = None

    if args.install:
        options = args.install, 'install'
    elif args.update:
        options = args.update, 'update'

    if command == 'init' and len(args.command) == 3:
        result = init_SCORE(args.command[1], args.command[2])
    elif command == 'run' and len(args.command) == 2:
        result, _ = run_SCORE(args.command[1], *options)
    elif command == 'stop':
        result = stop_SCORE()
    elif command == 'clear':
        result = clear_SCORE()
        if result is 1:  # success
            print('Cleared the score successfully.')
    elif command == 'samples':
        result = make_SCORE_samples()
    else:
        parser.print_help()
        result = ExitCode.COMMAND_IS_WRONG.value

    sys.exit(result)
