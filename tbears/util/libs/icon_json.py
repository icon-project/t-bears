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
import hashlib
import os
import time

from tbears.tbears_exception import ZipException, FillDeployPaylodException, JsonContentsException
from tbears.util import InMemoryZip, IcxSigner


class JsonContents:

    def __init__(self, step_limit=123, nonce=1, version=3, _id=1):
        if not all(isinstance(arg, int) for arg in (step_limit, nonce, version, _id)):
            raise JsonContentsException

        self.step_limit = step_limit
        self.nonce = nonce
        self.version = version
        self.id = _id

    def json_rpc_format(self, method: str, params: dict = None) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.id,
        }
        if params is not None:
            payload['params'] = convert_dict(params)

        return payload

    def json_send_transaction(self, signer: 'IcxSigner', to: str, value: str) -> dict:
        payload = self.params_send_transaction(f'hx{signer.address.hex()}', to, value)
        put_signature_to_payload(payload, signer)
        return self.json_rpc_format('icx_sendTransaction', params=payload)

    def json_send_transaction_deploy(self, path: str, signer: 'IcxSigner',
                                     score_address: str = None, deploy_params: dict = {}) -> dict:
        if not score_address:
            score_address = f'cx{"0"*40}'
        payload = self.params_send_transaction(f'hx{signer.address.hex()}', score_address, hex(0))
        payload['dataType'] = 'deploy'
        payload['data'] = {}
        payload['data']['params'] = deploy_params
        fill_deploy_content(payload, path)
        put_signature_to_payload(payload, signer)
        return self.json_rpc_format('icx_sendTransaction', params=payload)

    def json_send_transaction_score(self, signer: 'IcxSigner', to, value, score_method: str,
                                    score_params: dict = {}):
        payload = self.params_send_transaction(f'hx{signer.address.hex()}', to, value)
        payload['dataType'] = 'call'
        payload['data'] = {}
        payload['data']['method'] = score_method
        payload['data']['params'] = score_params
        put_signature_to_payload(payload, signer)
        return self.json_rpc_format('icx_sendTransaction', params=payload)

    def params_send_transaction(self, fr: str, to: str, value: str) -> dict:
        payload = {
            "from": fr,
            "to": to,
            "value": value,
            "timestamp": hex(int(time.time() * 10 ** 6)),
            "stepLimit": hex(self.step_limit),
            "nonce": hex(self.nonce)
        }
        if self.version >= 3:
            payload['version'] = hex(self.version)

        return payload

    def json_icx_call(self, fr: str, to: str, score_method: str, score_params: dict = {}):
        return self.json_rpc_format('icx_call',
                                    params=JsonContents.params_icx_call(fr, to, score_method, score_params))

    def json_tx_result(self, tx_hash: str) -> dict:
        return self.json_rpc_format('icx_getTransactionResult', params=JsonContents.params_tx_result(tx_hash))

    def json_total_supply(self) -> dict:
        return self.json_rpc_format('icx_totalSupply')

    def json_get_balance(self, address: str) -> dict:
        return self.json_rpc_format('icx_getBalance', params=JsonContents.params_get_balance(address))

    def json_score_api(self, address: str) -> dict:
        return self.json_rpc_format('icx_getScoreApi', params=JsonContents.params_score_api(address))

    @staticmethod
    def params_tx_result(tx_hash: str) -> dict:
        return {'txHash': tx_hash}

    @staticmethod
    def params_get_balance(address: str) -> dict:
        return {"address": address}

    @staticmethod
    def params_score_api(address: str) -> dict:
        return {"address": address}

    @staticmethod
    def params_icx_call(fr: str, to: str, score_method: str, score_params: dict = {}) -> dict:
        return {
            "from": fr,
            "to": to,
            "dataType": "call",
            "data": {
                "method": score_method,
                "params": score_params
            }
        }

    def json_dummy_send_transaction(self, fr: str, to: str, value: str,
                                    data: dict, signature: str, data_type: str = None) -> dict:
        payload = {
            "from": fr,
            "to": to,
            "value": value,
            "stepLimit": hex(self.step_limit),
            "nonce": hex(self.nonce),
            "timestamp": hex(int(time.time() * 10 ** 6)),
            "signature": signature
        }
        if self.version >= 3:
            payload['version'] = hex(self.version)
        if data_type == 'deploy' or data_type == 'call':
            payload['dataType'] = data_type
            payload['data'] = data

        return self.json_rpc_format('icx_sendTransaction', params=payload)


def convert_dict(dict_value) -> dict:
    """ convert dict's values to str type.

    :param dict_value: Dict to convert
    :return:
    """
    output = {}

    for key, value in dict_value.items():
        if isinstance(value, dict):
            output[key] = convert_dict(value)
        elif isinstance(value, list):
            output[key] = convert_list(value)
        else:
            output[key] = convert_value(value)

    return output


def convert_list(list_value) -> list:
    """ convert list's values to str type.

        :param list_value: list to convert
        :return:
        """
    output = []

    for item in list_value:
        if isinstance(item, dict):
            item = convert_dict(item)
        elif isinstance(item, list):
            item = convert_list(item)
        else:
            item = convert_value(item)

        output.append(item)
    return output


def convert_value(value):
    if isinstance(value, int):
        return hex(value)
    else:
        return str(value)


def get_deploy_req_template():
    payload = {
        "from": "",
        "to": f'cx{"0"*40}',
        "stepLimit": "0x12345",
        "timestamp": hex(int(time.time() * 10 ** 6)),
        "nonce": "0x1",
        "dataType": "deploy",
        "data": {
            "contentType": "application/zip",
            "content": "",
            "params": {

            }
        }
    }
    return payload


def put_signature_to_payload(payload: dict, signer: 'IcxSigner'):
    phrase = f'icx_sendTransaction.{get_tx_phrase(payload)}'
    msg_hash = hashlib.sha3_256(phrase.encode()).digest()
    signature = signer.sign(msg_hash)
    payload['signature'] = signature.decode()


def get_tx_phrase(params: dict) -> str:
    keys = [k for k in params]
    keys.sort()
    key_count = len(keys)
    if key_count == 0:
        return ""
    phrase = ""

    if not params[keys[0]]:
        phrase += keys[0]
    elif not isinstance(params[keys[0]], dict):
        phrase += f'{keys[0]}.{params[keys[0]]}'
    else:
        phrase += f'{keys[0]}.{get_tx_phrase(params[keys[0]])}'

    for i in range(1, key_count):
        key = keys[i]

        if not params[key]:
            phrase += f'.{key}'
        elif not isinstance(params[key], dict):
            phrase += f'.{key}.{params[key]}'
        else:
            phrase += f'.{key}.{get_tx_phrase(params[key])}'

    return phrase


def fill_deploy_content(payload: dict = None, project_root_path: str = None):
    """Fill zip data to deploy payload.

    :param payload:
    :param project_root_path:
    :return:
    """
    if not payload:
        raise Exception
    if os.path.isdir(project_root_path) is False:
        raise Exception
    try:
        memory_zip = InMemoryZip()
        memory_zip.zip_in_memory(project_root_path)
    except ZipException:
        raise FillDeployPaylodException
    else:
        payload['data']['contentType'] = 'application/zip'
        payload['data']['content'] = f'0x{memory_zip.data.hex()}'


def fill_optional_deploy_field(payload: dict, step_limit: str = None, score_address: str = None,
                               params: dict = None):
    """Fill step_lmit, score_address, params of deploy payload.

    :param payload: deploy payload.
    :param step_limit: step limit.
    :param score_address: It is needed when you want to update your SCORE.
    :param params: Parameters passed to the on_init or on_update methods.
    :return:
    """
    if step_limit:
        payload["stepLimit"] = step_limit
    if score_address:
        payload["to"] = score_address
    if params:
        payload["data"]["params"] = params


def get_icx_sendTransaction_payload(signer: 'IcxSigner', to, value, nonce=1, step_limit=12345, version=3, _id=1):
    """

    :param signer: IcxSigner instanace. it is needed to make signature.
    :param to: Address to send icx.
    :param value: Amount of coin to transfer.
    :param nonce: optional value.
    :param step_limit: step limit.
    :param version: icon api version.
    :param _id: optional value.
    :return: Requests.Response object.
    """
    json_contents = JsonContents(step_limit, nonce, version, _id)
    return json_contents.json_send_transaction(signer, to, value)


def get_icx_sendTransaction_score_payload(signer: 'IcxSigner', to, value, score_method,
                                          score_params={}, nonce=1, step_limit=12345, version=3, _id=1):
    """

        :param signer: IcxSigner instanace. it needed to make signature.
        :param to: Address to send icx.
        :param value: Amount of coin to transfer.
        :param nonce: optional value.
        :param step_limit: step limit.
        :param version: icon api version.
        :param _id: optional value.
        :param score_params: Parameters to pass to SCORE's method.
        :return: Requests.Response object.
        """
    json_contents = JsonContents(step_limit, nonce, version, _id)
    return json_contents.json_send_transaction_score(signer, to, value, score_method, score_params)


def get_icx_sendTransaction_deploy_payload(signer: 'IcxSigner', path,
                                           nonce=1, step_limit=12345, version=3, _id=1, deploy_params={}, to=None):
    """

        :param signer: IcxSigner instanace. it is needed to make signature.
        :param to: Address to send icx.
        :param nonce: optional value.
        :param step_limit: step limit.
        :param version: icon api version.
        :param _id: optional value.
        :return: Requests.Response object.
        """
    json_contents = JsonContents(step_limit, nonce, version, _id)
    return json_contents.json_send_transaction_deploy(path, signer, to, deploy_params)


def get_dummy_icx_sendTransaction_payload(fr, to, value, nonce=1, step_limit=12345, version=3, _id=1,
                                          signature='dummysign', data_type=None, data=None):
    """

    :param fr:
    :param to: Address to send icx.
    :param nonce: optional value.
    :param step_limit: step limit.
    :param version: icon api version.
    :param _id: optional value.
    :param signature: signature
    :param data_type: data_type. it can be 'call', 'deploy' or None
    :param data: It is needed when 'data_type' is deploy or call.
    :return:
    """
    json_contents = JsonContents(step_limit, nonce, version, _id)
    return json_contents.json_dummy_send_transaction(fr, to, value, data, signature, data_type)


def get_icx_getBalance_payload(address):
    """Inquire balance of given address.

    :param address: Address which you want to inquire balances
    :return:
    """
    return JsonContents().json_get_balance(address)


def get_icx_getScoreApi_payload(address):
    """Inquire scoreapi of given score address.
    :param address: SCORE Address which you want to inquire SCOREAPI.
    :return:
    """
    return JsonContents().json_score_api(address)


def get_icx_totalSupply_payload():
    """Inquire total supply of icx.

    :return:
    """
    return JsonContents().json_total_supply()


def get_icx_getTransactionResult_payload(tx_hash):
    """Inquire Transaction Result with given transaction hash(tx_hash).

    :param tx_hash:
    :return:
    """
    return JsonContents().json_tx_result(tx_hash)


def get_icx_call_payload(fr, to, score_method, score_params={}):
    """Call SCORE's method.

    :param fr:
    :param to: SCORE's address.
    :param score_method: This is the method of SCORE that you want to call.
    :param score_params: Parameters to be passed to the SCORE's method.
    :return:
    """
    return JsonContents().json_icx_call(fr, to, score_method, score_params)
