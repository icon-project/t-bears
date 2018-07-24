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
from tbears.command.command_wallet import CommandWallet
from tbears.tbears_exception import TBearsCommandException
from tbears.config.tbears_config import FN_CLI_CONF


class ArgsParserTest(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.parser = self.cmd.parser
        self.subparsers = self.cmd.subparsers

    @staticmethod
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)

    def test_init(self):
        project = 'proj_unittest'
        score_class = 'TestClass'

        # working good
        cmd = f'init {project} {score_class}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'init')
        self.assertEqual(parsed.project, project)
        self.assertEqual(parsed.score_class, score_class)

        try:
            CommandUtil._check_init(vars(parsed))
        except:
            exception_raised = True
        else:
            exception_raised = False
        self.assertFalse(exception_raised)

        # not enough argument
        cmd = f'init {project}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # # argument checking module

        # project and score_class are same
        cmd = f'init {project} {project}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandUtil._check_init, vars(parsed))

        # project directory exist
        cmd = f'init {project} {score_class}'
        self.touch(project)
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandUtil._check_init, vars(parsed))
        os.remove(project)

    def test_samples(self):
        # parsing
        cmd = f'samples'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'samples')

        # too much argument
        cmd = f'samples arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_keystore(self):
        path = 'testpath'
        password = 'qwer1234%'

        # parsing
        cmd = f'keystore {path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'keystore')
        self.assertEqual(parsed.path, path)

        # not enough argument
        cmd = f'keystore'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # # argument checking module

        # path file exist
        cmd = f'keystore {path}'
        self.touch(path)
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandWallet._check_keystore, vars(parsed), password)
        os.remove(path)

        # invalid password
        cmd = f'keystore {path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandWallet._check_keystore, vars(parsed), 'qwe')

    def test_start(self):
        address = '0.0.0.0'
        port = 9000
        config_path = './tbears'

        # parsing
        cmd = f'start -a {address} -p {port} -c {config_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'start')
        self.assertEqual(str(parsed.address), address)
        self.assertEqual(parsed.port, port)
        self.assertEqual(parsed.config, config_path)

        # invalid argument
        cmd = f'start wrongargument'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'start --abcd {address}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'start --address wrongip'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'start --port wrongport'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_stop(self):
        # parsing
        cmd = f'stop'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'stop')

        # too much argument
        cmd = f'stop arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_deploy(self):
        project = 'proj_unittest'
        uri = 'http://127.0.0.1:9000/api/v3'
        arg_type = 'tbears'
        mode = "install"
        arg_from = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        to = "cx0000000000000000000000000000000000000000"
        keystore = './keystore_unittest'
        config_path = './deploy'

        # parsing
        cmd = f'deploy {project} -u {uri} -t {arg_type} -m {mode} -f {arg_from} -o {to} -k {keystore} -c {config_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'deploy')
        self.assertEqual(parsed.project, project)
        self.assertEqual(parsed.uri, uri)
        self.assertEqual(parsed.contentType, arg_type)
        self.assertEqual(parsed.mode, mode)
        self.assertEqual(parsed.to, to)
        self.assertEqual(parsed.keyStore, keystore)
        self.assertEqual(parsed.config, config_path)

        # invalid argument
        cmd = f'deploy arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'deploy {project} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'deploy {project} -t not_supported_type'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        cmd = f'deploy {project} -m not_supported_mode'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # # argument checking module

        # no project directory
        cmd = f'deploy {project}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # make project directory
        os.mkdir(project)

        # icon type need keystore option
        cmd = f'deploy {project} -t zip'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # keystore file does not exist
        cmd = f'deploy {project} -t zip -k {keystore}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed), "password")

        # update mode need to option
        cmd = f'deploy {project} -m update'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # deploy tbears SCORE to remote
        cmd = f'deploy {project} -t tbears -u http://1.2.3.4:9000/api/v3'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandScore._check_deploy, vars(parsed))

        # delete project directory
        shutil.rmtree(project)

    def test_clear(self):
        # parsing
        cmd = f'clear'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'clear')

        # too much argument
        cmd = f'clear arg1 arg2'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_transfer(self):
        arg_from = f"hx{'0'*40}"
        to = f"hx1{'0'*39}"
        value = 1e18
        arg_type = 'dummy'
        keystore = 'keystore_path'
        node_uri = 'http://localhost:9000/api/v3'
        invalid_address = f'hx123'
        config = FN_CLI_CONF
        invalid_coin_value = 1.1
        nid = '0x123456'

        cmd = f'transfer {to} {value} -k {keystore} -u {node_uri} -c {config} -f {arg_from} -n {nid}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'transfer')
        self.assertEqual(parsed.to, to)
        self.assertEqual(parsed.value, value)
        self.assertEqual(parsed.keyStore, keystore)
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.config, config)
        dict_parsed = vars(parsed) # from is keyword in python, can't use parsed.from
        self.assertEqual(dict_parsed['from'], arg_from)
        self.assertEqual(parsed.nid, nid)

        # invalid argument tests
        # given more arguments.
        cmd = f'transfer arg1 arg2 arg3'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        # invalid argument
        cmd = f'transfer {to} {value} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # given invalid value to arguments.
        cmd = f'transfer {invalid_address} {value}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandWallet._check_transfer, vars(parsed))
        cmd = f'transfer {to} {invalid_coin_value}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandWallet._check_transfer, vars(parsed))
        # given nonexistent keystore file path.
        cmd = f'transfer {to} {value} -k {keystore}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandWallet._check_transfer, vars(parsed))

    def test_result(self):
        tx_hash = '0x685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe'
        node_uri = 'http://localhost:9000/api/v3'
        config = FN_CLI_CONF
        cmd = f'txresult {tx_hash} -u {node_uri} -c {config}'
        invalid_hash = '0x1'
        parsed = self.parser.parse_args(cmd.split())

        self.assertEqual(parsed.command, 'txresult')
        self.assertEqual(parsed.hash, tx_hash)
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.config, config)

        # given more arguments.
        cmd = f'txresult {tx_hash} arg1'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # given invalid tx hash
        cmd = f'txresult {invalid_hash}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(TBearsCommandException, CommandWallet._check_txresult, vars(parsed))
