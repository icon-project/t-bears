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
from tests.test_util import TEST_UTIL_DIRECTORY


class ArgsParserTest(unittest.TestCase):
    def setUp(self):
        self.cmd = Command()
        self.parser = self.cmd.parser
        self.subparsers = self.cmd.subparsers
        self.project = 'proj_unittest'

    def tearDown(self):
        if os.path.exists(self.project):
            if os.path.isdir(self.project):
                shutil.rmtree(self.project)
            else:
                os.remove(self.project)

    @staticmethod
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)

    def test_result(self):
        tx_hash = '0x685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe'
        node_uri = 'http://localhost:9000/api/v3'
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')
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
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_balance(self):
        arg_from = f"hx{'0'*40}"
        node_uri = 'http://localhost:9000/api/v3'
        invalid_address = f'hx123'
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')

        cmd = f'balance {arg_from} -u {node_uri}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'balance')
        self.assertEqual(parsed.address, arg_from)
        self.assertEqual(parsed.uri, node_uri)

        # invalid argument tests
        # given more arguments.
        cmd = f'balance arg1 arg2 arg3'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        # invalid argument
        cmd = f'balance {arg_from} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # given invalid value to arguments.
        cmd = f'balance {invalid_address}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_totalsup(self):
        node_uri = 'http://localhost:9000/api/v3'

        cmd = f'totalsupply -u {node_uri}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'totalsupply')
        self.assertEqual(parsed.uri, node_uri)

        # invalid argument tests
        # given more arguments.
        cmd = f'totalsupply arg1 arg2 arg3'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        # invalid argument
        cmd = f'totalsupply -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_scoreapi(self):
        score_address = f"cx{'0'*40}"
        node_uri = 'http://localhost:9000/api/v3'
        invalid_score_address = f'hx{"0"*40}'

        cmd = f'scoreapi {score_address} -u {node_uri}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'scoreapi')
        self.assertEqual(parsed.uri, node_uri)

        # invalid argument tests
        # given more arguments.
        cmd = f'scoreapi arg1 arg2 arg3'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        # invalid argument
        cmd = f'scoreapi {score_address} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # given invalid value to arguments.
        cmd = f'scoreapi {invalid_score_address}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_tx_by_hash(self):
        tx_hash = '0x685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe'
        node_uri = 'http://localhost:9000/api/v3'
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')
        cmd = f'txbyhash {tx_hash} -u {node_uri} -c {config}'
        invalid_hash = '0x1'
        parsed = self.parser.parse_args(cmd.split())

        self.assertEqual(parsed.command, 'txbyhash')
        self.assertEqual(parsed.hash, tx_hash)
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.config, config)

        # given more arguments.
        cmd = f'txbyhash {tx_hash} arg1'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # given invalid tx hash
        cmd = f'txbyhash {invalid_hash}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_block_by_hash(self):
        block_hash = '0x685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe'
        node_uri = 'http://localhost:9000/api/v3'
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')
        invalid_hash = '0x1'

        cmd = f'blockbyhash {block_hash} -u {node_uri} -c {config}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'blockbyhash')
        self.assertEqual(parsed.hash, block_hash)
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.config, config)

        # given more arguments.
        cmd = f'blockbyhash {block_hash} arg1'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # invalid argument
        cmd = f'totalsupply -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # given invalid tx hash
        cmd = f'blockbyhash {invalid_hash}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_block_by_height(self):
        block_height = '0x12'
        node_uri = 'http://localhost:9000/api/v3'
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')
        cmd = f'blockbyheight {block_height} -u {node_uri} -c {config}'
        parsed = self.parser.parse_args(cmd.split())

        self.assertEqual(parsed.command, 'blockbyheight')
        self.assertEqual(parsed.height, block_height)
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.config, config)

        # given more arguments.
        cmd = f'blockbyheight {block_height} arg1'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # invalid argument
        cmd = f'blockbyheight -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    def test_last_block(self):
        node_uri = 'http://localhost:9000/api/v3'
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')
        cmd = f'lastblock -u {node_uri} -c {config}'
        parsed = self.parser.parse_args(cmd.split())

        self.assertEqual(parsed.command, 'lastblock')
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.config, config)

        # given more arguments.
        cmd = f'lastblock arg1'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # invalid argument
        cmd = f'lastblock -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

