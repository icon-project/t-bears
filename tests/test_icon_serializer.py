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
import json
import unittest

import tbears.libs.icon_serializer
from tbears import libs
from tbears.libs.icon_serializer import generate_origin_for_icx_send_tx_hash


class TestTXPhrase(unittest.TestCase):

    def test_serialize_v2(self):
        # test to see if a hash is properly generated with v2 params.
        request = r'''{
            "jsonrpc": "2.0",
            "method": "icx_sendTransaction",
            "id": 1234,
            "params": {
                "version": "0x3",
                "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
                "to": "hx5bfdb090f43a808005ffc27c25b213145e80b7cd",
                "value": "0xde0b6b3a7640000",
                "timestamp": "0x563a6cf330136",
                "nonce": "0x1"
            }
        }'''

        request = json.loads(request)

        question = request["params"]
        answer = "icx_sendTransaction.from.hxbe258ceb872e08851f1f59694dac2558708ece11.nonce.0x1." \
                 "timestamp.0x563a6cf330136.to.hx5bfdb090f43a808005ffc27c25b213145e80b7cd." \
                 "value.0xde0b6b3a7640000.version.0x3"

        result = generate_origin_for_icx_send_tx_hash(question)
        self.assertEqual(result, answer)

    def test_serialize_case_v3(self):
        # test to see if a hash is properly generated with v3 params.
        request = '''{
            "jsonrpc": "2.0",
            "method": "icx_sendTransaction",
            "id": 1234,
            "params": {
                "version": "0x3",
                "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
                "to": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32",
                "stepLimit": "0x12345",
                "timestamp": "0x563a6cf330136",
                "nonce": "0x1",
                "dataType": "call",
                "data": {
                    "method": "transfer",
                    "params": {
                        "to": "hxab2d8215eab14bc6bdd8bfb2c8151257032ecd8b",
                        "value": "0x1",
                        "array0": [
                            "1",
                            "221"
                        ],
                        "array1": [
                            {
                                "hash": "0x12",
                                "value": "0x34"
                            },
                            {
                                "hash": "0x56",
                                "value": "0x78"
                            }
                        ]
                    }
                }
            }
        }'''

        request = json.loads(request)

        question = request["params"]
        answer = "icx_sendTransaction.data.{method.transfer.params." \
                 "{array0.[1.221].array1.[{hash.0x12.value.0x34}.{hash.0x56.value.0x78}]." \
                 "to.hxab2d8215eab14bc6bdd8bfb2c8151257032ecd8b.value.0x1}}." \
                 "dataType.call.from.hxbe258ceb872e08851f1f59694dac2558708ece11.nonce.0x1.stepLimit.0x12345." \
                 "timestamp.0x563a6cf330136.to.cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32.version.0x3"

        result = generate_origin_for_icx_send_tx_hash(question)
        self.assertEqual(result, answer)

    def test_serialize_v3_escape(self):
        # test whether the hash is properly generated When there are escape characters in v3 params.
        request = r'''{
            "jsonrpc": "2.0",
            "method": "icx_sendTransaction",
            "id": 1234,
            "params": {
                "version": "0x3",
                "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
                "to": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32",
                "stepLimit": "0x12345",
                "timestamp": "0x563a6cf330136",
                "nonce": "0x1",
                "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA=",
                "dataType": "call",
                "data": {
                    "method": "transfer",
                    "params": {
                        "to": "hx.ab2d8215eab\\14bc6bdd8bfb2c[8151257]032ec{d8}b",
                        "value": "0x1",
                        "array0": [
                            "1",
                            "2.21"
                        ],
                        "array1": [
                            {
                                "hash": "0x12",
                                "value": "0x34"
                            },
                            {
                                "hash": "0x56",
                                "value": "0x78"
                            }
                        ]
                    }
                }
            }
        }'''

        request = json.loads(request)

        question = request['params']
        answer = r"icx_sendTransaction.data.{method.transfer.params." \
                 r"{array0.[1.2\.21].array1.[{hash.0x12.value.0x34}.{hash.0x56.value.0x78}]." \
                 r"to.hx\.ab2d8215eab\\14bc6bdd8bfb2c\[8151257\]032ec\{d8\}b.value.0x1}}." \
                 r"dataType.call.from.hxbe258ceb872e08851f1f59694dac2558708ece11.nonce.0x1.stepLimit.0x12345." \
                 r"timestamp.0x563a6cf330136.to.cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32.version.0x3"

        result = generate_origin_for_icx_send_tx_hash(question)
        self.assertEqual(result, answer)

    def test_serialize_v3_null(self):
        # test whether the hash is properly generated When there are null characters in v3 params.
        request = r'''{
            "jsonrpc": "2.0",
            "method": "icx_sendTransaction",
            "id": 1234,
            "params": {
                "version": "0x3",
                "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
                "to": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32",
                "stepLimit": "0x12345",
                "timestamp": "0x563a6cf330136",
                "nonce": "0x1",
                "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA=",
                "dataType": "call",
                "data": {
                    "method": "transfer",
                    "params": {
                        "to": "hxab2d8215eab14bc6bdd8bfb2c8151257032ecd8b",
                        "value": "0x1",
                        "array0": [
                            null,
                            null
                        ],
                        "array1": [
                            {
                                "hash": null,
                                "value": null
                            },
                            {
                                "hash": null,
                                "value": "0x78"
                            }
                        ]
                    }
                }
            }
        }'''

        request = json.loads(request)

        question = request["params"]
        answer = r"icx_sendTransaction.data.{method.transfer.params." \
                 r"{array0.[\0.\0].array1.[{hash.\0.value.\0}.{hash.\0.value.0x78}]." \
                 r"to.hxab2d8215eab14bc6bdd8bfb2c8151257032ecd8b.value.0x1}}." \
                 r"dataType.call.from.hxbe258ceb872e08851f1f59694dac2558708ece11.nonce.0x1.stepLimit.0x12345." \
                 r"timestamp.0x563a6cf330136.to.cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32.version.0x3"

        result = generate_origin_for_icx_send_tx_hash(question)
        self.assertEqual(result, answer)

    def test_serialize_v2_v3_compatibility(self):
        # For v2 params, verify that the results for the old hash creation logic
        # and the newly implemented hash generation logic are the same.
        # These methods are obsolete.
        # But this one and new one must have same results for v2 request.
        def create_origin_for_hash(json_data: dict):
            def gen_origin_str(json_data: dict):
                ordered_keys = list(json_data)
                ordered_keys.sort()
                for key in ordered_keys:
                    yield key
                    if isinstance(json_data[key], str):
                        yield json_data[key]
                    elif isinstance(json_data[key], dict):
                        yield from gen_origin_str(json_data[key])
                    elif isinstance(json_data[key], int):
                        yield str(json_data[key])
                    else:
                        raise TypeError(f"{key} must be one of them(dict, str, int).")

            origin = ".".join(gen_origin_str(json_data))
            return origin

        def generate_icx_hash(icx_origin_data, tx_hash_key):
            copy_tx = copy.deepcopy(icx_origin_data)
            if 'method' in copy_tx:
                del copy_tx['method']
            if 'signature' in copy_tx:
                del copy_tx['signature']
            if tx_hash_key in copy_tx:
                del copy_tx[tx_hash_key]
            origin = create_origin_for_hash(copy_tx)
            origin = f"icx_sendTransaction.{origin}"
            # gen hash
            return hashlib.sha3_256(origin.encode()).hexdigest()

        request = r'''{
            "jsonrpc": "2.0",
            "method": "icx_sendTransaction",
            "id": 1234,
            "params": {
                "version": "0x3",
                "from": "hxbe258ceb872e08851f1f59694dac2558708ece11",
                "to": "hx5bfdb090f43a808005ffc27c25b213145e80b7cd",
                "value": "0xde0b6b3a7640000",
                "timestamp": "0x563a6cf330136",
                "nonce": "0x1",
                "signature": "VAia7YZ2Ji6igKWzjR2YsGa2m53nKPrfK7uXYW78QLE+ATehAVZPC40szvAiA6NEU5gCYB4c4qaQzqDh2ugcHgA="
            }
        }'''

        request = json.loads(request)

        question = request["params"]

        result_new_hash = tbears.libs.icon_serializer.generate_icx_hash(question)
        result_old_hash = generate_icx_hash(question, "tx_hash")
        self.assertEqual(result_new_hash, result_old_hash)
