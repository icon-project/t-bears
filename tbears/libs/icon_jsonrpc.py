# Copyright 2018 ICON Foundation
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
import copy
import hashlib
import itertools
import json
import os
import time
from typing import Optional, Union

import requests
from iconcommons.logger.logger import Logger

from tbears.config.tbears_config import TBEARS_CLI_TAG, GOVERNANCE_ADDRESS
from tbears.libs.icon_serializer import generate_origin_for_icx_send_tx_hash
from tbears.tbears_exception import ZipException, DeployPayloadException, IconClientException, TBearsEstimateException


class IconJsonrpc:
    # used for generating jsonrpc id
    request_id = itertools.count(start=1)

    def __init__(self, signer: str):
        """Constructor

        :param signer: IcxSigner object or address string
        """
        # Signature is not needed in a local environment. So just assign a string
        self.__signer = None
        self.__address = signer

    @staticmethod
    def from_string(from_: str) -> 'IconJsonrpc':
        """Create IconJsonrpc object from string

        :param from_: Address string
        :return: IconJsonrpc object
        """
        return IconJsonrpc(from_)

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
        """Make JSON-RPC request for icx_getScoreApi

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
        """Make JSON-RPC request for icx_getTransactionResult for API version 2

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

    def sendTransaction(self,
                        version: str = '0x3',
                        from_: str = None,
                        to: str = None,
                        value: str = '0x0',
                        step_limit: str = None,
                        nid: str = '0x3',
                        nonce: str= '0x1',
                        timestamp: str = None,
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
        if timestamp is None:
            timestamp = hex(int(time.time() * 10 ** 6))
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
                           timestamp: str=None, nonce: str='1'):
        """Make JSON-RPC request of icx_sendTransaction
        :param from_: From address. If not set, use __address member of object
        :param to: To address
        :param value: Amount of ICX coin in loop to transfer (1 icx = 1e18 loop)
        :param fee: fee
        :param timestamp: timestamp
        :param nonce: nonce
        :return: icx_sendTransaction JSON-RPC request dictionary
        """
        if timestamp is None:
            timestamp = str(int(time.time() * 10 ** 6))
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

        self.put_signature(params)
        params["tx_hash"] = msg_hash

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

    @classmethod
    def iseGetStatus(cls, _filter: list):
        """Make JSON-RPC request of ise_GetStatus

        :return: ise_GetStatus request dictionary
        """

        return {
            "jsonrpc": "2.0",
            "method": "ise_getStatus",
            "id": next(cls.request_id),
            "params": {
                "filter": _filter
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

    def put_signature(self, params: dict) -> None:
        """Make signature and put to params of icx_sendTransaction request.

        :param params: params of icx_sendTransaction request.
        """
        if self.__signer:
            # generate phrase which is used for making signature.
            # if transaction data is changed, signature will be invalid as phrase also changed
            put_signature_to_params(self.__signer, params)
        else:
            # in a local environment, doesn't need actual signature as doesn't validate tx
            # so just assign string data
            params['signature'] = 'sig'


class IconClient(object):
    def __init__(self, uri: str):
        """Constructor

        :param uri: URI of destination
        """
        self.__uri = uri

    def send(self, request) -> dict:
        """Send request to URI

        :param request: JSON-RPC request
        :return: response dictionary of request.
        """
        Logger.info(f"Send request to {self.__uri}. Request body: {request}", TBEARS_CLI_TAG)

        # if query doesn't change any state of iconservice or loopchain, use 'send' method
        response = requests.post(url=self.__uri, json=request)
        try:
            response_json = response.json()
        except ValueError:
            if not response.ok:
                raise IconClientException(f"Got error response. Response status_code: [{response.status_code}]")
        else:
            return response_json

    def send_transaction(self, request) -> dict:
        """Send request icx_sendTransaction to URI. If get success response, send icx_getTransactionResult request
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


def put_signature_to_params(signer: 'IcxSigner', params: dict) -> None:
    phrase = generate_origin_for_icx_send_tx_hash(params)
    msg_hash = hashlib.sha3_256(phrase.encode()).digest()
    signature = signer.sign(msg_hash)
    params['signature'] = signature.decode()


def convert_tx_request_to_estimate(request: dict):
    """Convert Transaction request data to estimate request data.

    :param request: Request to convert
    :return: Converted data
    """

    data = copy.deepcopy(request)
    data['method'] = "debug_estimateStep"
    del data['params']['signature']
    del data['params']['stepLimit']
    return data


def get_enough_step(request: dict, uri: str) -> int:
    estimate_request = convert_tx_request_to_estimate(request)
    debug_uri = uri.replace('api/v3', 'api/debug/v3')
    debug_client = IconClient(debug_uri)
    estimate_response = debug_client.send(estimate_request)
    if "error" in estimate_response:
        raise TBearsEstimateException(f"Got error response while estimating step. error message "
                                      f": {estimate_response['error']['message']}")
    estimated_step = int(estimate_response['result'], 16)
    step_limit = int(estimated_step * 1.1)
    return step_limit


def get_default_step(uri: str) -> int:
    client = IconClient(uri)
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "icx_call",
        "params": {
            "to": "cx0000000000000000000000000000000000000001",
            "dataType": "call",
            "data": {
                "method": "getStepCosts"
            }
        }
    }
    response = client.send(request=payload)
    if 'result' in response:
        default_step = int(response['result']['default'], 16)
    else:
        print(json.dumps(response, indent=4))
        default_step = 100000
    return default_step

