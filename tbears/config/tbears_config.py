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

FN_SERVER_CONF = './tbears_server_config.json'
FN_CLI_CONF = './tbears_cli_config.json'

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
        "outputType": "console|file"
    },
    "service": {
        "fee": False,
        "audit": False
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
    }
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
