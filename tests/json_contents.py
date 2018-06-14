def get_request_json_of_call_hello():
    return {
        "jsonrpc": "2.0",
        "method": "hello",
        "id": 1,
        "params": {}
    }


def get_request_of_icx_getTransactionResult(tx_hash: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 40889,
        "method": "icx_getTransactionResult",
        "params": {"txHash": tx_hash}
    }


def get_request_json_of_get_icx_balance(address: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_getBalance",
        "id": 30889,
        "params": {
            "address": address
        }
    }


def get_request_json_of_send_icx(fr: str, to: str, value: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 10889,
        "params": {
            "from": fr,
            "to": to,
            "value": value,
            "fee": "0x2386f26fc10000",
            "timestamp": "0x1523327456264040",
        }
    }


def get_request_json_of_get_score_api(to: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_getScoreApi",
        "id": 50889,
        "params": {
            "from": "hx0000000000000000000000000000000000000000",
            "to": to
        }
    }


def get_request_json_of_get_token_balance(to: str, addr_from: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_call",
        "id": 50889,
        "params": {
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
    }


def get_request_json_of_transfer_token(fr: str, to: str, addr_to: str, value: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 110889,
        "params": {
            "from": fr,
            "to": to,
            "value": "0x0",
            "fee": "0x2386f26fc10000",
            "timestamp": "0x1523327456264040",
            "dataType": "call",
            "data": {
                "method": "transfer",
                "params": {
                    "addr_to": addr_to,
                    "value": value
                }
            }
        }
    }


def get_request_json_of_check_crowd_end(fr: str, to: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 200889,
        "params": {
            "from": fr,
            "to": to,
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


def get_request_json_of_crowd_withrawal(fr: str, to: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_sendTransaction",
        "id": 210889,
        "params": {
            "from": fr,
            "to": to,
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


def get_request_json_of_token_total_supply(token_addr: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_call",
        "id": 60889,
        "params": {
            "from": "hx0000000000000000000000000000000000000000",
            "to": token_addr,
            "dataType": "call",
            "data": {
                "method": "total_supply",
                "params": {}
            }
        }
    }


def get_request_json_of_nonexist_method(token_addr: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "icx_call",
        "id": 60889,
        "params": {
            "from": "hx0000000000000000000000000000000000000000",
            "to": token_addr,
            "dataType": "call",
            "data": {
                "method": "total_supp",
                "params": {}
            }
        }
    }


god_address = f'hx{"0"*40}'
test_address = f'hx1{"0"*39}'
token_owner_address = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
token_score_address = "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf"
