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

import shutil
import unittest

from iconservice import Address

from tbears.util.test_client import send_req

from tbears.command import init_SCORE, run_SCORE, clear_SCORE, deploy_SCORE, make_SCORE_samples
from tests.common import *
from tests.test_tbears_samples import test_addr

token_owner_address = "hx4873b94352c8c1f3b2f09aaeccea31ce9e90bd31"


class TestDeployScore(unittest.TestCase):

    def tearDown(self):
        clear_SCORE()

        try:
            if os.path.exists('sample_token'):
                shutil.rmtree('sample_token')
            if os.path.exists('./.test_tbears_db'):
                shutil.rmtree('./.test_tbears_db')
            if os.path.exists('sample_crowd_sale'):
                shutil.rmtree('sample_crowd_sale')
            os.remove('./tbears.log')
        except:
            pass

    def test_call_token_score(self):
        init_SCORE('sample_token', 'SampleToken')
        run_SCORE('sample_token', None, None, TBEARS_JSON_PATH)

        exit_code, response = deploy_SCORE('sample_token', key_store_path=os.path.join(DIRECTORY_PATH, 'keystore'),
                                           password='qwer1234%')

        tx_hash = response.json()['result']
        score_address = send_req('icx_getTransactionResult', {'txHash': tx_hash}).json()['result']['scoreAddress']

        payload = get_request_json_of_token_total_supply(score_address)
        res = send_req('icx_call', payload).json()['result']

        self.assertEqual(hex(1000*10**18), res)

        payload = get_request_json_of_get_token_balance(score_address, token_owner_address)
        res = send_req('icx_call', payload).json()['result']

        self.assertEqual(hex(1000*10**18), res)

        payload = get_request_json_of_transfer_token(token_owner_address, score_address, god_address, hex(10*10**18))
        send_req('icx_sendTransaction', payload)

        payload = get_request_json_of_get_token_balance(score_address, god_address)
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(hex(10*10**18), res)

    def test_call_score_methods(self):
        make_SCORE_samples()
        run_SCORE('sample_token', None, None, TBEARS_JSON_PATH)

        exit_code, response = deploy_SCORE('sample_token', key_store_path=os.path.join(DIRECTORY_PATH, 'keystore'),
                                           password='qwer1234%')

        tx_hash = response.json()['result']
        token_score_address = send_req('icx_getTransactionResult', {'txHash': tx_hash}).json()['result']['scoreAddress']

        exit_code, response = deploy_SCORE('sample_crowd_sale', key_store_path=os.path.join(DIRECTORY_PATH, 'keystore'),
                                           password='qwer1234%', params={'token_address': token_score_address})
        tx_hash = response.json()['result']
        crowd_sale_score_address = send_req('icx_getTransactionResult',
                                            {'txHash': tx_hash}).json()['result']['scoreAddress']

        # seq1
        # genesis -> hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(token_owner) 10icx
        payload = get_request_json_of_send_icx(fr=Address.from_string(god_address),
                                               to=Address.from_string(token_owner_address),
                                               value=10 * 10 ** 18)

        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        result = send_req('icx_getTransactionResult', payload).json()['result']
        self.assertEqual(result['status'], hex(1))
        print(result)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(token_owner_address))
        res = send_req('icx_getBalance', payload).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(token_owner_address))
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        payload = get_request_json_of_transfer_token(fr=Address.from_string(token_owner_address),
                                                     to=Address.from_string(token_score_address),
                                                     addr_to=Address.from_string(crowd_sale_score_address),
                                                     value=1000 * 10 ** 18)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(crowd_sale_score_address))
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(res, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(token_owner_address),
                                               to=Address.from_string(crowd_sale_score_address),
                                               value=hex(2 * 10 ** 18))
        tx_hash = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(token_owner_address))

        res = send_req('icx_getBalance', payload).json()['result']
        self.assertEqual(res, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(token_owner_address))
        res = send_req('icx_call', payload).json()['result']
        self.assertEqual(res, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(token_owner_address),
                                               to=Address.from_string(crowd_sale_score_address),
                                               value=8 * 10 ** 18)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(god_address),
                                               to=Address.from_string(test_addr),
                                               value=90 * 10 ** 18)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_request_json_of_send_icx(fr=Address.from_string(test_addr),
                                               to=Address.from_string(crowd_sale_score_address),
                                               value=90 * 10 ** 18)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_request_json_of_check_crowd_end(fr=Address.from_string(token_owner_address),
                                                      to=Address.from_string(crowd_sale_score_address))
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq14
        # safe withrawal
        payload = get_request_json_of_crowd_withrawal(fr=token_owner_address, to=crowd_sale_score_address)
        res = send_req('icx_sendTransaction', payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        res = send_req('icx_getTransactionResult', payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        res = send_req('icx_getBalance', payload).json()['result']
        self.assertEqual(res, hex(100 * 10 ** 18))


