send_transaction_json = {
    "jsonrpc": "2.0", "method": "icx_sendTransaction", "id": 10889,
    "params": {
        "from": "hx0000000000000000000000000000000000000000",
        "to": "hx1000000000000000000000000000000000000000",
        "value": "0xde0b6b3a7640000", "fee": "0x2386f26fc10000",
        "timestamp": "1523327456264040",
        "tx_hash": "1b06cfef02fd6c69e38f2d3079720f2c44be94455a7e664803a4fcbc3a695802"
    }
}

give_icx_to_token_owner_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 10889,
    "params": {
        "from": "hx0000000000000000000000000000000000000000",
        "to": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "value": "0xde0b6b3a7640000",
        "fee": "0x2386f26fc10000",
        "timestamp": "1523327456264040",
        "tx_hash": "1b06cfef02fd6c69e38f2d3079720f2c44be94455a7e664803a4fcbc3a695802"
    }
}

god_balance_json = {
    "jsonrpc": "2.0",
    "method": "icx_getBalance",
    "id": 30889,
    "params": {
        "address": "hx0000000000000000000000000000000000000000"
    }
}

test_balance_json = {
    "jsonrpc": "2.0",
    "method": "icx_getBalance",
    "id": 30889,
    "params": {
        "address": "hx1000000000000000000000000000000000000000"
    }
}

token_balance_json1 = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 50889,
    "params": {
        "from": "hx1000000000000000000000000000000000000000",
        "to": "cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c",
        "data_type": "call",
        "data": {
            "method": "balance_of",
            "params": {
                "addr_from": "hx1000000000000000000000000000000000000000"
            }
        }
    }
}

token_balance_json2 = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 50889,
    "params": {
        "from": "hx0000000000000000000000000000000000000000",
        "to": "cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c",
        "data_type": "call",
        "data": {
            "method": "balance_of",
            "params": {
                "addr_from": "hx0000000000000000000000000000000000000000"
            }
        }
    }
}

token_god_balance_json = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 50889,
    "params": {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c",
        "data_type": "call",
        "data": {
            "method": "balance_of",
            "params": {
                "addr_from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            }
        }
    }
}

token_total_supply_json = {
    "jsonrpc": "2.0",
    "method": "icx_call",
    "id": 60889,
    "params": {
        "from": "hx0000000000000000000000000000000000000000",
        "to": "cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c",
        "data_type": "call",
        "data": {
            "method": "total_supply",
            "params":
                {}
        }
    }
}

token_transfer_json = {
    "jsonrpc": "2.0",
    "method": "icx_sendTransaction",
    "id": 70889,
    "params": {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "to": "cxb995b8c9c1fb9b93ad17c3b59df452dbaaa39a7c",
        "value": "0x0",
        "fee": "0x2386f26fc10000",
        "timestamp": "1523327456264040",
        "tx_hash": "1b06cfef02fd6c69e38f2d3079720f2c44be94455a7e664803a4fcbc3a695802",
        "data_type": "call",
        "data": {
            "method": "transfer",
            "params": {
                "addr_to": "hx1000000000000000000000000000000000000000",
                "value": "0x1"
            }
        }
    }
}
