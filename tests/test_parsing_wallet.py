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

import os
from argparse import ArgumentTypeError, ArgumentError

from tbears.command.command_wallet import CommandWallet
from tbears.tbears_exception import TBearsCommandException
from tests.test_parsing_command import TestCommand
from tests.test_util import TEST_UTIL_DIRECTORY

class TestWalletParsing(TestCommand):
    def setUp(self):
        super().setUp()
        self.tear_down_params = ['unit_test_keystore', 'proj_unittest']
        self.keystore_path = 'unit_test_keystore'
        self.keystore_password = 'qwer1234%'

    #keystore
    def test_keystore_args_parsing(self):
        # Parsing test
        cmd = f'keystore {self.keystore_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'keystore')
        self.assertEqual(parsed.path, self.keystore_path)

        # Not enough argument
        cmd = f'keystore'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Too much argument
        cmd = f'keystore {self.keystore_path} too_much_args'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # File already exist
        self.touch(self.keystore_path)
        cmd = f'keystore {self.keystore_path}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())
        os.remove(self.keystore_path)

    def test_keystore_check_argument(self):
        # Correct command and environment(same file doesn't exists)
        expected_password = self.keystore_password
        cmd = f'keystore {self.keystore_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(CommandWallet._check_keystore(vars(parsed), self.keystore_password), expected_password)

        # File already exist
        cmd = f'keystore {self.keystore_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.touch(self.keystore_path)
        self.assertRaises(TBearsCommandException, CommandWallet._check_keystore, vars(parsed), self.keystore_password)
        os.remove(self.keystore_path)

        # Invalid path: no directory exists
        # 'keystore' command doesn't make directory. so only exist path valid
        cmd = f'keystore ./no_exist_directory/{self.keystore_path}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertRaises(Exception, self.cmd.cmdWallet.keystore, vars(parsed), self.keystore_password)

    #lastblock
    def test_lastblock_args_parsing(self):
        node_uri = 'http://localhost:9999/api/v3'
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')
        cmd = f'lastblock -u {node_uri} -c {config}'
        parsed = self.parser.parse_args(cmd.split())

        self.assertEqual(parsed.command, 'lastblock')
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.config, config)

        # given more arguments.
        cmd = f'lastblock arg1'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # invalid config path
        cmd = f'lastblock -c ./invalid_config_path'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # invalid argument
        cmd = f'lastblock -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    #blockbyhash
    def test_blockbyhash_args_parsing(self):
        block_hash = '0x685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe'
        node_uri = 'http://localhost:9999/api/v3'
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

    def test_validate_block_hash_data(self):
        invalid_prefix = 'ox685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe'
        self.assertRaises(TBearsCommandException, self.cmd.cmdWallet._validate_block_hash, invalid_prefix)

        invalid_length = '0x685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfefdsffds'
        self.assertRaises(TBearsCommandException, self.cmd.cmdWallet._validate_block_hash, invalid_length)

    #blockbyheight
    def test_blockbyheight_args_parsing(self):
        block_height = '0x12'
        node_uri = 'http://localhost:9999/api/v3'
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

    #txresult
    def test_txresult_args_parsing(self):
        tx_hash = '0x685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe'
        node_uri = 'http://localhost:9999/api/v3'
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

        # given invalid tx hash_prefix
        cmd = f'txresult Ox1234'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    #transfer
    def test_transfer_args_parsing(self):
        addr_hx = f"hx{'0'*40}"
        addr_cx = f"cx{'0'*40}"

        node_uri = 'http://localhost:9999/api/v3'
        nid = '0x4'
        value = 0x14
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')
        self.touch(self.keystore_path)
        cmd = f'transfer {addr_hx} {value} -f {addr_hx} -k {self.keystore_path} -n {nid} -u {node_uri} -c {config}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.value, value)
        self.assertEqual(parsed.nid, nid)
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.config, config)

        # 'from' opt and 'to' args should accept both contract address(cx) and eoa address(hx)
        self.assertEqual(parsed.to, addr_hx)
        self.assertEqual(vars(parsed)['from'], addr_hx)

        cmd = f'transfer -f {addr_cx} {addr_cx} {value}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.to, addr_cx)
        self.assertEqual(vars(parsed)['from'], addr_cx)
        os.remove(self.keystore_path)

        # Invalid from address
        invalid_from_addr = 'hx1'
        cmd = f'transfer -f {invalid_from_addr} {addr_cx}  {value}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Invalid to address
        invalid_to_addr = 'hx1'
        cmd = f'transfer {invalid_to_addr} {value}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Too much argument
        cmd = f'transfer {addr_cx} {value} arg3'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Insufficient argument
        cmd = f'transfer {addr_cx}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Insufficient argument
        cmd = f'transfer {value}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Wrong option
        cmd = f'transfer {addr_cx} {value} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Not supported address (only cx or hx prefix are available)
        wrong_addr = f'ax{"0"*40}'
        cmd = f'transfer {wrong_addr} {value}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # Keystore file does not exist
        cmd = f'transfer {addr_cx} {value} -k ./keystore_not_exist'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # config file does not exist
        cmd = 'transfer {to_addr_cx} {value} -c ./config_not_exist'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        #check transfer return password or None(if str)

    #balance
    def test_balance_args_parsing(self):
        addr_hx = f"hx{'0'*40}"
        addr_cx = f"cx{'0'*40}"

        node_uri = 'http://localhost:9000/api/v3'
        invalid_address = f'hx123'
        config = os.path.join(TEST_UTIL_DIRECTORY, 'test_tbears_cli_config.json')

        cmd = f'balance {addr_hx} -u {node_uri} -c {config}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'balance')
        self.assertEqual(parsed.uri, node_uri)

        # 'from' args should accept both contract address(cx) and eoa address(hx)
        self.assertEqual(parsed.address, addr_hx)

        cmd = f'balance {addr_cx} -u {node_uri}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.address, addr_cx)

        # invalid argument tests
        # given more arguments.
        cmd = f'balance arg1 arg2 arg3'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # invalid argument
        cmd = f'balance {addr_cx} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # given invalid address
        cmd = f'balance {invalid_address}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # config file does not exist
        cmd = f'balance {addr_cx} -c ./config_not_exist'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())


    #totalsupply
    def test_totalsupply_args_parsing(self):
        node_uri = 'http://localhost:9999/api/v3'

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

    #soreapi
    def test_scoreapi_args_parsing(self):
        addr_cx = f"cx{'0'*40}"
        addr_hx = f'hx{"0"*40}'

        node_uri = 'http://localhost:9999/api/v3'

        cmd = f'scoreapi {addr_cx} -u {node_uri}'
        parsed = self.parser.parse_args(cmd.split())
        self.assertEqual(parsed.command, 'scoreapi')
        self.assertEqual(parsed.uri, node_uri)
        self.assertEqual(parsed.address, addr_cx)

        # should accept only score address(not eoa address)
        cmd = f'scoreapi {addr_hx}'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # invalid argument tests
        # given more arguments
        cmd = f'scoreapi arg1 arg2 arg3'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

        # invalid argument
        cmd = f'scoreapi {addr_cx} -w wrongoption'
        self.assertRaises(SystemExit, self.parser.parse_args, cmd.split())

    #txbyhash
    def test_txbyhash_args_parsing(self):
        tx_hash = '0x685cf62751cef607271ed7190b6a707405c5b07ec0830156e748c0c2ea4a2cfe'
        node_uri = 'http://localhost:9999/api/v3'
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