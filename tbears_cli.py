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

from tbears import *
from tbears.util import check_required_args


def main():
    parser = argparse.ArgumentParser(prog='tbears_cli.py', usage="""
    ==========================
    tbears sample: ~~~~~~~~~~~
    ==========================
        tbears commands:
            init <project>
            test <project>
            run <project>
            deploy <project> -n testnet | mainnet
            compress <project> -p <SCORE directory path>
        """)

    parser.add_argument('command', nargs='*', help='init, test, run, deploy, compress, install')
    parser.add_argument('-n', help='mainnet | testnet', dest='network', type=str, default='testnet')
    parser.add_argument('-p', help='path of SCORE directory', dest='path', type=str)

    args = parser.parse_args()

    command = args.command[0]

    result = None

    if len(args.command) < 2:
        parser.print_help()
        sys.exit(ExitCode.COMMAND_IS_WRONG.value)

    if command == 'init' and len(args.command) == 3:
        result = init(args.command[1], args.command[2])
    elif command == 'test':
        result = test()
    elif command == 'run':
        result = run()
    elif command == 'deploy':
        result = deploy(args.network)
    elif command == 'compress' and check_required_args(path=args.path):
        result = compress(project=args.command[1], score_path=args.path)
    else:
        parser.print_help()
        result = ExitCode.COMMAND_IS_WRONG.value

    sys.exit(result)


if __name__ == '__main__':
    main()
