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
import json
import os
import time

import requests

from tbears.tbears_exception import ZipException, FillDeployPaylodException
from tbears.util import IcxSigner, InMemoryZip


class IconClient:

    def __init__(self, url: str, version: int, private_key: bytes):
        self._url = url
        self._version = version
        self._private_key = private_key
        self._signer = IcxSigner(self._private_key)

    def send(self, method: str, params: dict) -> requests.Response:
        json_content = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 12345,
        }
        if method == 'icx_sendTransaction':
            if self._version == 3:
                params['version'] = hex(3)
            params['timestamp'] = hex(int(time.time() * 10 ** 6))
            put_signature_to_payload(params, self._signer)

        if method != 'icx_getTotalSupply':
            json_content['params'] = convert_dict(params)

        json_content = json.dumps(json_content)
        resp = requests.post(self._url, json_content)
        return resp


def fill_deploy_payload(payload: dict = None, project_root_path: str = None, signer: 'IcxSigner' = None):
    if not payload or not signer:
        raise Exception
    if os.path.isdir(project_root_path) is False:
        raise Exception
    try:
        memory_zip = InMemoryZip()
        memory_zip.zip_in_memory(project_root_path)
    except ZipException:
        raise FillDeployPaylodException
    else:
        payload['data']['content'] = f'0x{memory_zip.data.hex()}'
        payload['from'] = f'hx{signer.address.hex()}'


def put_signature_to_payload(payload: dict, signer: 'IcxSigner'):
    phrase = f'icx_sendTransaction.{get_tx_phrase(payload)}'
    msg_hash = hashlib.sha3_256(phrase.encode()).digest()
    signature = signer.sign(msg_hash)
    payload['signature'] = signature.decode()


def fill_optional_deploy_field(payload: dict, step_limit: str = None, score_address: str = None,
                               params: dict = None):
    if step_limit:
        payload["stepLimit"] = step_limit
    if score_address:
        payload["to"] = score_address
    if params:
        payload["data"]["params"] = params


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
        "timestamp": f'{hex(int(time.time() * 10 ** 6))}',
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


def get_deploy_payload(path: str, signer: 'IcxSigner', step_limit: str=None, score_address: str=None,
                       params: dict=None) -> dict:
    payload = get_deploy_req_template()
    fill_optional_deploy_field(payload=payload, step_limit=step_limit, score_address=score_address,
                               params=params)
    fill_deploy_payload(payload, path, signer)
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