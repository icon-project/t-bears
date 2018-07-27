# Copyright 2018 theloop Inc.
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
import time
from random import randint

import requests
from typing import Optional, Union
import itertools
import hashlib

from secp256k1 import PrivateKey

from tbears.libs.icx_signer import key_from_key_store, IcxSigner
from tbears.libs.in_memory_zip import InMemoryZip
from tbears.libs.icon_serializer import generate_origin_for_icx_send_tx_hash
from tbears.tbears_exception import ZipException, DeployPayloadException


class IconJsonrpc:
    request_id = itertools.count(start=1)

    def __init__(self, signer: Union[IcxSigner, str]):
        """Constructor

        :param signer: IcxSigner object or address string
        """
        if isinstance(signer, IcxSigner):
            self.__signer = signer
            self.__address = f'hx{self.__signer.address.hex()}'
        else:
            self.__signer = None
            self.__address = signer

    @staticmethod
    def from_string(from_: str) -> 'IconJsonrpc':
        """Create IconJsonrpc object from string

        :param from_: Address string
        :return: IconJsonrpc object
        """
        return IconJsonrpc(from_)

    @staticmethod
    def from_key_store(keystore: str, password: str) -> 'IconJsonrpc':
        """Create IconJsonrpc object from keystore file path and password

        :param keystore: keystore file path
        :param password: password string
        :return: IconJsonrpc object
        """
        return IconJsonrpc(IcxSigner(key_from_key_store(keystore, password)))

    @staticmethod
    def from_private_key(private_key: Optional[PrivateKey] = None) -> 'IconJsonrpc':
        """Create IconJsonrpc object from PrivateKey object. If parameter is None, make PrivateKey object.

        :param private_key: PrivateKey object
        :return: IconJsonrpc object
        """
        return IconJsonrpc(IcxSigner(private_key=private_key or PrivateKey().private_key))

    @property
    def address(self) -> str:
        """Returns address string

        :return: address string
        """
        return self.__address

    @property
    def signer(self) -> 'IcxSigner':
        """Returns signer

        :return: IcxSigner object
        """
        return self.__signer

    @classmethod
    def getLastBlock(cls) -> dict:
        """Make JSON-RPC request for icx_getLastBlock

        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getLastBlock",
            "id": next(cls.request_id)
        }

    @classmethod
    def getBlockByHeight(cls, height: str) -> dict:
        """Make JSON-RPC request for icx_getBlockByHeight

        :param height: Block height
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHeight",
            "params": {
                "height": height
            },
            "id": next(cls.request_id)
        }

    @classmethod
    def getBlockByHash(cls, block_hash: str) -> dict:
        """Make JSON-RPC request for icx_getBlockByHash

        :param block_hash: block hash
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getBlockByHash",
            "params": {
                "hash": block_hash
            },
            "id": next(cls.request_id)
        }

    def call(self, to: str, data: dict, from_: str = None) -> dict:
        """Make JSON-RPC request for icx_call

        :param to: TO address
        :param data:
        :param from_: From address. If not set, use __address member of object
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_call",
            "params": {
                "from": from_ or self.__address,
                "to": to,
                "dataType": "call",
                "data": data
            },
            "id": next(self.request_id)
        }

    @classmethod
    def getBalance(cls, address: str) -> dict:
        """Make JSON-RPC request for getBalance

        :param address: address string to query
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getBalance",
            "params": {
                "address": address
            },
            "id": next(cls.request_id)
        }

    @classmethod
    def getScoreApi(cls, score_address: str) -> dict:
        """Make JSON-RPC request for icx_getBalance

        :param score_address: SCORE address to query
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getScoreApi",
            "params": {
                "address": score_address
            },
            "id": next(cls.request_id)
        }

    @classmethod
    def getTotalSupply(cls) -> dict:
        """Make JSON-RPC request for icx_getTotalSupply

        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getTotalSupply",
            "id": next(cls.request_id)
        }

    @classmethod
    def getTransactionResult(cls, tx_hash: str) -> dict:
        """Make JSON-RPC request for icx_getTransactionResult

        :param tx_hash: Hash string to query
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionResult",
            "params": {
                "txHash": tx_hash
            },
            "id": next(cls.request_id)
        }

    @classmethod
    def getTransactionResult_v2(cls, tx_hash: str) -> dict:
        """Make JSON-RPC request for icx_getTransactionResult for api version 2

        :param tx_hash: Hash string to query
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionResult",
            "params": {
                "tx_hash": tx_hash
            },
            "id": next(cls.request_id)
        }

    @classmethod
    def getTransactionByHash(cls, tx_hash: str) -> dict:
        """Make JSON-RPC request for icx_getTransactionByHash

        :param tx_hash: Hash string to query
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionByHash",
            "params": {
                "txHash": tx_hash
            },
            "id": next(cls.request_id)
        }

    @classmethod
    def getTransactionByHash_v2(cls, tx_hash: str) -> dict:
        """Make JSON-RPC request for icx_getTransactionByHash for api version 2

        :param tx_hash: Hash string to query
        :return: JSON dictionary
        """
        return {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionByHash",
            "params": {
                "tx_hash": tx_hash
            },
            "id": next(cls.request_id)
        }

    def sendTransaction(self,
                        version: str = '0x3',
                        from_: str = None,
                        to: str = None,
                        value: str = '0x0',
                        step_limit: str = '0x2000',
                        nid: str = '0x3',
                        nonce: str= '0x1',
                        timestamp: str = hex(int(time.time() * 10 ** 6)),
                        data_type: str = None,
                        data: Union[dict, str, None] = None) -> dict:
        """Make JSON-RPC request of icx_sendTransaction
        :param version: version
        :param from_: From address. If not set, use __address member of object
        :param to: To address
        :param value: Amount of ICX coin in loop to transfer (1 icx = 1e18 loop)
        :param step_limit: Maximum step limit for transaction
        :param nid: Network ID
        :param nonce: nonce
        :param timestamp: timestamp
        :param data_type: type of data. {'call'|'deploy'|'message'}
        :param data: data dictionary
        :return: icx_sendTransaction JSON-RPC request dictionary
        """
        # make params
        params = {
            "version": version,
            "from": from_ or self.__address,
            "value": value,
            "stepLimit": step_limit,
            "timestamp": timestamp,
            "nid": nid,
            "nonce": nonce,
        }

        # insert 'to' if need
        if to:
            params['to'] = to

        # insert 'data_type' and 'data' if need
        if data_type and data:
            params['data'] = data
            params['dataType'] = data_type

        # insert signature
        self.put_signature(params)

        return {
            "jsonrpc": "2.0",
            "method": "icx_sendTransaction",
            "params": params,
            "id": next(self.request_id)
        }

    def sendTransaction_v2(self, from_: str = None, to: str = None, value: str = '0x0', fee: str = hex(int(1e16)),
                           timestamp: str=hex(int(time.time() * 10 ** 6)), nonce: str='0x1'):
        """Make JSON-RPC request of icx_sendTransaction
        :param from_: From address. If not set, use __address member of object
        :param to: To address
        :param value: Amount of ICX coin in loop to transfer (1 icx = 1e18 loop)
        :param fee: fee
        :param timestamp: timestamp
        :param nonce: nonce
        :return: icx_sendTransaction JSON-RPC request dictionary
        """
        params = {
            "from": from_ or self.__address,
            "value": value,
            "fee": fee,
            "timestamp": timestamp,
            "nonce": nonce
        }
        if to:
            params['to'] = to

        msg_phrase = generate_origin_for_icx_send_tx_hash(params)
        msg_hash = hashlib.sha3_256(msg_phrase.encode()).digest().hex()

        params["tx_hash"] = msg_hash
        self.put_signature(params)

        return {
            "jsonrpc": "2.0",
            "method": "icx_sendTransaction",
            "params": params,
            "id": next(self.request_id)
        }

    def getTransactionByAddress(self, address: str, index: int=0):
        """Make JSON-RPC request of icx_getTransactionByAddress

        :param address: address string to query.
        :param index: index to query
        :return: icx_getTransactionByAddress JSON-RPC request dictionary
        """

        return {
            "jsonrpc": "2.0",
            "method": "icx_getTransactionByAddress",
            "id": next(self.request_id),
            "params": {
                "address": address,
                "index": index
            }
        }

    @staticmethod
    def gen_call_data(method: str, params: dict = {}) -> dict:
        """Generate data dictionary for icx_call and icx_sendTransaction which dataType is 'call'

        :param method: method name in SCORE
        :param params: parameters for method
        :return: data dictionary
        """
        return {
            "method": method,
            "params": params
        }

    @staticmethod
    def gen_deploy_data(content: str,
                        content_type: str = "application/zip",
                        params: dict = {}) -> dict:
        """Generate data dictionary of icx_sendTransaction which dataType is 'deploy'

        :param content: SCORE data
        :param content_type: type of contenst. {'application/zip'|'application/tbears'}
        :param params: parameter for on_install() or on_update() of SCORE
        :return: data dictionary
        """
        return {
            "contentType": content_type,
            "content": content,
            "params": params
        }

    @staticmethod
    def gen_deploy_data_content(path: str) -> str:
        """Generate zip data(hex string) of SCORE.

        :param path: The path of the directory to be zipped.
        """
        if os.path.isdir(path) is False:
            raise Exception
        try:
            memory_zip = InMemoryZip()
            memory_zip.zip_in_memory(path)
        except ZipException:
            raise DeployPayloadException(f"Can't zip SCORE contents")
        else:
            return f'0x{memory_zip.data.hex()}'

    def put_signature(self, params: dict) -> None:
        """Make signature and put to params of icx_sendTransaction request.

        :param params: params of icx_sendTransaction request.
        """
        if self.__signer:
            phrase = generate_origin_for_icx_send_tx_hash(params)
            msg_hash = hashlib.sha3_256(phrase.encode()).digest()
            signature = self.__signer.sign(msg_hash)
            params['signature'] = signature.decode()
        else:
            params['signature'] = 'sig'


class IconClient(object):
    def __init__(self, uri: str):
        """Constructor

        :param uri: uri of destination
        """
        self.__uri = uri

    def send(self, request) -> dict:
        """Send request to uri

        :param request: JSON-RPC request
        :return: response dictionary of request.
        """
        return requests.post(url=self.__uri, json=request).json()

    def send_transaction(self, request) -> dict:
        """Send request icx_sendTransaction to uri. If get success response, send icx_getTransactionResult request
        and return response

        :param request: JSON-RPC request
        :return: response dictionary of request.
        """
        # check method
        if request['method'] != 'icx_sendTransaction':
            raise ValueError(f'invalid method {request["method"]}')

        # sendTransaction
        response = self.send(request=request)

        if 'error' in response:
            return response

        # getTransactionResult
        return requests.post(url=self.__uri,
                             json=IconJsonrpc.getTransactionResult(tx_hash=response['result'])).json()
