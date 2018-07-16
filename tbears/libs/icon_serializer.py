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
import copy
import hashlib

translator = str.maketrans({
    "\\": "\\\\",
    "{": "\\{",
    "}": "\\}",
    "[": "\\[",
    "]": "\\]",
    ".": "\\."
})


def generate_origin_for_hash(json_data: dict):

    def encode(data):
        if isinstance(data, dict):
            return encode_dict(data)
        elif isinstance(data, list):
            return encode_list(data)
        else:
            return escape(data)

    def encode_dict(data: dict):
        result = ".".join(_encode_dict(data))
        return "{" + result + "}"

    def _encode_dict(data: dict):
        for key in sorted(data.keys()):
            yield key
            yield encode(data[key])

    def encode_list(data: list):
        result = ".".join(_encode_list(data))
        return f"[" + result + "]"

    def _encode_list(data: list):
        for item in data:
            yield encode(item)

    def escape(data):
        if data is None:
            return "\\0"

        data = str(data)
        return data.translate(translator)

    return ".".join(_encode_dict(json_data))


def get_tx_hash_key(icx_origin_data):
    if get_tx_version(icx_origin_data) == hex(3):
        tx_hash_key = "txHash"
    else:
        tx_hash_key = "tx_hash"
    return tx_hash_key


def get_tx_version(icx_origin_data):
    if 'version' in icx_origin_data and icx_origin_data['version'] == hex(3):
        return hex(3)
    return hex(2)


def generate_origin_for_icx_send_tx_hash(icx_origin_data):
    copy_tx = copy.deepcopy(icx_origin_data)

    tx_hash_key = get_tx_hash_key(icx_origin_data)
    if tx_hash_key in copy_tx:
        del copy_tx[tx_hash_key]

    if 'method' in copy_tx:
        del copy_tx['method']

    if 'signature' in copy_tx:
        del copy_tx['signature']

    origin = generate_origin_for_hash(copy_tx)
    return f"icx_sendTransaction.{origin}"


def generate_icx_hash(icx_origin_data):
    origin = generate_origin_for_icx_send_tx_hash(icx_origin_data)
    return hashlib.sha3_256(origin.encode()).hexdigest()
