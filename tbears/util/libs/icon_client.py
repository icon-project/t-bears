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

import requests

from tbears.util import IcxSigner


class IconClient:

    def __init__(self, url: str, version: int, private_key: bytes):
        self._url = url
        self._version = version
        self._private_key = private_key
        self._signer = IcxSigner(self._private_key)

    def send(self, payload: dict) -> requests.Response:
        json_content = json.dumps(payload)
        resp = requests.post(self._url, json_content)
        return resp
