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

from tbears.util.icx_signer import key_from_key_store, IcxSigner

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))
TBEARS_JSON_PATH = os.path.join(DIRECTORY_PATH, 'test_tbears.json')


def get_request_json_of_call_hello():
    return {
        "jsonrpc": "2.0",
        "method": "hello",
        "id": 1,
        "params": {}
    }


def get_request_of_icx_getTransactionResult(tx_hash: str) -> dict:
    return {"txHash": tx_hash}


def get_request_json_of_get_icx_balance(address: str) -> dict:
    return {"address": address}


def get_request_json_of_send_icx(fr: str, to: str, value: str) -> dict:
    return {
        "from": fr,
        "to": to,
        "value": value,
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
    }


def get_request_json_of_get_token_balance(to: str, addr_from: str) -> dict:
    return {
        "from": "hx0000000000000000000000000000000000000000",
        "to": to,
        "dataType": "call",
        "data": {
            "method": "balance_of",
            "params": {
                "addr_from": addr_from
            }
        }
    }


def get_request_json_of_transfer_token(fr: str, to: str, addr_to: str, value: str) -> dict:
    return {
        "from": fr,
        "to": to,
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
        "dataType": "call",
        "data": {
            "method": "transfer",
            "params": {
                "addr_to": addr_to,
                "value": value
            }
        }
    }


def get_request_json_of_check_crowd_end(fr: str, to: str) -> dict:
    return {
        "from": fr,
        "to": to,
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
        "dataType": "call",
        "data": {
            "method": "check_goal_reached",
            "params": {}
        }
    }


def get_request_json_of_crowd_withrawal(fr: str, to: str) -> dict:
    return {
        "from": fr,
        "to": to,
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
        "dataType": "call",
        "data": {
            "method": "safe_withdrawal",
            "params": {}
        }
    }


def get_request_json_of_token_total_supply(token_addr: str) -> dict:
    return {
        "from": "hx0000000000000000000000000000000000000000",
        "to": token_addr,
        "dataType": "call",
        "data": {
            "method": "total_supply",
            "params": {}
        }
    }


def get_request_json_of_nonexist_method(token_addr: str) -> dict:
    return {
        "from": "hx0000000000000000000000000000000000000000",
        "to": token_addr,
        "dataType": "call",
        "data": {
            "method": "total_supp",
            "params": {}
        }
    }


def get_request_json_of_get_score_api(address: str) -> dict:
    return {
        "address": address
    }


god_address = f'hx{"0"*40}'
test_address = f'hx1{"0"*39}'
token_owner_address = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
token_score_address = "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf"
CALL = 'icx_call'
SEND = 'icx_sendTransaction'
BAL = 'icx_getBalance'
TX_RESULT = 'icx_getTransactionResult'
API = 'icx_getScoreApi'
URL = "http://localhost:9000/api/v3"
deploy_token_owner_private_key = key_from_key_store(os.path.join(DIRECTORY_PATH, 'keystore'), 'qwer1234%')
token_owner_signer = IcxSigner(deploy_token_owner_private_key)
deploy_token_owner_address = f'hx{token_owner_signer.address.hex()}'
