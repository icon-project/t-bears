import unittest
import os

from tbears.util import post

from tbears.command import run_SCORE, clear_SCORE, make_SCORE_samples

DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))

send_icx_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 10889,
    "params": {
        "from": "hx0000000000000000000000000000000000000000",
        "to": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "value": "0x8ac7230489e80000",
        "fee": "0x2386f26fc10000",
        "timestamp": "1523327456264040",
        "txHash": "1b06cfef02fd6c69e38f2d3079720f2c44be94455a7e664803a4fcbc3a695802"
    }
}

get_token_balance_json = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 50889,
    "params": {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c",
        "dataType": "call",
        "data": {
            "method": "balance_of",
            "params": {
                "addr_from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            }
        }
    }
}

icx_get_balance_json = {
    "jsonrpc": "2.0",
    "method": "icx_getBalance",
    "id": 30889,
    "params": {
        "address": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
}

transfer_token_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 110889,
    "params": {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c",
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "1523327456264040",
        "txHash": "1b06cfef02fd6c69e38f2d3079720f2c44be94455a7e664803a4fcbc3a695802",
        "dataType": "call",
        "data": {
            "method": "transfer",
            "params": {
                "addr_to": "cxae84227f0e977397994ffd00aec9e6b65b78a050",
                "value": "0x3635c9adc5dea00000"
            }
        }
    }
}

check_crowd_sale_end_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 200889,
    "params": {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cxae84227f0e977397994ffd00aec9e6b65b78a050",
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "1523327456264040",
        "txHash": "1b06cfef02fd6c69e38f2d3079720f2c44be94455a7e664803a4fcbc3a695802",
        "dataType": "call",
        "data": {
            "method": "check_goal_reached",
            "params": {}
        }
    }
}

crowd_sale_withrawal_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 210889,
    "params": {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cxae84227f0e977397994ffd00aec9e6b65b78a050",
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "1523327456264040",
        "txHash": "1b06cfef02fd6c69e38f2d3079720f2c44be94455a7e664803a4fcbc3a695802",
        "dataType": "call",
        "data": {
            "method": "safe_withdrawal",
            "params": {}
        }
    }
}
god_address = "hx0000000000000000000000000000000000000000"
token_owner_address = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
token_score_address = "cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c"
crowd_sale_score_address = "cxae84227f0e977397994ffd00aec9e6b65b78a050"
test_addr = "hxbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


class TestTBears(unittest.TestCase):
    def setUp(self):
        self.url = "http://localhost:9000/api/v3"

    def tearDown(self):
        clear_SCORE()

    def test_score_methods(self):
        make_SCORE_samples()
        result, _ = run_SCORE('tokentest')
        result, _ = run_SCORE('sampleCrowdSale')
        # seq1
        # genesis -> hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(token_owner) 10icx
        post(self.url, send_icx_json)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        res = post(self.url, icx_get_balance_json).json()["result"]
        self.assertEqual(res, hex(10*10**18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        res = post(self.url, get_token_balance_json).json()["result"]
        self.assertEqual(res, hex(1000*10**18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        transfer_token_json['params']['from'] = token_owner_address
        transfer_token_json['params']['data']['params']['addr_to'] = crowd_sale_score_address

        post(self.url, transfer_token_json)

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        get_token_balance_json['params']['data']['params']['addr_from'] = crowd_sale_score_address
        res = post(self.url, get_token_balance_json).json()['result']
        self.assertEqual(res, hex(1000*10**18))

        # seq6
        # check token balance of token_owner. value : 0
        get_token_balance_json['params']['data']['params']['addr_from'] = token_owner_address
        res = post(self.url, get_token_balance_json).json()['result']
        self.assertEqual(res, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        send_icx_json['params']['from'] = token_owner_address
        send_icx_json['params']['to'] = crowd_sale_score_address
        send_icx_json['params']['value'] = hex(2*10**18)
        post(self.url, send_icx_json)

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        icx_get_balance_json['params']['address'] = token_owner_address
        res = post(self.url, icx_get_balance_json).json()['result']
        self.assertEqual(res, hex(8*10**18))

        # seq9
        # check token balance of token_owner. value : 0x2
        get_token_balance_json['params']['data']['params']['addr_from'] = token_owner_address
        res = post(self.url, get_token_balance_json).json()['result']
        self.assertEqual(res, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        send_icx_json['params']['from'] = token_owner_address
        send_icx_json['params']['to'] = crowd_sale_score_address
        send_icx_json['params']['value'] = hex(8*10**18)
        post(self.url, send_icx_json)

        # seq11
        # genesis -> test_address. value 90*10**18
        send_icx_json['params']['from'] = god_address
        send_icx_json['params']['to'] = test_addr
        send_icx_json['params']['value'] = hex(90 * 10 ** 18)
        post(self.url, send_icx_json)

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        send_icx_json['params']['from'] = test_addr
        send_icx_json['params']['to'] = crowd_sale_score_address
        send_icx_json['params']['value'] = hex(90 * 10 ** 18)
        post(self.url, send_icx_json)

        # seq13
        # check CrowdSaleEnd
        post(self.url, check_crowd_sale_end_json)

        # seq14
        # safe withrawal
        post(self.url, crowd_sale_withrawal_json)

        # seq15
        # check icx balance of token_owner value : 100*10**18
        icx_get_balance_json['params']['address'] = token_owner_address
        res = post(self.url, icx_get_balance_json).json()['result']
        self.assertEqual(res, hex(100*10**18))


if __name__ == "__main__":
    unittest.main()
