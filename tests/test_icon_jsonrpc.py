# -*- coding: utf-8 -*-
# Copyright 2017-2018 ICON Foundation
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
import unittest
import time

from secp256k1 import PrivateKey

from tbears.libs.icon_jsonrpc import IconJsonrpc
from tests.test_util.jsonschema_validator import validate_jsonschema_v3
from tests.test_util import TEST_UTIL_DIRECTORY


class TestIconJsonrpcV3(unittest.TestCase):
    def setUp(self):
        self.validator = validate_jsonschema_v3

    def check_jsonschema_validation(self, request: dict, raised: bool = False, version: int=3):
        try:
            self.validator(request=request)
        except:
            exception_raised = True
        else:
            exception_raised = False
        self.assertEqual(exception_raised, raised)

    def check_key_value(self, org: dict, result: dict):
        for k, v in org.items():
            self.assertTrue(k in result)
            self.assertEqual(v, result[k])

    def test_from_string(self):
        addr = f'hx{"0"*40}'
        from_str = IconJsonrpc.from_string(addr)
        self.assertFalse(from_str.signer)
        self.assertEqual(addr, from_str.address)

    def test_gen_call_data(self):
        data = {
            "method": "transfer",
            "params": {
                "to": "hxto",
                "value": int(1e18)
            }
        }
        gen_data = IconJsonrpc.gen_call_data(method=data['method'], params=data['params'])
        self.assertEqual(data, gen_data)

        # check default params
        gen_data = IconJsonrpc.gen_call_data(method=data['method'])
        self.assertEqual(data['method'], gen_data['method'])
        self.assertEqual({}, gen_data['params'])

    def test_gen_deploy_data(self):
        data = {
            "contentType": "contentType",
            "content": "content",
            "params": {
                "initialSuppliy": 0x10000,
                "decimals": 18
            }
        }
        gen_data = IconJsonrpc.gen_deploy_data(content=data['content'],
                                               content_type=data['contentType'],
                                               params=data['params'])
        self.assertEqual(data, gen_data)

        # check default values
        gen_data = IconJsonrpc.gen_deploy_data(content=data['content'])
        self.assertEqual(data['content'], gen_data['content'])
        self.assertEqual("application/zip", gen_data['contentType'])
        self.assertEqual({}, gen_data['params'])

    def test_getLastBlock(self):
        request = IconJsonrpc.getLastBlock()
        self.check_jsonschema_validation(request=request)

    def test_getBlockByHeight(self):
        request = IconJsonrpc.getBlockByHeight("2")
        self.check_jsonschema_validation(request=request)
        request = IconJsonrpc.getBlockByHeight("0x2")
        self.check_jsonschema_validation(request=request)

    def test_getBlockByHash(self):
        txHash = '0x43de4f25a41cb8cd09b0478300ce8da24191f1602e54b6db2ce6274311556164'
        request = IconJsonrpc.getBlockByHash(txHash)
        self.check_jsonschema_validation(request=request)

    def test_getBalance(self):
        addr = f'hx{"0"*40}'
        request = IconJsonrpc.getBalance(address=addr)
        self.check_jsonschema_validation(request=request)

    def test_ScoreApi(self):
        addr = f'cx{"0"*40}'
        request = IconJsonrpc.getScoreApi(score_address=addr)
        self.check_jsonschema_validation(request=request)

    def test_getTotalSupply(self):
        request = IconJsonrpc.getTotalSupply()
        self.check_jsonschema_validation(request=request)

    def test_getTransactionResult(self):
        txHash = '0x43de4f25a41cb8cd09b0478300ce8da24191f1602e54b6db2ce6274311556164'
        request = IconJsonrpc.getTransactionResult(txHash)
        self.check_jsonschema_validation(request=request)

    def test_getTransactionByHash(self):
        txHash = '0x43de4f25a41cb8cd09b0478300ce8da24191f1602e54b6db2ce6274311556164'
        request = IconJsonrpc.getTransactionByHash(txHash)
        self.check_jsonschema_validation(request=request)

    def test_sendTransaction(self):
        # IconJsonrpc object from string
        addr = f'hx{"0"*40}'
        from_str = IconJsonrpc.from_string(addr)

        icon_jsonrpc_objs = [from_str]

        request_template = {
            "to": f'hx{"a"*40}',
            "version": hex(3),
            "value": hex(int(1e10)),
            "stepLimit": hex(0x2000),
            "nid": hex(3),
            "nonce": hex(1),
            "timestamp": hex(int(time.time() * 10 ** 6))
        }
        """
        test transfer
        """
        for obj in icon_jsonrpc_objs:
            self.check_sendTransaction(obj, request_template)

        """
        test dataType 'call'
        """
        request_template["dataType"] = 'call'
        request_template["data"] = {
            "method": "transfer",
            "params": {
                "to": "hxto",
                "value": hex(0x10)
            }
        }
        for obj in icon_jsonrpc_objs:
            self.check_sendTransaction(obj, request_template)

        """
        test dataType 'deploy'
        """
        request_template["dataType"] = 'deploy'
        request_template["data"] = {
            "contentType": "application/zip",
            "content": "0xcontent",
            "params": {
                "on_install": "need_param?",
                "on_update": "need_param?",
            }
        }
        for obj in icon_jsonrpc_objs:
            self.check_sendTransaction(obj, request_template)

        """
        test dataType 'message'
        """
        request_template["dataType"] = 'message'
        request_template["data"] = "0xmessage"

        for obj in icon_jsonrpc_objs:
            self.check_sendTransaction(obj, request_template)

    def check_sendTransaction(self, icon_jsonrpc: 'IconJsonrpc', org_data: dict):
        if 'data' in org_data:
            request = icon_jsonrpc.sendTransaction(to=org_data['to'],
                                                   version=org_data['version'],
                                                   value=org_data['value'],
                                                   step_limit=org_data['stepLimit'],
                                                   nid=org_data['nid'],
                                                   nonce=org_data['nonce'],
                                                   timestamp=org_data['timestamp'],
                                                   data_type=org_data['dataType'],
                                                   data=org_data['data'])
        else:
            request = icon_jsonrpc.sendTransaction(to=org_data['to'],
                                                   version=org_data['version'],
                                                   value=org_data['value'],
                                                   step_limit=org_data['stepLimit'],
                                                   nid=org_data['nid'],
                                                   nonce=org_data['nonce'],
                                                   timestamp=org_data['timestamp'])
        self.check_jsonschema_validation(request=request)
        self.assertEqual(icon_jsonrpc.address, request['params']['from'])
        self.check_key_value(org_data, request['params'])
