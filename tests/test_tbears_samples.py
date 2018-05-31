import copy
import shutil
import unittest
import os

from tbears.util import post

from tbears.command import run_SCORE, clear_SCORE, make_SCORE_samples, stop_SCORE, init_SCORE

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
        "timestamp": "0x1523327456264040",
    }
}

get_token_balance_json = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 50889,
    "params": {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf",
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
        "to": "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf",
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
        "dataType": "call",
        "data": {
            "method": "transfer",
            "params": {
                "addr_to": "cx8c814aa96fefbbb85131f87f6e0cb7878a95c1d3",
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
        "to": "cx8c814aa96fefbbb85131f87f6e0cb7878a95c1d3",
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
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
        "to": "cx8c814aa96fefbbb85131f87f6e0cb7878a95c1d3",
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "0x1523327456264040",
        "dataType": "call",
        "data": {
            "method": "safe_withdrawal",
            "params": {}
        }
    }
}
check_token_supply = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 60889,
    "params": {
        "from": "hx0000000000000000000000000000000000000000",
        "to": "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf",
        "dataType": "call",
        "data": {
            "method": "total_supply",
            "params": {}
        }
    }
}
god_address = "hx0000000000000000000000000000000000000000"
token_owner_address = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
token_score_address = "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf"
crowd_sale_score_address = "cx8c814aa96fefbbb85131f87f6e0cb7878a95c1d3"
test_addr = "hxbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
treasary_address = "hx1000000000000000000000000000000000000000"


class TestTBears(unittest.TestCase):
    def setUp(self):
        self.url = "http://localhost:9000/api/v3"
        self.send_icx_json = copy.deepcopy(send_icx_json)
        self.get_token_balance_json = copy.deepcopy(get_token_balance_json)
        self.icx_get_balance_json = copy.deepcopy(icx_get_balance_json)
        self.transfer_token_json = copy.deepcopy(transfer_token_json)
        self.check_crowd_sale_end_json = copy.deepcopy(check_crowd_sale_end_json)
        self.crowd_sale_withrawal_json = copy.deepcopy(crowd_sale_withrawal_json)
        self.check_token_supply = copy.deepcopy(check_token_supply)

    def tearDown(self):
        clear_SCORE()
        os.remove('logger.log')
        shutil.rmtree('sample_token')
        if os.path.exists('sample_crowd_sale'):
            shutil.rmtree('sample_crowd_sale')

    def test_token(self):
        init_SCORE('sample_token', 'SampleToken')
        result, _ = run_SCORE('sample_token')

        # send transaction
        self.send_icx_json['params']['from'] = god_address
        self.send_icx_json['params']['to'] = treasary_address
        self.send_icx_json['params']['value'] = hex(10*10**18)
        res = post(self.url, self.send_icx_json).json()['result']['status']
        self.assertEqual(res, 1)

        # # get balance
        self.icx_get_balance_json['params']['address'] = treasary_address
        res = post(self.url, self.icx_get_balance_json).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

        # # check token supply
        res = post(self.url, self.check_token_supply).json()['result']
        self.assertEqual(res, hex(1000*10**18))

        # check token balance
        res = post(self.url, self.get_token_balance_json).json()['result']
        self.assertEqual(res, hex(1000*10**18))

        # send token to test_addr
        self.transfer_token_json['params']['data']['params']['addr_to'] = treasary_address
        self.transfer_token_json['params']['data']['params']['value'] = hex(10*10**18)
        res = post(self.url, self.transfer_token_json).json()['result']['status']
        self.assertEqual(res, 1)

        # check token balance
        self.get_token_balance_json['params']['data']['params']['addr_from'] = treasary_address
        res = post(self.url, self.get_token_balance_json).json()['result']
        self.assertEqual(res, hex(10 * 10 ** 18))

    def test_score_methods(self):
        make_SCORE_samples()
        result, _ = run_SCORE('sample_token')
        result, _ = run_SCORE('sample_crowd_sale')
        # seq1
        # genesis -> hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(token_owner) 10icx
        res = post(self.url, self.send_icx_json).json()['result']['status']
        self.assertEqual(res, 1)

        # seq2
        # check icx balance of token_owner value : 10*10**18
        res = post(self.url, self.icx_get_balance_json).json()["result"]
        self.assertEqual(res, hex(10 * 10 ** 18))

        # seq3
        # check token balance token_owner. value : 1000*10**18
        res = post(self.url, self.get_token_balance_json).json()["result"]
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq4
        # transfer token to CrowdSale_address. value: 1000*10**18
        self.transfer_token_json['params']['from'] = token_owner_address
        self.transfer_token_json['params']['data']['params']['addr_to'] = crowd_sale_score_address

        res = post(self.url, self.transfer_token_json).json()['result']['status']
        self.assertEqual(res, 1)

        # seq5
        # check token balance of CrowdSale_address. value : 1000*10**18
        self.get_token_balance_json['params']['data']['params']['addr_from'] = crowd_sale_score_address
        res = post(self.url, self.get_token_balance_json).json()['result']
        self.assertEqual(res, hex(1000 * 10 ** 18))

        # seq6
        # check token balance of token_owner. value : 0
        self.get_token_balance_json['params']['data']['params']['addr_from'] = token_owner_address
        res = post(self.url, self.get_token_balance_json).json()['result']
        self.assertEqual(res, hex(0))

        # seq7
        # transfer icx to CrowdSale. value : 2*10**18
        self.send_icx_json['params']['from'] = token_owner_address
        self.send_icx_json['params']['to'] = crowd_sale_score_address
        self.send_icx_json['params']['value'] = hex(2 * 10 ** 18)
        res = post(self.url, self.send_icx_json).json()['result']['status']
        self.assertEqual(res, 1)

        # seq8
        # check icx balance of token_owner. value : 8*10**18
        self.icx_get_balance_json['params']['address'] = token_owner_address
        res = post(self.url, self.icx_get_balance_json).json()['result']
        self.assertEqual(res, hex(8 * 10 ** 18))

        # seq9
        # check token balance of token_owner. value : 0x2
        self.get_token_balance_json['params']['data']['params']['addr_from'] = token_owner_address
        res = post(self.url, self.get_token_balance_json).json()['result']
        self.assertEqual(res, hex(2))

        # seq10
        # transfer icx to CrowdSale. value : 8*10**18
        self.send_icx_json['params']['from'] = token_owner_address
        self.send_icx_json['params']['to'] = crowd_sale_score_address
        self.send_icx_json['params']['value'] = hex(8 * 10 ** 18)
        res = post(self.url, self.send_icx_json).json()['result']['status']
        self.assertEqual(res, 1)

        # seq11
        # genesis -> test_address. value 90*10**18
        self.send_icx_json['params']['from'] = god_address
        self.send_icx_json['params']['to'] = test_addr
        self.send_icx_json['params']['value'] = hex(90 * 10 ** 18)
        res = post(self.url, self.send_icx_json).json()['result']['status']
        self.assertEqual(res, 1)

        # seq12
        # transfer icx to CrowdSale. value : 90*10**18
        self.send_icx_json['params']['from'] = test_addr
        self.send_icx_json['params']['to'] = crowd_sale_score_address
        self.send_icx_json['params']['value'] = hex(90 * 10 ** 18)
        res = post(self.url, self.send_icx_json).json()['result']['status']
        self.assertEqual(res, 1)

        # seq13
        # check CrowdSaleEnd
        res = post(self.url, self.check_crowd_sale_end_json).json()['result']['status']
        self.assertEqual(res, 1)

        # seq14
        # safe withrawal
        res = post(self.url, self.crowd_sale_withrawal_json).json()['result']['status']
        self.assertEqual(res, 1)


        # seq15
        # check icx balance of token_owner value : 100*10**18
        self.icx_get_balance_json['params']['address'] = token_owner_address
        res = post(self.url, self.icx_get_balance_json).json()['result']
        self.assertEqual(res, hex(100 * 10 ** 18))


if __name__ == "__main__":
    unittest.main()
