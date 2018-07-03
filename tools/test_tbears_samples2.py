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
import unittest
from time import sleep

from iconservice import Address

from tbears.util.icon_client import IconClient

from tbears.command import make_SCORE_samples, deploy_SCORE
from tests.common import *
from tests.sample_test_client import send_req

TOOLS_DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))

test_addr = "hx0133de0d928d4972e6a2656689a54fadeb5f4af5"
test_addr2 = "hx0133de0d928d4972e6a2656689a54fadeb5f4af4"


class TestTBears(unittest.TestCase):

    def setUp(self):
        self.url = URL
        self.version = 3
        self.icon_client_token_owner = IconClient(self.url, self.version, deploy_token_owner_private_key)

    def test_call_score_methods(self):
        make_SCORE_samples()

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
                                               to=deploy_token_owner_address,
                                               value=10 * 10 ** 18)
        resp = self.icon_client_token_owner.send(SEND, payload)
        resp_json = resp.json()
        tx_hash = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)

        sleep(3)
        resp = self.icon_client_token_owner.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result['status'], hex(1))
        print(result)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(deploy_token_owner_address))
        resp = self.icon_client_token_owner.send(BAL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(10 * 10 ** 18))

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
        resp = self.icon_client_token_owner.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        sleep(3)
        resp = send_req(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(crowd_sale_score_address))
        resp = self.icon_client_token_owner.send(CALL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        payload = get_request_json_of_get_token_balance(to=token_score_address, addr_from=deploy_token_owner_address)
        resp = self.icon_client_token_owner.send(CALL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        payload = get_request_json_of_send_icx(fr=deploy_token_owner_address,
                                               to=crowd_sale_score_address,
                                               value=hex(2 * 10 ** 18))
        tx_hash = self.icon_client_token_owner.send(SEND, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=tx_hash)
        sleep(3)
        resp = self.icon_client_token_owner.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        payload = get_request_json_of_get_icx_balance(address=Address.from_string(deploy_token_owner_address))

        resp = self.icon_client_token_owner.send(BAL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        payload = get_request_json_of_get_token_balance(to=Address.from_string(token_score_address),
                                                        addr_from=Address.from_string(deploy_token_owner_address))
        resp = self.icon_client_token_owner.send(CALL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        payload = get_request_json_of_send_icx(fr=deploy_token_owner_address,
                                               to=crowd_sale_score_address,
                                               value=hex(8 * 10 ** 18))
        resp = self.icon_client_token_owner.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        sleep(3)
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
        resp = self.icon_client_token_owner.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        sleep(3)
        resp = self.icon_client_token_owner.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        payload = get_request_json_of_send_icx(fr=test_addr,
                                               to=crowd_sale_score_address,
                                               value=hex(90 * 10 ** 18))
        res = self.icon_client_token_owner.send(SEND, payload).json()['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=res)
        sleep(3)
        res = self.icon_client_token_owner.send(TX_RESULT, payload).json()['result']['status']
        self.assertEqual(res, hex(1))

        # seq13
        # check CrowdSaleEnd
        payload = get_request_json_of_check_crowd_end(fr=deploy_token_owner_address,
                                                      to=crowd_sale_score_address)
        resp = self.icon_client_token_owner.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        sleep(3)
        resp = self.icon_client_token_owner.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq14
        # safe withrawal
        payload = get_request_json_of_crowd_withrawal(fr=deploy_token_owner_address, to=crowd_sale_score_address)
        resp = self.icon_client_token_owner.send(SEND, payload)
        resp_json = resp.json()
        result = resp_json['result']
        payload = get_request_of_icx_getTransactionResult(tx_hash=result)
        sleep(3)
        resp = self.icon_client_token_owner.send(TX_RESULT, payload)
        resp_json = resp.json()
        result = resp_json['result']
        status = result['status']
        self.assertEqual(status, hex(1))

        # seq15
        # check icx balance of token_owner value : 100*10**18
        payload = get_request_json_of_get_icx_balance(address=deploy_token_owner_address)
        resp = self.icon_client_token_owner.send(BAL, payload)
        resp_json = resp.json()
        result = resp_json['result']
        self.assertEqual(result, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
