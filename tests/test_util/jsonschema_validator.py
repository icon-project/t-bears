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

from jsonrpcserver import status
from jsonschema import validate
from jsonschema.exceptions import ValidationError

icx_sendTransaction_v2: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_sendTransaction",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_sendtransaction",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "from": {"type": "string", "maxLength": 42, "pattern": "^hx"},
                "to": {"type": "string", "maxLength": 42, "pattern": "^hx"},
                "value": {"type": "string"},
                "fee": {"type": "string"},
                "timestamp": {"type": "string"},
                "nonce": {"type": "string"},
                "tx_hash": {"type": "string"},
                "signature": {"type": "string"},
            },
            "additionalProperties": False,
            "required": ["from", "to", "value", "fee", "timestamp", "tx_hash", "signature"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]

}

icx_getTransactionResult_v2: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getBalance",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getbalance",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "tx_hash": {"type": "string"},
            },
            "additionalProperties": False,
            "required": ["tx_hash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBalance_v2: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getBalance",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getbalance",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "maxLength": 42, "pattern": "^hx"},
            },
            "additionalProperties": False,
            "required": ["address"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBlockByHeight_v2: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getBlockByHeight",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getblockbyheight",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "height": {"type": "string"},
            },
            "additionalProperties": False,
            "required": ["height"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBlockByHash_v2: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getBlockByHash",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getblockbyhash",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "hash": {"type": "string"},
            },
            "additionalProperties": False,
            "required": ["hash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getLastBlock_v2: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getLastBlock",
    "id": "https://github.com/icon-project/icx_JSON_RPC#icx_getlastblock",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id"]
}

icx_getTransactionByAddress_v2: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getTransactionByAddress",
    "id": "googledoc.icx_getTransactionByAddress",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "maxLength": 42, "pattern": "^hx"},
                "index": {"type": "number"},
            },
            "additionalProperties": False,
            "required": ["address", "index"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id"]
}

icx_getTotalSupply_v2: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getTotalSupply",
    "id": "googledoc.icx_getTotalSupplu",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id"]
}

SCHEMA_V2: dict = {
    "icx_sendTransaction": icx_sendTransaction_v2,
    "icx_getTransactionResult": icx_getTransactionResult_v2,
    "icx_getBalance": icx_getBalance_v2,
    "icx_getTotalSupply": icx_getTotalSupply_v2,
    "icx_getLastBlock": icx_getLastBlock_v2,
    "icx_getBlockByHash": icx_getBlockByHash_v2,
    "icx_getBlockByHeight": icx_getBlockByHeight_v2,
    "icx_getTransactionByAddress": icx_getTransactionByAddress_v2
}


def validate_jsonschema_v2(request: object):
    validate_jsonschema(request, SCHEMA_V2)


icx_call_v3: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_call",
    "id": "https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3#icx_call",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string", "enum": ["icx_call"]},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "from": {"type": "string", "maxLength": 42},
                "to": {"type": "string", "maxLength": 42},
                "dataType": {"type": "string", "enum": ["call"]},
                "data": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string"},
                        "params": {"type": "object"}
                    },
                    "additionalProperties": False,
                    "required": ["method"]
                },
            },
            "additionalProperties": False,
            "required": ["from", "to", "dataType", "data"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getBalance_v3: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getBalance",
    "id": "https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3#icx_getbalance",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "maxLength": 42, "pattern": "^hx|^cx"},
            },
            "additionalProperties": False,
            "required": ["address"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getScoreApi_v3: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getScoreApi",
    "id": "https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3#icx_getscoreapi",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "maxLength": 42, "pattern": "^cx"},
            },
            "additionalProperties": False,
            "required": ["address"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getTransactionResult_v3: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getTransactionResult",
    "id": "https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3#icx_gettransactionresult",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "txHash": {"type": "string"}
            },
            "additionalProperties": False,
            "required": ["txHash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_getTransactionByHash_v3: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_getTransactionByHash",
    "id": "https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3#icx_gettransactionbyhash",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "txHash": {"type": "string", "minLength": 66, "maxLength": 66, "pattern": "^0x[0-9a-f]{64}"}
            },
            "additionalProperties": False,
            "required": ["txHash"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]
}

icx_sendTransaction_v3: dict = {
    "$schema": "http://json-schema.org/schema#",
    "title": "icx_sendTransaction",
    "id": "https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3#icx_sendtransaction",
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "enum": ["2.0"]},
        "method": {"type": "string"},
        "id": {"type": "number"},
        "params": {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "from": {"type": "string", "maxLength": 42},
                "to": {"type": "string", "maxLength": 42},
                "value": {"type": "string"},
                "stepLimit": {"type": "string"},
                "timestamp": {"type": "string"},
                "nid": {"type": "string"},
                "nonce": {"type": "string"},
                "signature": {"type": "string"},
                "dataType": {"type": "string", "enum": ["call", "deploy", "message"]},
                "data": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string"},
                                "contentType": {"type": "string"},
                                "content": {"type": "string"},
                                "params": {"type": "object"}
                            },
                            "additionalProperties": False,
                        },
                        {"type": "string"}
                    ],
                },
            },
            "additionalProperties": False,
            "required": ["version", "from", "stepLimit", "timestamp", "nid", "signature"]
        }
    },
    "additionalProperties": False,
    "required": ["jsonrpc", "method", "id", "params"]

}

SCHEMA_V3: dict = {
    "icx_getLastBlock": icx_getLastBlock_v2,
    "icx_getBlockByHeight": icx_getBlockByHeight_v2,
    "icx_getBlockByHash": icx_getBlockByHash_v2,
    "icx_call": icx_call_v3,
    "icx_getBalance": icx_getBalance_v3,
    "icx_getScoreApi": icx_getScoreApi_v3,
    "icx_getTotalSupply": icx_getTotalSupply_v2,
    "icx_getTransactionResult": icx_getTransactionResult_v3,
    "icx_getTransactionByHash": icx_getTransactionByHash_v3,
    "icx_sendTransaction": icx_sendTransaction_v3
}


def validate_jsonschema_v3(request: object):
    validate_jsonschema(request, SCHEMA_V3)


def validate_jsonschema(request: object, schemas: dict = SCHEMA_V3):
    """ Validate JSON-RPC v3 schema.

    refer to
    v2 : https://github.com/icon-project/icx_JSON_RPC
    v3 : https://repo.theloop.co.kr/theloop/LoopChain/wikis/doc/loopchain-json-rpc-v3

    :param request: JSON-RPC request to validate
    :param schemas: The schema to validate with
    :return: N/A
    """
    # get JSON-RPC batch request
    if isinstance(request, list):
        for req in request:
            validate_jsonschema(req, schemas=schemas)
        return

    # get schema for 'method'
    schema: dict = None
    method = request.get('method', None)
    if method and isinstance(method, str):
        schema = schemas.get(method, None)
    if schema is None:
        raise ValueError(f"JSON schema validation error: Method not found")

    # check request
    try:
        validate(instance=request, schema=schema)
    except ValidationError as e:
        raise ValueError(f"JSON schema validation error: {e}")
