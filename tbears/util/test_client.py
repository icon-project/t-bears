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
import json
import time

import requests


class TestClient:
    url = 'http://localhost:9000/api/v3'

    def send_req(self, method: str, params: dict):
        if method == 'icx_sendTransaction':
            self.check_timestamp(params)

        json_content = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 1,
            "params": self.convert_values(params)
        }
        res = requests.post(self.url, json.dumps(json_content))
        return res

    def convert_values(self, params) -> dict:
        return self.convert_dict(params)

    def convert_dict(self, dict_value) -> dict:
        output = {}

        for key, value in dict_value.items():
            if isinstance(value, dict):
                output[key] = self.convert_dict(value)
            elif isinstance(value, list):
                output[key] = self.convert_list(value)
            else:
                output[key] = self.convert_value(value)

        return output

    def convert_list(self, list_value) -> list:
        output = []

        for item in list_value:
            if isinstance(item, dict):
                item = self.convert_dict(item)
            elif isinstance(item, list):
                item = self.convert_list(item)
            else:
                item = self.convert_value(item)

            output.append(item)
        return output

    @staticmethod
    def convert_value(value):
        if isinstance(value, int):
            return hex(value)
        else:
            return str(value)

    def check_timestamp(self, params):
        if 'timestamp' not in params:
            params['timestamp'] = int(time.time() * 10 ** 6)
