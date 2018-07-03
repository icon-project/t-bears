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

from tbears.util.icon_client import IconClient, get_deploy_payload
from tbears.util.icx_signer import key_from_key_store, IcxSigner
from tests.sample_test_client import send_req

from tbears.command import init_SCORE, run_SCORE, clear_SCORE, make_SCORE_samples
from tests.common import *
from tests.test_tbears_samples import test_addr

token_owner_address = "hx4873b94352c8c1f3b2f09aaeccea31ce9e90bd31"
token_owner_private_key = key_from_key_store(os.path.join(DIRECTORY_PATH, 'keystore'), 'qwer1234%')
token_score_name = 'sample_token'
token_score_class = 'SampleToken'
crowd_score_name = 'sample_crowd_sale'


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

    def setUp(self):
        self.url = URL
        self.token_owner_private_key = IcxSigner(token_owner_private_key)
        self.icon_client_token_owner = IconClient(self.url, version=3, private_key=token_owner_private_key)

    def test_call_token_score(self):
        token_score_name = 'sample_token'
        token_score_class = 'SampleToken'
        init_SCORE(token_score_name, token_score_class)
        run_SCORE(token_score_name, None, None, TBEARS_JSON_PATH)

        deploy_payload = get_deploy_payload(token_score_name, self.token_owner_private_key)
        response = self.icon_client_token_owner.send(SEND, deploy_payload)
        res_json = response.json()
        tx_hash = res_json['result']

        transaction_result_payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)

        response = self.icon_client_token_owner.send(TX_RESULT, transaction_result_payload)
        score_address = response.json()['result']['scoreAddress']
        payload = get_request_json_of_token_total_supply(score_address)

        response = self.icon_client_token_owner.send(CALL, payload)
        response_json = response.json()
        result = response_json['result']

        self.assertEqual(hex(1000 * 10 ** 18), result)

        payload = get_request_json_of_get_token_balance(score_address, token_owner_address)
        response = self.icon_client_token_owner.send(CALL, payload)
        response_json = response.json()
        result = response_json['result']

        self.assertEqual(hex(1000 * 10 ** 18), result)

        payload = get_request_json_of_transfer_token(token_owner_address, score_address, god_address,
                                                     hex(10 * 10 ** 18))
        self.icon_client_token_owner.send(SEND, payload)

        payload = get_request_json_of_get_token_balance(score_address, god_address)
        response = self.icon_client_token_owner.send(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(hex(10 * 10 ** 18), result)

    def test_call_score_methods(self):
        make_SCORE_samples()
        run_SCORE('sample_token', None, None, TBEARS_JSON_PATH)

        deploy_payload = get_deploy_payload(token_score_name, self.token_owner_private_key)
        response = self.icon_client_token_owner.send(SEND, deploy_payload)
        response_json = response.json()
        tx_hash = response_json['result']
        transaction_result_payload = get_request_of_icx_getTransactionResult(tx_hash)

        response = self.icon_client_token_owner.send(TX_RESULT, transaction_result_payload)
        response_json = response.json()
        token_score_address = response_json['result']['scoreAddress']

        crowd_deploy_payload = get_deploy_payload(crowd_score_name, self.token_owner_private_key,
                                                  params={'token_address': token_score_address})
        response = self.icon_client_token_owner.send(SEND, crowd_deploy_payload)
        response_json = response.json()
        tx_hash = response_json['result']

        transaction_result_payload = get_request_of_icx_getTransactionResult(tx_hash)
        response = self.icon_client_token_owner.send(TX_RESULT,
                                                     transaction_result_payload)
        response_json = response.json()
        crowd_sale_score_address = response_json['result']['scoreAddress']

        # seq1
        # genesis -> token_owner 10icx
        payload = get_request_json_of_send_icx(fr=god_address,
                                               to=token_owner_address,
                                               value=hex(10 * 10 ** 18))

        response = self.icon_client_token_owner.send(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = self.icon_client_token_owner.send(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result['status'], hex(1))

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        response = self.icon_client_token_owner.send(BAL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=token_score_address,
                                                        addr_from=token_owner_address)
        response = self.icon_client_token_owner.send(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        payload = get_request_json_of_transfer_token(fr=token_owner_address,
                                                     to=token_score_address,
                                                     addr_to=crowd_sale_score_address,
                                                     value=hex(1000 * 10 ** 18))
        response = self.icon_client_token_owner.send(SEND, payload)
        response_json = response.json()
        result = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        response = self.icon_client_token_owner.send(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=token_score_address,
                                                        addr_from=crowd_sale_score_address)
        response = self.icon_client_token_owner.send(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=token_owner_address)
        response = self.icon_client_token_owner.send(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_request_json_of_send_icx(fr=token_owner_address,
                                               to=crowd_sale_score_address,
                                               value=hex(2 * 10 ** 18))
        response = self.icon_client_token_owner.send(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = self.icon_client_token_owner.send(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)

        response = self.icon_client_token_owner.send(BAL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_request_json_of_get_token_balance(to=token_score_address,
                                                        addr_from=token_owner_address)
        response = self.icon_client_token_owner.send(CALL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_request_json_of_send_icx(fr=token_owner_address,
                                               to=crowd_sale_score_address,
                                               value=8 * 10 ** 18)
        response = self.icon_client_token_owner.send(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = self.icon_client_token_owner.send(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        payload = get_request_json_of_send_icx(fr=god_address,
                                               to=test_addr,
                                               value=hex(90 * 10 ** 18))
        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = self.icon_client_token_owner.send(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_request_json_of_send_icx(fr=test_addr,
                                               to=crowd_sale_score_address,
                                               value=hex(90 * 10 ** 18))
        response = send_req(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)

        response = self.icon_client_token_owner.send(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_request_json_of_check_crowd_end(fr=token_owner_address,
                                                      to=crowd_sale_score_address)
        response = self.icon_client_token_owner.send(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = self.icon_client_token_owner.send(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # # seq14
        # safe withrawal
        payload = get_request_json_of_crowd_withrawal(fr=token_owner_address, to=crowd_sale_score_address)
        response = self.icon_client_token_owner.send(SEND, payload)
        response_json = response.json()
        tx_hash = response_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        response = self.icon_client_token_owner.send(TX_RESULT, payload)
        response_json = response.json()
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_request_json_of_get_icx_balance(address=token_owner_address)
        response = self.icon_client_token_owner.send(BAL, payload)
        response_json = response.json()
        result = response_json['result']
        self.assertEqual(result, hex(100 * 10 ** 18))
