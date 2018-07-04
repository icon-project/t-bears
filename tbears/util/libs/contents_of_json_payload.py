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


def get_payload_of_transaction_result(tx_hash: str) -> dict:
    return {"txHash": tx_hash}


def get_payload_of_get_icx_balance(address: str) -> dict:
    return {"address": address}


def get_payload_of_send_icx(fr: str, to: str, value: str) -> dict:
    return {
        "from": fr,
        "to": to,
        "value": value
    }


def get_payload_of_get_score_api(address: str) -> dict:
    return {
        "address": address
    }


def get_payload_of_send_tx_to_score(fr: str, to: str, value: str, score_method: str, params: dict=None):
    if not params:
        params = {}
    return {
        "from": fr,
        "to": to,
        "value": value,
        "dataType": "call",
        "data": {
            "method": score_method,
            "params": params
        }
    }


def get_payload_of_icx_call(fr: str, to: str, score_method: str, params: dict=None):
    if not params:
        params = {}
    return {
        "from": fr,
        "to": to,
        "dataType": "call",
        "data": {
            "method": score_method,
            "params": params
        }
    }
