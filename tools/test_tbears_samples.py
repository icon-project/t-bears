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
import os
import time
import unittest

import requests

from tbears.command import make_SCORE_samples, deploy_SCORE
from tbears.util.icx_signer import key_from_key_store, IcxSigner

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))
god_address = f'hx{"0" * 40 }'
test_addr = "hx0133de0d928d4972e6a2656689a54fadeb5f4af5"
test_addr2 = "hx0133de0d928d4972e6a2656689a54fadeb5f4af4"
URL = 'http://localhost:9000/api/v3'
deploy_token_owner_private_key = key_from_key_store(
    os.path.join(DIRECTORY_PATH, 'keystore'), 'qwer1234%')
token_owner_signer = IcxSigner(deploy_token_owner_private_key)
deploy_token_owner_address = f'hx{token_owner_signer.address.hex()}'


class IconClient(object):
    def __init__(self, url: str, version: int, private_key: bytes):
        self._url = url
        self._version = version
        self._private_key = private_key
        self._signer = IcxSigner(self._private_key)

    def send(self, method: str, params: dict) -> requests.Response:
        content: dict = self._get_content(method, params)

        payload = json.dumps(content)
        res = requests.post(self._url, payload)
        return res

    def transfer(self, from_: str, to: str, value: int) -> requests.Response:
        method = 'icx_sendTransaction'
        params = {
            'from': from_,
            'to': to,
            'value': value,
            'stepLimit': 10000
        }

        return self.send(method, params)

    def _get_content(self, method: str, params: dict) -> dict:
        if self._version >= 3:
            params['version'] = hex(self._version)

        if method == 'icx_sendTransaction':
            timestamp = int(time.time() * 10 ** 6)
            params['timestamp'] = hex(timestamp)

        self._convert_params(params)

        content = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 12345,
            'params': params
        }

        return content

    @staticmethod
    def _convert_params(params: dict):
        int_keys = ('value', 'nonce', 'stepLimit')
        for key in int_keys:
            if key in params and isinstance(params[key], int):
                params[key] = hex(params[key])


class TestTBears(unittest.TestCase):

    def setUp(self):
        self.url = URL
        self.timeout = 0
        self.version = 3
        self.icon_client = IconClient(
            self.url, self.version, deploy_token_owner_private_key)

    def test_call_score_methods(self):
        make_SCORE_samples()

        # seq0
        # genesis send 1,000,000 icx to tester
        params = {
            'from': god_address,
            'to': deploy_token_owner_address,
            'value': 1000000 * 10 ** 18,
            'stepLimit': 10000
        }
        res = self.icon_client.send('icx_sendTransaction', params)
        content = res.json()
        self.assertTrue('result' in content)

        exit_code, res = deploy_SCORE(
            'sample_token',
            key_store_path=os.path.join(DIRECTORY_PATH, 'keystore'),
            password='qwer1234%')
        content = res.json()

        time.sleep(self.timeout)

        tx_hash = content['result']
        params = {'txHash': tx_hash}
        res = self.icon_client.send('icx_getTransactionResult', params)
        content = res.json()
        token_score_address = content['result']['scoreAddress']

        time.sleep(self.timeout)

        exit_code, response = deploy_SCORE(
            'sample_crowd_sale',
            key_store_path=os.path.join(DIRECTORY_PATH, 'keystore'),
            password='qwer1234%',
            params={'token_address': token_score_address})

        tx_hash = response.json()['result']
        params = {'txHash': tx_hash}
        res = self.icon_client.send('icx_getTransactionResult', params)
        content = res.json()
        crowd_sale_score_address = content['result']['scoreAddress']

        time.sleep(self.timeout)

        # seq0
        # genesis send 1,000,000 icx to tester
        params = {
            'from': god_address,
            'to': test_addr,
            'value': 1000000 * 10 ** 18,
            'stepLimit': 10000
        }
        res = self.icon_client.send('icx_sendTransaction', params)
        content = res.json()
        self.assertTrue('result' in content)

        time.sleep(self.timeout)

        # # seq1
        # test_addr -> token_owner 10icx
        params = {
            'from': test_addr,
            'to': deploy_token_owner_address,
            'value': 10 * 10 ** 18,
            'stepLimit': 10000
        }
        res = self.icon_client.send('icx_sendTransaction', params)
        content = res.json()
        self.assertTrue('result' in content)

        time.sleep(self.timeout)

        tx_hash = content['result']
        params = {'txHash': tx_hash}
        res = self.icon_client.send('icx_getTransactionResult', params)
        content = res.json()
        self.assertTrue('result' in content)
        tx_result = content['result']
        self.assertEqual('0x1', tx_result['status'])

        # seq2
        # check icx balance of token_owner value : 10*10**18
        params = {'address': deploy_token_owner_address}
        res = self.icon_client.send('icx_getBalance', params)
        content = res.json()
        result = content['result']
        self.assertEqual(hex(10 * 10 ** 18), result)

        """
        # seq3
        # check token balance token_owner. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(deploy_token_owner_address))
        resp = send_req(CALL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        payload = get_request_json_of_transfer_token(fr=deploy_token_owner_address,
                                                     to=token_score_address,
                                                     addr_to=crowd_sale_score_address,
                                                     value=hex(1000 * 10 ** 18))
        resp = self.client.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        time.sleep(3)
        resp = send_req(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(crowd_sale_score_address))
        resp = self.client.send(CALL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=deploy_token_owner_address)
        resp = self.client.send(CALL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_request_json_of_send_icx(fr=deploy_token_owner_address,
                                               to=crowd_sale_score_address,
                                               value=hex(2 * 10 ** 18))
        tx_hash = self.client.send(SEND, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        time.sleep(3)
        resp = self.client.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(deploy_token_owner_address))

        resp = self.client.send(BAL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(deploy_token_owner_address))
        resp = self.client.send(CALL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_request_json_of_send_icx(fr=deploy_token_owner_address,
                                               to=crowd_sale_score_address,
                                               value=hex(8 * 10 ** 18))
        resp = self.client.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        time.sleep(3)
        resp = send_req(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq11
        # test_address -> test_address2. value 90*10**18
        payload = get_request_json_of_send_icx(fr=test_addr,
                                               to=test_addr2,
                                               value=hex(90 * 10 ** 18))
        resp = self.client.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        time.sleep(3)
        resp = self.client.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_request_json_of_send_icx(fr=test_addr,
                                               to=crowd_sale_score_address,
                                               value=hex(90 * 10 ** 18))
        res = self.client.send(SEND, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        time.sleep(3)
        res = self.client.send(TX_RESULT, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_request_json_of_check_crowd_end(fr=deploy_token_owner_address,
                                                      to=crowd_sale_score_address)
        resp = self.client.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        time.sleep(3)
        resp = self.client.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq14
        # safe withrawal
        payload = get_request_json_of_crowd_withrawal(fr=deploy_token_owner_address, to=crowd_sale_score_address)
        resp = self.client.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        time.sleep(3)
        resp = self.client.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_request_json_of_get_icx_balance(address=deploy_token_owner_address)
        resp = self.client.send(BAL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(100 * 10 ** 18))
        """


if __name__ == "__main__":
    unittest.main()
