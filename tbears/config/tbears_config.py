# -*- coding: utf-8 -*-
# Copyright 2018 ICON Foundation
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

from copy import deepcopy

FN_SERVER_CONF = './tbears_server_config.json'
FN_CLI_CONF = './tbears_cli_config.json'

TBEARS_CLI_TAG = 'tbears_cli'


class ConfigKey:
    CHANNEL = 'channel'
    AMQP_KEY = 'amqpKey'
    AMQP_TARGET = 'amqpTarget'
    BLOCK_CONFIRM_INTERVAL = 'blockConfirmInterval'
    BLOCK_CONFIRM_EMPTY = 'blockConfirmEmpty'


tbears_server_config = {
    "hostAddress": "127.0.0.1",
    "port": 9000,
    "scoreRootPath": "./.score",
    "stateDbRootPath": "./.statedb",
    "log": {
        "logger": "tbears",
        "level": "info",
        "filePath": "./tbears.log",
        "colorLog": True,
        "outputType": "file",
        "rotate": {
            "type": "bytes",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10
        }
    },
    "service": {
        "fee": False,
        "audit": False,
        "deployerWhiteList": False
    },
    "genesis": {
        "nid": "0x3",
        "accounts": [
            {
                "name": "genesis",
                "address": "hx0000000000000000000000000000000000000000",
                "balance": "0x2961fff8ca4a62327800000"
            },
            {
                "name": "fee_treasury",
                "address": "hx1000000000000000000000000000000000000000",
                "balance": "0x0"
            },
            {
                "name": "test1",
                "address": "hxe7af5fcfd8dfc67530a01a0e403882687528dfcb",
                "balance": "0x2961fff8ca4a62327800000"
            }
        ]
    },
    ConfigKey.CHANNEL: "loopchain_default",
    ConfigKey.AMQP_KEY: "7100",
    ConfigKey.AMQP_TARGET: "127.0.0.1",
    ConfigKey.BLOCK_CONFIRM_INTERVAL: 10,
    ConfigKey.BLOCK_CONFIRM_EMPTY: True
}


def make_server_config(config: dict) -> dict:
    server_config = deepcopy(config)
    del server_config[ConfigKey.CHANNEL]
    del server_config[ConfigKey.AMQP_KEY]
    del server_config[ConfigKey.AMQP_TARGET]

    return server_config


tbears_cli_config = {
    "uri": "http://127.0.0.1:9000/api/v3",
    "nid": "0x3",
    "keyStore": None,
    "from": "hxe7af5fcfd8dfc67530a01a0e403882687528dfcb",
    "to": "cx0000000000000000000000000000000000000000",
    "deploy": {
        "stepLimit": "0x10000000",
        "mode": "install",
        "scoreParams": {}
    },
    "txresult": {},
    "transfer": {
        "stepLimit": "0xf4240",
    }
}


FN_KEYSTORE_TEST1 = './keystore_test1'
TEST1_PRIVATE_KEY = '592eb276d534e2c41a2d9356c0ab262dc233d87e4dd71ce705ec130a8d27ff0c'

keystore_test1 = {
    "address": "hxe7af5fcfd8dfc67530a01a0e403882687528dfcb",
    "crypto": {
        "cipher": "aes-128-ctr",
        "cipherparams": {
            "iv": "dc0762c56ca56cd06038df5051c9e23e"
        },
        "ciphertext": "7cc40efac0b14eaf56f951c9c9620f9f34bac548175e85052aa9f753423dc984",
        "kdf": "scrypt",
        "kdfparams": {
            "dklen": 32,
            "n": 16384,
            "r": 1,
            "p": 8,
            "salt": "380c00457be5fd1c244f5745c322b21f"
        },
        "mac": "157dda6fb7092df62ff93411bed54e5a64dbf06c1aae3b375d356061a9c3dfd1"
    },
    "id": "e2ca66c6-b8de-4413-82cb-52c2a2200b8d",
    "version": 3,
    "coinType": "icx"
}
