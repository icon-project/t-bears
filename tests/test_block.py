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
import unittest
import shutil
import time

from tbears.block_manager.block import Block
from tbears.config.tbears_config import tbears_server_config


class TestTBearsBlock(unittest.TestCase):
    DB_PATH = './testdb'
    PREV_BLOCK_HASH = '0123456789abcdef'

    def setUp(self):
        self.block = Block(db_path=self.DB_PATH)

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
        self.block = Block(db_path=self.DB_PATH)
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
        # genesis block
        timestamp = int(time.time() * 10 ** 6)

        self.block.save_block(self.PREV_BLOCK_HASH, tbears_server_config.get('genesis'), timestamp)
        self.block.commit_block(self.PREV_BLOCK_HASH)

        block_by_height = self.block.get_block_by_height(0)
        block_by_hash = self.block.get_block_by_hash(self.PREV_BLOCK_HASH)
        self.assertEqual(block_by_hash, block_by_height)
        self.assertEqual('tbears', block_by_hash.get('version'))
        self.assertEqual('', block_by_hash.get('prev_block_hash'))
        self.assertEqual(timestamp, block_by_hash.get('time_stamp'))
        self.assertEqual(tbears_server_config.get('genesis'), block_by_hash.get('confirmed_transaction_list')[0])
        self.assertEqual(self.PREV_BLOCK_HASH, block_by_hash.get('block_hash'))
        self.assertEqual(0, block_by_hash.get('height'))
        self.assertEqual("", block_by_hash.get('peer_id'))
        self.assertEqual("", block_by_hash.get('signature'))


        # normal block
        tx_list = [
            {'txHash': '01'},
            {'txHash': '02'},
            {'txHash': '03'}
        ]
        timestamp = int(time.time() * 10 ** 6)
        block_hash = self.PREV_BLOCK_HASH + '01'

        self.block.save_block(block_hash, tx_list, timestamp)
        self.block.commit_block(block_hash)

        last_block = self.block.get_last_block()
        block_by_hash = self.block.get_block_by_hash(block_hash)
        self.assertEqual(block_by_hash, last_block)
        self.assertEqual('tbears', block_by_hash.get('version'))
        self.assertEqual(self.PREV_BLOCK_HASH, block_by_hash.get('prev_block_hash'))
        self.assertEqual(timestamp, block_by_hash.get('time_stamp'))
        self.assertEqual(tx_list, block_by_hash.get('confirmed_transaction_list'))
        self.assertEqual(block_hash, block_by_hash.get('block_hash'))
        self.assertEqual(1, block_by_hash.get('height'))
        self.assertNotEqual("", block_by_hash.get('peer_id'))
        self.assertNotEqual("", block_by_hash.get('isgnature'))
