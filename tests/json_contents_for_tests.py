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

from tbears.util import IcxSigner
from tbears.util.icx_signer import key_from_key_store


def get_params_for_get_token_balance(addr_from: str) -> tuple:
    return 'balance_of', {"addr_from": addr_from}


def get_data_for_transfer_token(addr_to: str, value: str) -> dict:
    return {
        "method": 'transfer',
        "params": {
            "addr_to": addr_to,
            "value": value
        }
    }


def get_params_for_transfer_token(addr_to: str, value: str) -> tuple:
    return 'transfer', { "addr_to": addr_to, "value": value}


def get_request_json_of_nonexist_method() -> tuple:
    return 'nonexistent_method', {}


god_address = f'hx{"0"*40}'
test_address = f'hx1{"0"*39}'
token_owner_address = "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
token_score_address = "cxb8f2c9ba48856df2e889d1ee30ff6d2e002651cf"
TBEARS_LOCAL_URL = "http://localhost:9000/api/v3"
DIRECTORY_PATH = os.path.abspath((os.path.dirname(__file__)))
deploy_token_owner_private_key = key_from_key_store(os.path.join(DIRECTORY_PATH, 'keystore'), 'qwer1234%')
token_owner_signer = IcxSigner(deploy_token_owner_private_key)
deploy_token_owner_address = f'hx{token_owner_signer.address.hex()}'
TBEARS_JSON_PATH = os.path.join(DIRECTORY_PATH, 'test_tbears.json')
