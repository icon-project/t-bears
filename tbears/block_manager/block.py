# Copyright 2018 ICON Foundation
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
import json
import uuid
from typing import Union, Optional

from iconcommons import IconConfig
from iconcommons.logger import Logger
from iconservice.icon_constant import DATA_BYTE_ORDER, DEFAULT_BYTE_SIZE

from tbears.block_manager.tbears_db import TbearsDB

LOG_BLOCK = 'BLOCK'


class DbPrefix(object):
    TX = b'tx|'
    TXRESULT = b'txResult|'
    BLOCK = b'block|'
    BLOCK_INDEX = b'blockIndex|'
    BLOCK_HEIGHT = b'blockHeight|'
    PREV_BLOCK = b'prevBlockHash|'


class Block(object):
    def __init__(self, db_path: str):
        self._db: TbearsDB = TbearsDB(TbearsDB.make_db(db_path))
        self._block_height = -1
        self._prev_block_hash = None
        self._peer_id = str(uuid.uuid1())

        self.load_block_info()
        
    @property
    def db(self):
        return self._db

    @property
    def peer_id(self):
        return self._peer_id
    
    def load_block_info(self):
        """
        Load block height and previous block hash from DB
        :return:
        """
        byte_block_height = self.db.get(DbPrefix.BLOCK_HEIGHT)
        byte_prev_block_hash = self.db.get(DbPrefix.PREV_BLOCK)

        if byte_block_height is not None:
            block_height = byte_block_height.decode()
            self._block_height = int(block_height)
        if byte_prev_block_hash is not None:
            self._prev_block_hash = bytes.hex(byte_prev_block_hash)

    @property
    def block_height(self):
        return self._block_height

    def increase_block_height(self):
        self._block_height += 1
        self.db.put(DbPrefix.BLOCK_HEIGHT, str(self._block_height).encode())

    @property
    def prev_block_hash(self):
        return self._prev_block_hash

    def set_prev_block_hash(self, block_hash: str):
        self._prev_block_hash = block_hash
        self.db.put(DbPrefix.PREV_BLOCK, bytes.fromhex(self._prev_block_hash))

    def commit_block(self, prev_block_hash: str):
        """
        Update block height and previous block hash
        :param prev_block_hash:
        :return:
        """
        self.increase_block_height()
        self.set_prev_block_hash(block_hash=prev_block_hash)

    def save_transactions(self, tx_list: list, block_hash: str):
        """
        Save transactions to DB
        :param tx_list: transaction list
        :param block_hash: block hash
        :return:
        """
        Logger.debug(f'save_transactions: {tx_list}', LOG_BLOCK)
        if len(tx_list) == 0:
            return

        # write transaction with batch
        with self.db.create_write_batch() as wb:
            for i, tx in enumerate(tx_list):
                key, value = self._get_tx_value(i, tx['txHash'], tx, block_hash, self.block_height + 1)
                self.db.write_batch(write_batch=wb, key=key, value=value)

    @staticmethod
    def _get_tx_value(index: int, k: str, v: dict, block_hash: str, block_height: int):
        """
        Get transaction key, value bytes data for DB writing
        :param index: transaction index
        :param k: key
        :param v: value
        :param block_hash: block hash
        :param block_height: block height
        :return:
        """
        key = DbPrefix.TX + bytes.fromhex(k)

        value = {
            'transaction': v,
            'tx_index': hex(index),
            'block_height': hex(block_height),
            'block_hash': f'0x{block_hash}'
        }

        return key, json.dumps(value).encode()

    def save_txresult(self, tx_hash: str, tx_result):
        """
        Save transaction result to DB
        :param tx_hash: transaction hash
        :param tx_result: transaction result
        :return:
        """
        self.db.put(DbPrefix.TXRESULT + bytes.fromhex(tx_hash), json.dumps(tx_result).encode())

    def save_txresults(self, tx_results: list):
        """
        Save transaction results to DB
        :param tx_results: transaction result dictionary
        :return:
        """
        Logger.debug(f'save_txresults:{tx_results}', LOG_BLOCK)

        # write transaction result with batch
        with self.db.create_write_batch() as wb:
            for tx_result in tx_results:
                # key from transaction hash
                key = DbPrefix.TXRESULT + bytes.fromhex(tx_result.get('txHash'))

                # get value from transaction result
                value = json.dumps(tx_result).encode()

                self.db.write_batch(write_batch=wb, key=key, value=value)

    def save_txresults_legacy(self, tx_list: list, results: dict):
        """
        Save transaction results to DB
        :param tx_list: transaction list
        :param results: transaction result dictionary
        :return:
        """
        Logger.debug(f'save_txresult:{results}', LOG_BLOCK)
        if len(tx_list) == 0:
            return

        # write transaction result with batch
        with self.db.create_write_batch() as wb:
            for tx in tx_list:
                tx_hash = tx['txHash']
                # key from transaction hash
                key = DbPrefix.TXRESULT + bytes.fromhex(tx_hash)

                # get value from transaction result dict by tx hash
                tx_result = results.get(tx_hash, "")
                tx_result['txHash'] = f'0x{tx_hash}'
                value = json.dumps(tx_result).encode()

                self.db.write_batch(write_batch=wb, key=key, value=value)

    def save_block(self, block_hash: str, tx: Union[list, dict], timestamp: int):
        """
        Save block to DB
        :param block_hash: block hash
        :param tx: transactions
        :param timestamp: block confirm timestamp
        :return:
        """
        is_genesis = isinstance(tx, dict)
        tx_list = []
        if is_genesis:
            tx_list.append(tx)
        else:
            tx_list = tx

        block_height = self.block_height + 1

        block = {
            "version": "tbears",
            "prev_block_hash": self.prev_block_hash if not is_genesis else "",
            "merkle_tree_root_hash": "tbears_block_manager_does_not_support_block_merkle_tree",
            "time_stamp": timestamp,
            "confirmed_transaction_list": tx_list,
            "block_hash": block_hash,
            "height": block_height,
            "peer_id": self.peer_id if not is_genesis else "",
            "signature": "tbears_block_manager_does_not_support_block_signature" if not is_genesis else ""
        }

        # save block
        self.db.put(DbPrefix.BLOCK + bytes.fromhex(block_hash), json.dumps(block).encode())

        # save block height/hash for block query request
        self.db.put(DbPrefix.BLOCK_INDEX + block_height.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER),
                    bytes.fromhex(block_hash))

        Logger.debug(f'save block : block_height:{block_height}, block_hash: {block_hash}, block: {block}', LOG_BLOCK)

    def get_last_block(self) -> Optional[dict]:
        """
        Get last block information
        :return: block information
        """
        # get block hash from block height/hash DB
        block_hash: bytes = self.db.get(DbPrefix.BLOCK_INDEX +
                                        self.block_height.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER))
        if block_hash is None:
            return None

        # get block Info.
        return self._get_block_by_hash(block_hash=block_hash)

    def get_block_by_height(self, block_height: int) -> Optional[dict]:
        """
        Get block information by height
        :param block_height: block height
        :return: block information
        """
        # get block hash from block height/hash DB
        block_hash: bytes = self.db.get(DbPrefix.BLOCK_INDEX + block_height.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER))
        if block_hash is None:
            return None

        # get block Info.
        return self._get_block_by_hash(block_hash=block_hash)

    def get_block_by_hash(self, block_hash: str) -> Optional[dict]:
        """
        Get block information by hash
        :param block_hash: block hash
        :return: block information
        """
        # get block Info.
        return self._get_block_by_hash(block_hash=bytes.fromhex(block_hash))

    def _get_block_by_hash(self, block_hash: bytes) -> Optional[dict]:
        """
        Get block information by hash
        :param block_hash: block hash
        :return: block information
        """
        try:
            # get block data from DB
            block: bytes = self.db.get(DbPrefix.BLOCK + block_hash)
            if block is None:
                return None
            block_json = json.loads(block)
        except Exception as e:
            Logger.debug(f'_get_block_by_hash: exception with ({e})', LOG_BLOCK)
            return None
        else:
            Logger.debug(f'_get_block_by_hash: get {block_json}', LOG_BLOCK)
            return block_json

    def get_transaction(self, tx_hash: str) -> Optional[dict]:
        """
        Get transaction information by transaction hash
        :param tx_hash: transaction hash
        :return: transaction information
        """
        tx_payload = self.db.get(DbPrefix.TX + bytes.fromhex(tx_hash))
        if tx_payload is None:
            return None

        return json.loads(tx_payload)

    def get_txresult(self, tx_hash: str) -> Optional[bytes]:
        """
        Get transaction result by transaction hash
        :param tx_hash: transaction hash
        :return: transaction result information
        """
        tx_payload = self.db.get(DbPrefix.TXRESULT + bytes.fromhex(tx_hash))
        if tx_payload is None:
            return None

        return tx_payload
