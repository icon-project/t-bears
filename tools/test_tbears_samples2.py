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
import time
import unittest
import os

from iconservice import Address

from tbears.util import put_signature_to_params
from tbears.util.icx_signer import IcxSigner, key_from_key_store

from tbears.command import run_SCORE, make_SCORE_samples, deploy_SCORE, clear_SCORE
from tbears.util.test_client import send_req

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))


def get_request_json_of_call_hello():
    return {
        "jsonrpc": "2.0",
        "method": "hello",
        "id": 1,
        "params": {}
    }


def get_request_of_icx_getTransactionResult(tx_hash: str) -> dict:
    return {
        "version": "0x3",
        "txHash": tx_hash
    }


def get_request_json_of_get_icx_balance(address: str) -> dict:
    return {
        "version": "0x3",
        "address": address
    }


def get_request_json_of_send_icx(fr: str, to: str, value: str) -> dict:
    return {
        "version": "0x3",
        "from": fr,
        "to": to,
        "value": value,
        "stepLimit": "0x12345",
        "timestamp": hex(int(time.time() * 10 ** 6)),
    }


def get_request_json_of_get_token_balance(to: str, addr_from: str) -> dict:
    return {
        "version": "0x3",
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
        "version": "0x3",
        "from": fr,
        "to": to,
        "value": "0x0",
        "stepLimit": "0x12345",
        "timestamp": hex(int(time.time() * 10 ** 6)),
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
        "version": "0x3",
        "from": fr,
        "to": to,
        "value": "0x0",
        "stepLimit": "0x12345",
        "timestamp": hex(int(time.time() * 10 ** 6)),
        "dataType": "call",
        "data": {
            "method": "check_goal_reached",
            "params": {}
        }
    }


def get_request_json_of_crowd_withrawal(fr: str, to: str) -> dict:
    return {
        "version": "0x3",
        "from": fr,
        "to": to,
        "value": "0x0",
        "stepLimit": "0x12345",
        "timestamp": hex(int(time.time() * 10 ** 6)),
        "dataType": "call",
        "data": {
            "method": "safe_withdrawal",
            "params": {}
        }
    }


def get_request_json_of_token_total_supply(token_addr: str) -> dict:
    return {
        "version": "0x3",
        "from": "hx0000000000000000000000000000000000000000",
        "to": token_addr,
        "dataType": "call",
        "data": {
            "method": "total_supply",
            "params": {}
        }
    }


token_owner_address = "hx4873b94352c8c1f3b2f09aaeccea31ce9e90bd31"
god_address = "hx0000000000000000000000000000000000000000"
test_addr = "hx0133de0d928d4972e6a2656689a54fadeb5f4af5"
test_addr2 = "hx0133de0d928d4972e6a2656689a54fadeb5f4af4"
treasury_address = "hx1000000000000000000000000000000000000000"
private_key_token_owner = key_from_key_store(os.path.join(DIRECTORY_PATH, 'keystore'), 'qwer1234%')
private_key_tester = key_from_key_store(os.path.join(DIRECTORY_PATH, 'keystore2'), '1234qwer!')
token_owner_signer = IcxSigner(private_key_token_owner)
tester_signer = IcxSigner(private_key_tester)


class TestTBears(unittest.TestCase):
    def setUp(self):
        self.url = "http://localhost:9000/api/v3"

    def tearDown(self):
        clear_SCORE()

    def test_call_score_methods(self):
        make_SCORE_samples()
        run_SCORE('sample_token', None, None, None)

        exit_code, response = deploy_SCORE('sample_token', key_store_path=os.path.join(DIRECTORY_PATH, 'keystore'),
                                           password='qwer1234%')

        tx_hash = response.json()['result']
        token_score_address = send_req('icx_getTransactionResult', {'txHash': tx_hash}).json()['result']['scoreAddress']

        exit_code, response = deploy_SCORE('sample_crowd_sale', key_store_path=os.path.join(DIRECTORY_PATH, 'keystore'),
                                           password='qwer1234%', params={'token_address': token_score_address})
        tx_hash = response.json()['result']
        crowd_sale_score_address = send_req('icx_getTransactionResult',
                                            {'txHash': tx_hash}).json()['result']['scoreAddress']

        # seq0
        # genesis -> tester
        payload = get_request_json_of_send_icx(fr=god_address,
                                               to=test_addr,
                                               value=hex(1000000*10**18))
        send_req('icx_sendTransaction', payload)

        # # seq1
        # test_addr -> token_owner 10icx
        payload = get_request_json_of_send_icx(fr=test_addr,
                                               to=token_owner_address,
                                               value=10 * 10 ** 18)
        put_signature_to_params(payload, tester_signer)
        resp = send_req('icx_sendTransaction', payload)
        resp_json = resp.json()
        tx_hash = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        put_signature_to_params(payload, tester_signer)

        resp = send_req('icx_getTransactionResult', payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result['status'], hex(1))
        print(result)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(token_owner_address))
        resp = send_req('icx_getBalance', payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(token_owner_address))
        resp = send_req('icx_call', payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        payload = get_request_json_of_transfer_token(fr=token_owner_address,
                                                     to=token_score_address,
                                                     addr_to=crowd_sale_score_address,
                                                     value=hex(1000 * 10 ** 18))
        put_signature_to_params(payload, token_owner_signer)
        resp = send_req('icx_sendTransaction', payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        resp = send_req('icx_getTransactionResult', payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(crowd_sale_score_address))
        resp = send_req('icx_call', payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        resp = send_req('icx_call', payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_request_json_of_send_icx(fr=token_owner_address,
                                               to=crowd_sale_score_address,
                                               value=hex(2 * 10 ** 18))
        put_signature_to_params(payload, token_owner_signer)
        tx_hash = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        resp = send_req('icx_getTransactionResult', payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(token_owner_address))

        resp = send_req('icx_getBalance', payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(token_owner_address))
        resp = send_req('icx_call', payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_request_json_of_send_icx(fr=token_owner_address,
                                               to=crowd_sale_score_address,
                                               value=hex(8 * 10 ** 18))
        put_signature_to_params(payload, token_owner_signer)
        resp = send_req('icx_sendTransaction', payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        resp = send_req('icx_getTransactionResult', payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq11
        # test_address -> test_address2. value 90*10**18
        payload = get_request_json_of_send_icx(fr=test_addr,
                                               to=test_addr2,
                                               value=hex(90 * 10 ** 18))
        put_signature_to_params(payload, tester_signer)
        resp = send_req('icx_sendTransaction', payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        resp = send_req('icx_getTransactionResult', payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_request_json_of_send_icx(fr=test_addr,
                                               to=crowd_sale_score_address,
                                               value=hex(90 * 10 ** 18))
        put_signature_to_params(payload, tester_signer)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_request_json_of_check_crowd_end(fr=token_owner_address,
                                                      to=crowd_sale_score_address)
        put_signature_to_params(payload, token_owner_signer)
        resp = send_req('icx_sendTransaction', payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        resp = send_req('icx_getTransactionResult', payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq14
        # safe withrawal
        payload = get_request_json_of_crowd_withrawal(fr=token_owner_address, to=crowd_sale_score_address)
        put_signature_to_params(payload, token_owner_signer)
        resp = send_req('icx_sendTransaction', payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        resp = send_req('icx_getTransactionResult', payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        resp = send_req('icx_getBalance', payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
