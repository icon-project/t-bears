# -*- coding: utf-8 -*-
# Copyright 2017-2018 ICON Foundation
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
import json
import os
import shutil
import time
import unittest

from tbears.block_manager.block import Block
from tbears.block_manager.block_manager import BlockManager
from tbears.config.tbears_config import tbears_server_config


class TestTBearsBlock(unittest.TestCase):
    DB_PATH = './testdb'
    PREV_BLOCK_HASH = '0123456789abcdef'

    def setUp(self):
        config = tbears_server_config
        config['stateDbRootPath'] = self.DB_PATH
        self.block_manager = BlockManager(config)
        self.block = self.block_manager.block

    def tearDown(self):
        try:
            if os.path.exists(self.DB_PATH):
                shutil.rmtree(self.DB_PATH)
        except:
            pass

    def test_property(self):
        # block_height
        block_height = self.block.block_height
        self.assertEqual(-1, block_height)
        self.block.increase_block_height()
        self.assertEqual(block_height + 1, self.block.block_height)

        # prev_block_hash
        self.assertEqual(None, self.block.prev_block_hash)
        self.block.set_prev_block_hash(self.PREV_BLOCK_HASH)
        self.assertEqual(self.PREV_BLOCK_HASH, self.block.prev_block_hash)

        # reload Block info
        self.block.db.close()
        self.block = Block(db_path=f"{self.DB_PATH}/tbears/")
        self.assertEqual(block_height + 1, self.block.block_height)
        self.assertEqual(self.PREV_BLOCK_HASH, self.block.prev_block_hash)

    def test_commit_block(self):
        block_height = self.block.block_height
        self.block.commit_block(self.PREV_BLOCK_HASH)
        self.assertEqual(block_height + 1, self.block.block_height)
        self.assertEqual(self.PREV_BLOCK_HASH, self.block.prev_block_hash)

    def test_transactions(self):
        tx_list = [
            {'txHash': '01'},
            {'txHash': '02'},
            {'txHash': '03'}
        ]
        self.block.save_transactions(tx_list, self.PREV_BLOCK_HASH)

        for i, v in enumerate(tx_list):
            tx = self.block.get_transaction(v.get('txHash'))
            self.assertEqual(v, tx.get('transaction'))
            self.assertEqual(hex(i), tx.get('tx_index'))
            self.assertEqual(hex(self.block.block_height + 1), tx.get('block_height'))
            self.assertEqual(f'0x{self.PREV_BLOCK_HASH}', tx.get('block_hash'))

    def test_txresult(self):
        tx_result = {'key': 'value'}
        tx_hash = '0123'

        self.block.save_txresult(tx_hash, tx_result)
        result = self.block.get_txresult(tx_hash)
        self.assertEqual(tx_result, json.loads(result))

        tx_list = [
            {'txHash': '01'},
            {'txHash': '02'},
            {'txHash': '03'}
        ]
        tx_results = [
            {'txHash': '01', 'value': 1, 'blockHash': "test_block_hash"},
            {'txHash': '02', 'value': 2, 'blockHash': "test_block_hash"},
            {'txHash': '03', 'value': 3, 'blockHash': "test_block_hash"},
        ]

        new_block_hash = "new_block_hash"
        self.block.save_txresults(tx_results, new_block_hash)
        for i, v in enumerate(tx_list):
            result = self.block.get_txresult(v.get('txHash'))
            result_dict = json.loads(result)
            self.assertEqual(v.get('txHash'), result_dict.get('txHash'))
            self.assertEqual(tx_results[i].get('value'), result_dict.get('value'))
            self.assertEqual(new_block_hash, result_dict.get('blockHash'))

    def test_block(self):
        test_address = tbears_server_config['genesis']['accounts'][2]['address']
        # genesis block
        timestamp = int(time.time() * 10 ** 6)
        invoke_response = {
            "txResults": {},
            "stateRootHash": "1"*64,
            "hash": self.PREV_BLOCK_HASH
        }

        self.block_manager._prep_manager.get_prev_block_contributors_info()
        block = self.block_manager._make_block_data(self.PREV_BLOCK_HASH, tbears_server_config['genesis'],
                                                    timestamp, invoke_response)
        self.block.save_block(block)
        self.block.commit_block(self.PREV_BLOCK_HASH)

        self._check_block(self.PREV_BLOCK_HASH, '', tbears_server_config['genesis'], timestamp, 0,
                          test_address, test_address, is_genesis=True)

        # normal block
        tx_list = [
            {'txHash': '01'},
            {'txHash': '02'},
            {'txHash': '03'}
        ]
        timestamp = int(time.time() * 10 ** 6)
        block_hash = self.PREV_BLOCK_HASH + '01'
        invoke_response = {
            "txResults": [],
            "stateRootHash": "0"*64,
            "hash": block_hash,
        }

        block = self.block_manager._make_block_data(block_hash, tx_list, timestamp, invoke_response)
        self.block.save_block(block)
        self.block.commit_block(block_hash)

        self._check_block(block_hash, self.PREV_BLOCK_HASH, tx_list, timestamp, 1, test_address, test_address)

        tx_list = [
            {'txHash': '011'},
            {'txHash': '022'},
            {'txHash': '033'}
        ]
        timestamp = int(time.time() * 10 ** 6)
        block_hash = self.PREV_BLOCK_HASH + '02'
        invoke_response = {
            "txResults": [],
            "stateRootHash": "0" * 64,
            "hash": block_hash,
        }

        block = self.block_manager._make_block_data(block_hash, tx_list, timestamp, invoke_response)
        self.block.save_block(block)
        self.block.commit_block(block_hash)

    def _check_block(self, block_hash, prev_hash, tx_list, timestamp, height, leader, next_leader, is_genesis=False):
        last_block = self.block.get_last_block()
        block_by_hash = self.block.get_block_by_hash(block_hash)
        self.assertEqual(block_by_hash, last_block)
        self.assertEqual('tbears', block_by_hash.get('version'))
        self.assertEqual(prev_hash, block_by_hash.get('prevHash'))
        self.assertEqual(timestamp, block_by_hash.get('timestamp'))
        self.assertEqual(block_hash, block_by_hash.get('hash'))
        self.assertEqual(height, block_by_hash.get('height'))
        self.assertEqual(leader, block_by_hash.get('leader'))
        self.assertEqual(next_leader, block_by_hash.get('nextLeader'))
        self.assertIn("transactionsHash", block_by_hash)
        self.assertIn("receiptsHash", block_by_hash)
        self.assertIn("repsHash", block_by_hash)
        self.assertIn("nextRepsHash", block_by_hash)
        self.assertIn("leaderVotesHash", block_by_hash)
        self.assertIn("prevVotesHash", block_by_hash)
        self.assertIn("logsBloom", block_by_hash)
        self.assertIn("leaderVotes", block_by_hash)
        self.assertIn("prevVotes", block_by_hash)
        if is_genesis:
            self.assertEqual(tx_list, block_by_hash.get('transactions')[0])
            self.assertEqual("", block_by_hash.get('signature'))
        else:
            self.assertEqual(tx_list, block_by_hash.get('transactions'))
            self.assertEqual("tbears_block_manager_does_not_support_block_signature", block_by_hash.get('signature'))
