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
import os
import getpass
from ipaddress import ip_address

from iconservice.logger import Logger
from iconservice.logger.logger import LogLevel
import tbears
from tbears.command import ExitCode
from tbears.command.CommandServer import CommandServer
from tbears.command.CommandScore import CommandScore


def create_parser():
    parser = argparse.ArgumentParser(prog='tbears', description=f'tbears v{tbears.__version__} arguments');
    parser.add_argument('-d', '--debug', help='Debug mode', action='store_true')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description=f'If you want to see help message of subcommands, '
                                                   f'use "tbears subcommand -h"')

    add_init_parser(subparsers)
    add_start_parser(subparsers)
    add_stop_parser(subparsers)
    add_deploy_parser(subparsers)
    add_clear_parser(subparsers)
    add_sample_parser(subparsers)

    return parser


def add_init_parser(subparsers) -> None:
    parser_init = subparsers.add_parser('init', help='Initialize tbears project',
                                        description='Initialize SCORE development environment.\n'
                                                    'Generate <project>.py and package.json in <project> directory. '
                                                    'The name of the score class is <score_class>.')
    parser_init.add_argument('project', help='Project name')
    parser_init.add_argument('score_class', help='SCORE class name')
    parser_init.set_defaults(func=command_init)


def command_init(args):
    result = CommandServer.init(project=args.project, score_class=args.score_class)
    if result is ExitCode.SUCCEEDED:
        print(f'Initialize the SCORE {args.score_class} successfully in {args.project}.')
    else:
        print(f"Can't initialize the SCORE {args.score_class} in {args.project}.")

    return result.value


def add_start_parser(subparsers) -> None:
    parser_start = subparsers.add_parser('start', help='Start tbears serivce',
                                         description='Start tbears service')
    parser_start.add_argument('-a', '--address', help='Address to host on (default: 0.0.0.0)', type=ip_address)
    parser_start.add_argument('-p', '--port', help='Listen port (default: 9000)', type=int)
    parser_start.add_argument('-c', '--config', help='tbears configuration file path (default: ./tbears.json)')
    parser_start.set_defaults(func=command_start)


def command_start(args):
    if CommandServer.is_server_running():
        print(f"Tbears service was started already")
        return

    CommandServer.start(host=str(args.address), port=args.port, conf_file=args.config)

    return ExitCode.SUCCEEDED.value


def add_stop_parser(subparsers) -> None:
    parser_stop = subparsers.add_parser('stop', help='Stop tbears service',
                                        description='Stop all running SCORE and tbears service')
    parser_stop.set_defaults(func=command_stop)


def command_stop(_args):
    result = CommandServer.stop()
    if result is ExitCode.SUCCEEDED:
        print(f'Stopped tbear service successfully')
    else:
        print(f"Can't stop tbears service")
    return result.value


def add_deploy_parser(subparsers):
    parser_deploy = subparsers.add_parser('deploy', help='Deploy the SCORE',
                                          description='Deploy the SCORE in project')
    parser_deploy.add_argument('project', help='Project name')
    parser_deploy.add_argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                               dest='uri')
    parser_deploy.add_argument('-t', '--type', help='Deploy SCORE type ("tbears" or "icon". default: tbears',
                               choices=['tbears', 'icon'], dest='scoreType')
    parser_deploy.add_argument('-m', '--mode', help='Deploy mode ("install" or "update". default: update',
                               choices=['install', 'update'], dest='mode')
    parser_deploy.add_argument('-f', '--from', help='From address. i.e. SCORE owner address', dest='from')
    parser_deploy.add_argument('-o', '--to', help='To address. i.e. SCORE address', dest='to')
    parser_deploy.add_argument('-k', '--key-store', help='Key store file for SCORE owner', dest='keyStore')
    parser_deploy.add_argument('-c', '--config', help='deploy config path (default: ./deploy.json')
    parser_deploy.set_defaults(func=command_deploy)


def command_deploy(args):
    server = CommandServer.is_server_running()
    if not server:
        print(f'Start tbears server first')
        return ExitCode.COMMAND_IS_WRONG.value

    # check input argument
    if not os.path.isdir(args.project):
        print(f'There is no project directory.({args.project})')
        return ExitCode.COMMAND_IS_WRONG.value

    password = None
    if args.scoreType == 'icon':
        if args.keyStore is None:
            print(f'If you want to deploy SCORE to ICON node, set --key-store option')
            return ExitCode.COMMAND_IS_WRONG.value
        else:
            if not os.path.exists(args.keyStore):
                print(f'There is not keystore file {args.keyStore}')
                return ExitCode.COMMAND_IS_WRONG.value
            password = getpass.getpass("input your key store password: ")

    if args.mode == 'update' and not args.to:
        print(f'If you want to update SCORE, set --to option')
        return ExitCode.COMMAND_IS_WRONG.value

    # get deploy configuration
    conf = CommandScore.get_conf(args.config or './deploy.json')
    CommandScore.combine_conf(conf, vars(args))

    if conf['scoreType'] == 'tbears':
        uri: str = conf.get('uri', None)
        if uri and uri.find('127.0.0.1') == -1 and uri.find('localhost') == -1:
            print(f"Can't deploy tbears SCORE to remote")
            return ExitCode.COMMAND_IS_WRONG.value

    result, _ = CommandScore.deploy(project=args.project, conf=conf, password=password)

    return result.value


def add_clear_parser(subparsers):
    parser_clear = subparsers.add_parser('clear', help='Clear all SCORE deployed on tbears service',
                                         description='Clear all SCORE deployed on local tbears service')
    parser_clear.set_defaults(func=command_clear)


def command_clear(_args):
    server = CommandServer.is_server_running()
    if server:
        answer = input(f'You must stop tbears service to clear SCORE. Do you want to stop tbears service? (Y/n)')
        if answer == 'n':
            return ExitCode.COMMAND_IS_WRONG.value
        else:
            CommandServer.stop()

    result = CommandScore.clear()
    if result is ExitCode.SUCCEEDED:  # success
        print('Cleared the SCORE successfully.')
    else:
        print("There is no deployed SCORE")

    return result


def add_sample_parser(subparsers):
    parser_samples = subparsers.add_parser('samples',
                                           help='Create two SCORE samples (sample_crowd_sale, sample_token)',
                                           description='Create two SCORE samples (sample_crowd_sale, sample_token)')
    parser_samples.set_defaults(func=command_samples)


def command_samples(_args):
    result = CommandServer.make_samples()
    if result is ExitCode.SUCCEEDED:  # success
        print('Made samples successfully. (sample_crowd_sale, sample_token)')

    return result


def main():
    # create argument parser
    parser = create_parser()

    # parse argument
    args = parser.parse_args(sys.argv[1:])

    tbears_logger = Logger()
    if args.debug:
        tbears_logger.set_log_level(LogLevel.DEBUG)
    else:
        tbears_logger.set_log_level(LogLevel.WARNING)

    # work with parsed argument
    result = args.func(args)

    sys.exit(result)
