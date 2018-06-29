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
import json
import time

import requests
from iconservice import Logger


def send_req(method: str, params: dict, url: str=None):
    if method == 'icx_sendTransaction':
        check_timestamp(params)

    if url is None:
        url = 'http://localhost:9000/api/v3'

    json_content = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": convert_dict(params)
    }
    try:
        res = requests.post(url, json.dumps(json_content))
    except Exception as e:
        print(f'\n##############{str(e)}################\n')
    else:
        print(f'\n###############response : {res.json()}###############')
        return res


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


def check_timestamp(params):
    if 'timestamp' not in params:
        params['timestamp'] = int(time.time() * 10 ** 6)
