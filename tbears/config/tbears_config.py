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

FN_SERVER_CONF = './tbears_server_config.json'
FN_CLI_CONF = './tbears_cli_config.json'


class ConfigKey:
    CHANNEL = 'channel'
    AMQP_KEY = 'amqpKey'
    AMQP_TARGET = 'amqpTarget'


tbears_server_config = {
    "hostAddress": "0.0.0.0",
    "port": 9000,
    "scoreRootPath": "./.score",
    "stateDbRootPath": "./.statedb",
    "log": {
        "logger": "tbears",
        "level": "info",
        "filePath": "./tbears.log",
        "colorLog": True,
        "outputType": "console|file",
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
        "nid": "0x03",
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
            }
        ]
    },
    ConfigKey.CHANNEL: "loopchain_default",
    ConfigKey.AMQP_KEY: "7100",
    ConfigKey.AMQP_TARGET: "127.0.0.1",
}

tbears_cli_config = {
    "uri": "http://127.0.0.1:9000/api/v3",
    "nid": "0x3",
    "keyStore": None,
    "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "to": "cx0000000000000000000000000000000000000000",
    "stepLimit": "0x300000",
    "deploy": {
        "contentType": "tbears",
        "mode": "install",
        "scoreParams": {}
    },
    "txresult": {},
    "transfer": {}
}

log_to_file_config ={
     "log": {
        "logger": "tbears",
        "level": "info",
        "filePath": "./tbears.log",
        "colorLog": True,
        "outputType": "file"
    }
}
