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
import hashlib
import os
import time

from tbears.tbears_exception import ZipException, FillDeployPaylodException
from tbears.util import InMemoryZip, IcxSigner


def json_rpc_format(method: str, _id: int = 1, params: dict = {}) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": method,
        "id": _id,
        "params": convert_dict(params)
    }


def json_tx_result(tx_hash: str) -> dict:
    return json_rpc_format('icx_getTransactionResult', params=params_tx_result(tx_hash))


def json_total_supply() -> dict:
    return json_rpc_format('icx_totalSupply')


def params_tx_result(tx_hash: str) -> dict:
    return {'txHash': tx_hash}


def json_get_balance(address: str) -> dict:
    return json_rpc_format('icx_getBalance', params=params_get_balance(address))


def params_get_balance(address: str) -> dict:
    return {"address": address}


def json_score_api(address: str) -> dict:
    return json_rpc_format('icx_getScoreApi', params=params_score_api(address))


def params_score_api(address: str) -> dict:
    return {"address": address}


def params_icx_call(fr: str, to: str, score_method: str, params: dict = {}) -> dict:
    return {
        "from": fr,
        "to": to,
        "dataType": "call",
        "data": {
            "method": score_method,
            "params": params
        }
    }


def json_icx_call(fr: str, to: str, score_method: str, params: dict = {}):
    return json_rpc_format('icx_call', params=params_icx_call(fr, to, score_method, params))


def json_send_transaction(signer: 'IcxSigner', payload: dict, version: int) -> dict:
    if version == 3:
        payload['version'] = hex(3)
    put_signature_to_payload(payload, signer)
    return json_rpc_format('icx_sendTransaction', params=payload)


def params_send_transaction(fr: str, to: str, value: str,
                            step_limit: str = '0x12345', nonce: str = '0x1') -> dict:
    return {
        "from": fr,
        "to": to,
        "value": value,
        "timestamp": hex(int(time.time() * 10 ** 6)),
        "stepLimit": step_limit,
        "nonce": nonce
    }


def json_send_transaction_deploy(path: str, signer: 'IcxSigner', nonce: str = '0x1', step_limit: str = '0x12345',
                                 score_address: str = None, params: dict = {}, version=3) -> dict:
    if not score_address:
        score_address = f'cx{"0"*40}'
    payload = params_send_transaction(f'hx{signer.address.hex()}', score_address, '0x0', step_limit, nonce)
    payload['dataType'] = 'deploy'
    payload['data'] = {}
    payload['data']['params'] = params
    fill_deploy_content(payload, path)
    return json_send_transaction(signer, payload, version)


def json_send_transaction_score(signer: 'IcxSigner', to, value, score_method: str,
                                score_params: dict = {}, step_limit='0x12345', nonce='0x1', version=3):
    payload = params_send_transaction(f'hx{signer.address.hex()}', to, value, step_limit, nonce)
    payload['dataType'] = 'call'
    payload['data'] = {}
    payload['data']['method'] = score_method
    payload['data']['params'] = score_params
    return json_send_transaction(signer, payload, version)


def json_dummy_send_transaction(fr: str, to: str, value: str, step_limit: str,
                                data: dict, signature: str, nonce: str = "0x12345", data_type: str = None) -> dict:
    payload = {
        "from": fr,
        "to": to,
        "value": value,
        "stepLimit": step_limit,
        "nonce": nonce,
        "version": '0x3',
        "signature": signature
    }
    if data_type == 'deploy' or data_type == 'call':
        payload['dataType'] = data_type
        payload['data'] = data

        return json_rpc_format('icx_sendTransaction', params=payload)
    else:
        return json_rpc_format('icx_sendTransaction', params=payload)


def fill_deploy_content(payload: dict = None, project_root_path: str = None):
    if not payload:
        raise Exception
    if os.path.isdir(project_root_path) is False:
        raise Exception
    try:
        memory_zip = InMemoryZip()
        memory_zip.zip_in_memory(project_root_path)
    except ZipException:
        raise FillDeployPaylodException
    else:
        payload['data']['contentType'] = 'application/zip'
        payload['data']['content'] = f'0x{memory_zip.data.hex()}'


def fill_optional_deploy_field(payload: dict, step_limit: str = None, score_address: str = None,
                               params: dict = None):
    if step_limit:
        payload["stepLimit"] = step_limit
    if score_address:
        payload["to"] = score_address
    if params:
        payload["data"]["params"] = params


def put_signature_to_payload(payload: dict, signer: 'IcxSigner'):
    phrase = f'icx_sendTransaction.{get_tx_phrase(payload)}'
    msg_hash = hashlib.sha3_256(phrase.encode()).digest()
    signature = signer.sign(msg_hash)
    payload['signature'] = signature.decode()


def get_tx_phrase(params: dict) -> str:
    keys = [k for k in params]
    keys.sort()
    key_count = len(keys)
    if key_count == 0:
        return ""
    phrase = ""

    if not params[keys[0]]:
        phrase += keys[0]
    elif not isinstance(params[keys[0]], dict):
        phrase += f'{keys[0]}.{params[keys[0]]}'
    else:
        phrase += f'{keys[0]}.{get_tx_phrase(params[keys[0]])}'

    for i in range(1, key_count):
        key = keys[i]

        if not params[key]:
            phrase += f'.{key}'
        elif not isinstance(params[key], dict):
            phrase += f'.{key}.{params[key]}'
        else:
            phrase += f'.{key}.{get_tx_phrase(params[key])}'

    return phrase


def get_deploy_req_template():
    payload = {
        "version": "0x3",
        "from": "",
        "to": f'cx{"0"*40}',
        "stepLimit": "0x12345",
        "timestamp": hex(int(time.time() * 10 ** 6)),
        "nonce": "0x1",
        "dataType": "deploy",
        "data": {
            "contentType": "application/zip",
            "content": "",
            "params": {

            }
        }
    }
    return payload


def convert_dict(dict_value) -> dict:
    output = {}

    for key, value in dict_value.items():
        if isinstance(value, dict):
            output[key] = convert_dict(value)
        elif isinstance(value, list):
            output[key] = convert_list(value)
        else:
            output[key] = convert_value(value)

    return output


def convert_list(list_value) -> list:
    output = []

    for item in list_value:
        if isinstance(item, dict):
            item = convert_dict(item)
        elif isinstance(item, list):
            item = convert_list(item)
        else:
            item = convert_value(item)

        output.append(item)
    return output


def convert_value(value):
    if isinstance(value, int):
        return hex(value)
    else:
        return str(value)
