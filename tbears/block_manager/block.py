# Copyright 2017-2018 theloop Inc.
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
    def __init__(self, conf: 'IconConfig'):
        self._db: TbearsDB = TbearsDB(TbearsDB.make_db(f'{conf["stateDbRootPath"]}/tbears'))
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
        byte_block_height = self.db.get(DbPrefix.BLOCK_HEIGHT)
        byte_prev_block_hash = self.db.get(DbPrefix.PREV_BLOCK)

        if byte_block_height is not None:
            block_height = byte_block_height.decode()
            self._block_height = int(block_height)
        if byte_prev_block_hash is not None:
            self._prev_block_hash = bytes.hex(byte_prev_block_hash)

    def get_block_height(self):
        return self._block_height

    def set_block_height(self):
        self._block_height += 1
        self.db.put(DbPrefix.BLOCK_HEIGHT, str(self._block_height).encode())

    def get_prev_block_hash(self):
        return self._prev_block_hash

    def set_prev_block_hash(self, block_hash: str):
        self._prev_block_hash = block_hash
        self.db.put(DbPrefix.PREV_BLOCK, bytes.fromhex(self._prev_block_hash))

    def confirm_block(self, prev_block_hash: str):
        self.set_block_height()
        self.set_prev_block_hash(block_hash=prev_block_hash)

    def save_transaction(self, tx_hash: str, params: dict, block_hash: str, block_height: int):
        del params['txHash']
        params['txIndex'] = "0x0"
        params['blockHeight'] = hex(block_height)
        params['blockHash'] = f'0x{block_hash}'

        self.db.put(DbPrefix.TX + bytes.fromhex(tx_hash), json.dumps(params).encode())

    def save_transactions(self, tx_list: list, block_hash: str):
        Logger.debug(f'save_transactions: {tx_list}', LOG_BLOCK)
        if len(tx_list) == 0:
            return
        with self.db.create_write_batch() as wb:
            for i, tx in enumerate(tx_list):
                k = tx[0]
                v = tx[1]
                key, value = self._get_tx_value(i, k, v, block_hash, self._block_height)
                self.db.write_batch(write_batch=wb, key=key, value=value)

    @staticmethod
    def _get_tx_value(index: int, k: str, v: dict, block_hash: str, block_height: int):
        key = DbPrefix.TX + bytes.fromhex(k)

        value = {
            'transaction': v,
            'tx_index': hex(index),
            'block_height': hex(block_height),
            'block_hash': f'0x{block_hash}'
        }

        return key, json.dumps(value).encode()

    def save_txresult(self, tx_hash: str, tx_result):
        self.db.put(DbPrefix.TXRESULT + bytes.fromhex(tx_hash), json.dumps(tx_result).encode())

    def save_txresults(self, tx_list: list, results: dict):
        Logger.debug(f'save_txresult:{results}', LOG_BLOCK)
        if len(tx_list) == 0:
            return
        with self.db.create_write_batch() as wb:
            for tx in tx_list:
                key = DbPrefix.TXRESULT + bytes.fromhex(tx[0])
                tx_result = results.get(tx[0], "")
                tx_result['txHash'] = f'0x{tx[0]}'
                value = json.dumps(tx_result).encode()
                self.db.write_batch(write_batch=wb, key=key, value=value)

    def save_block(self, block_hash: str, tx: Union[list, dict], timestamp: int):
        is_genesis = isinstance(tx, dict)
        tx_list = []
        if not is_genesis:
            for tx_tuple in tx:
                tx_list.append(tx_tuple[0])
        else:
            tx_list.append(tx)
        block = {
            "version": "tbears",
            "prev_block_hash": self._prev_block_hash if not is_genesis else "",
            "merkle_tree_root_hash": "tbears_does_not_support_merkle_tree",
            "time_stamp": timestamp,
            "confirmed_transaction_list": tx_list,
            "block_hash": block_hash,
            "height": self._block_height,
            "peer_id": self.peer_id if not is_genesis else "",
            "signature": "tbears_does_not_support_signature" if not is_genesis else ""
        }

        # save block
        self.db.put(DbPrefix.BLOCK + bytes.fromhex(block_hash), json.dumps(block).encode())

        # save block height/hash
        self.db.put(DbPrefix.BLOCK_INDEX + self._block_height.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER),
                    bytes.fromhex(block_hash))

        Logger.debug(f'save block : block_height:{self._block_height}, block_hash: {block_hash}, block: {block}',
                     LOG_BLOCK)

    def get_last_block(self) -> Optional[dict]:
        block_hash: bytes = self.db.get(DbPrefix.BLOCK_INDEX + self._block_height.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER))
        if block_hash is None:
            return None

        return self.get_block_by_hash(block_hash=block_hash)

    def get_block_by_height(self, block_height: int) -> Optional[dict]:
        block_hash: bytes = self.db.get(DbPrefix.BLOCK_INDEX + block_height.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER))
        if block_hash is None:
            return None

        return self.get_block_by_hash(block_hash=block_hash)

    def get_block_by_hash(self, block_hash: bytes) -> Optional[dict]:
            try:
                block: bytes = self.db.get(DbPrefix.BLOCK + block_hash)
                if block is None:
                    return None
                block_json = self.get_block_result(json.loads(block))
            except Exception:
                return None
            else:
                return block_json

    def get_block_result(self, block: dict) -> dict:
        tx_list = block.get('confirmed_transaction_list', None)
        if tx_list is not None and isinstance(tx_list, list):
            result_list = []
            for tx in tx_list:
                if isinstance(tx, dict):
                    # genesis block
                    result_list.append(tx)
                    break
                tx_result = self.get_transaction(tx_hash=tx)
                result_list.append(tx_result['transaction'])

            block['confirmed_transaction_list'] = result_list

        return block

    def get_transaction(self, tx_hash: str) -> Optional[dict]:
        tx_payload = self.db.get(DbPrefix.TX + bytes.fromhex(tx_hash))
        if tx_payload is None:
            return None

        return json.loads(tx_payload)

    def get_txresult(self, tx_hash: str) -> Optional[bytes]:
        tx_payload = self.db.get(DbPrefix.TXRESULT + bytes.fromhex(tx_hash))
        if tx_payload is None:
            return None

        return tx_payload
