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
import os
import json

tbears_config = {
    "hostAddress": "0.0.0.0",
    "port": 9000,
    "scoreRoot": "./.score",
    "dbRoot": "./.db",
    "enableFee": False,
    "enableAudit": False,
    "log": {
        "colorLog": True,
        "level": "debug",
        "filePath": "./tbears.log",
        "outputType": "console|file|daily"
    },
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

deploy_config = {
    "uri": "http://127.0.0.1:9000/api/v3",
    "scoreType": "tbears",
    "mode": "install",
    "keyStore": None,
    "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "to": "cx0000000000000000000000000000000000000000",
    "nid": "0x1234",
    "stepLimit": "0x1234",
    "scoreParams": {
    }
}


class TBearsConfig(dict):
    def __init__(self, default_conf_path: str = './tbears.json', default_config: dict = tbears_config):
        self.default_conf_path = default_conf_path
        self.update(default_config)

    def load(self, user_input: dict = {}):
        for path in [user_input.get('config', ""), self.default_conf_path]:
            if path and self._load(path):
                break

        if user_input:
            self.update({k: v for k, v in user_input.items() if v})

    def _load(self, conf_path: str):
        if not os.path.exists(conf_path):
            return False
        with open(conf_path) as f:
            conf: dict = json.load(f)
            self.update(conf)
            return True
