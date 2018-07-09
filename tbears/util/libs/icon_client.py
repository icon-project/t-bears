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

from tbears.tbears_exception import IconClientException


class IconClient:

    def __init__(self, url: str):
        self._url = url

    def send(self, payload: dict) -> requests.Response:
        try:
            json_content = json.dumps(payload)
            resp = requests.post(self._url, json_content)
        except requests.exceptions.Timeout:
             raise RuntimeError("time out")
        except:
            raise IconClientException
        else:
            return resp
