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
import asyncio
import shutil
import unittest

from secp256k1 import PrivateKey

from tbears.command.CommandServer import CommandServer
from tbears.libs.icon_json import get_icx_sendTransaction_deploy_payload, get_icx_sendTransaction_score_payload, \
    get_icx_getBalance_payload, get_icx_getTransactionResult_payload, get_icx_call_payload, \
    get_dummy_icx_sendTransaction_payload
from tbears.util import get_deploy_contents_by_path
from tests.tbears_mock_server import API_PATH, init_mock_server

from tests.test_tbears_samples import test_addr
from tests.json_contents_for_tests import *

token_score_name = 'sample_token'
token_score_class = 'SampleToken'
crowd_score_name = 'sample_crowd_sale'


class TestDeployScore(unittest.TestCase):

    def tearDown(self):

        try:
            if os.path.exists(token_score_name):
                shutil.rmtree(token_score_name)
            if os.path.exists(crowd_score_name):
                shutil.rmtree(crowd_score_name)
            if os.path.exists('./.test_tbears_db'):
                shutil.rmtree('./.test_tbears_db')
            if os.path.exists('./.score'):
                shutil.rmtree('./.score')
            if os.path.exists('./.db'):
                shutil.rmtree('./.db')
            if os.path.exists('./tbears.json'):
                os.remove('./tbears.json')
            os.remove('./tbears.log')
        except:
            pass

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.path = API_PATH
        self.app = init_mock_server()
        self.private_key_token_owner = PrivateKey().private_key
        self.signer_token_owner = IcxSigner(self.private_key_token_owner)
        self.token_owner_address = f'hx{self.signer_token_owner.address.hex()}'

        self.private_key_user = PrivateKey().private_key
        self.signer_user = IcxSigner(self.private_key_user)
        self.user_address = f'hx{self.signer_user.address.hex()}'

    def test_call_token_score(self):
        CommandServer.init(token_score_name, token_score_class)

        deploy_contents = get_deploy_contents_by_path(token_score_name)

        deploy_payload = get_icx_sendTransaction_deploy_payload(self.signer_token_owner, deploy_contents)
        _, response = self.app.test_client.post(self.path, json=deploy_payload)
        res_json = response.json
        tx_hash = res_json['result']

        transaction_result_payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)

        _, response = self.app.test_client.post(self.path, json=transaction_result_payload)
        score_address = response.json['result']['scoreAddress']
        payload = get_icx_call_payload(score_address, score_address, score_method='total_supply')
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']

        self.assertEqual(hex(1000 * 10 ** 18), result)

        method_n_params = get_params_for_get_token_balance(self.token_owner_address)
        payload = get_icx_call_payload(self.token_owner_address, score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']

        self.assertEqual(hex(1000 * 10 ** 18), result)

        method_n_params = get_params_for_transfer_token(god_address, hex(10*10**18))
        payload = get_icx_sendTransaction_score_payload(self.signer_token_owner, score_address, hex(0),
                                                        *method_n_params)
        self.app.test_client.post(self.path, json=payload)

        method_n_params = get_params_for_get_token_balance(god_address)
        payload = get_icx_call_payload(self.user_address, score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(hex(10 * 10 ** 18), result)

    def test_call_score_methods(self):
        CommandServer.make_samples()

        deploy_contents = get_deploy_contents_by_path(token_score_name)

        deploy_payload = get_icx_sendTransaction_deploy_payload(self.signer_token_owner, deploy_contents)
        _, response = self.app.test_client.post(self.path, json=deploy_payload)
        response_json = response.json
        tx_hash = response_json['result']
        transaction_result_payload = get_icx_getTransactionResult_payload(tx_hash)

        _, response = self.app.test_client.post(self.path, json=transaction_result_payload)
        response_json = response.json
        token_score_address = response_json['result']['scoreAddress']

        deploy_contents = get_deploy_contents_by_path(crowd_score_name)

        crowd_deploy_payload = get_icx_sendTransaction_deploy_payload(self.signer_token_owner, deploy_contents,
                                                                      deploy_params={'token_address':
                                                                                         token_score_address})
        _, response = self.app.test_client.post(self.path, json=crowd_deploy_payload)
        response_json = response.json
        tx_hash = response_json['result']

        transaction_result_payload = get_icx_getTransactionResult_payload(tx_hash)
        _, response = self.app.test_client.post(self.path, json=transaction_result_payload)
        response_json = response.json
        crowd_sale_score_address = response_json['result']['scoreAddress']

        # seq1
        # genesis -> token_owner 10icx
        payload = get_dummy_icx_sendTransaction_payload(god_address, self.token_owner_address, hex(10*10**18))

        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result['status'], hex(1))

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_icx_getBalance_payload(self.token_owner_address)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        method_n_params = get_params_for_get_token_balance(self.token_owner_address)
        payload = get_icx_call_payload(self.token_owner_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        method_n_params = get_params_for_transfer_token(crowd_sale_score_address, hex(1000*10**18))
        payload = get_icx_sendTransaction_score_payload(self.signer_token_owner, token_score_address, hex(0),
                                                        *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=result)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        method_n_params = get_params_for_get_token_balance(crowd_sale_score_address)
        payload = get_icx_call_payload(self.token_owner_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        method_n_params = get_params_for_get_token_balance(self.token_owner_address)
        payload = get_icx_call_payload(self.token_owner_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_dummy_icx_sendTransaction_payload(fr=self.token_owner_address,
                                                        to=crowd_sale_score_address, value=hex(2 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_icx_getBalance_payload(address=self.token_owner_address)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_icx_call_payload(self.token_owner_address, token_score_address, *method_n_params)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_dummy_icx_sendTransaction_payload(self.token_owner_address, crowd_sale_score_address,
                                                        hex(8*10**18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq11
        # genesis -> test_address. value 90*10**18
        payload = get_dummy_icx_sendTransaction_payload(fr=god_address, to=test_addr, value=hex(90 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_dummy_icx_sendTransaction_payload(fr=test_addr,
                                                       to=crowd_sale_score_address, value=hex(90 * 10 ** 18))
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)

        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_dummy_icx_sendTransaction_payload(self.token_owner_address, crowd_sale_score_address, hex(0),
                                                        data_type='call', data={'method': 'check_goal_reached',
                                                                                "params": {}})
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq14
        # safe withrawal
        payload = get_dummy_icx_sendTransaction_payload(self.token_owner_address, crowd_sale_score_address, hex(0),
                                                        data_type='call', data={'method': 'safe_withdrawal',
                                                                                'params': {}})
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        tx_hash = response_json['result']
        payload = get_icx_getTransactionResult_payload(tx_hash=tx_hash)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_icx_getBalance_payload(address=self.token_owner_address)
        _, response = self.app.test_client.post(self.path, json=payload)
        response_json = response.json
        result = response_json['result']
        self.assertEqual(result, hex(100 * 10 ** 18))
