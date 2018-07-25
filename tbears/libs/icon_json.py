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
import time
from typing import TYPE_CHECKING

from tbears.libs.icon_serializer import generate_origin_for_icx_send_tx_hash
from tbears.tbears_exception import JsonContentsException

if TYPE_CHECKING:
    from tbears.util.icx_signer import IcxSigner


class JsonContents:
    """Utility class for make payload of requests."""

    def __init__(self, step_limit=123000, nonce=1, version=3, _id=1):
        if not all(isinstance(arg, int) for arg in (step_limit, nonce, version, _id)):
            raise JsonContentsException(f"stepLimit, nonce, version, id must be int type")

        self.step_limit = step_limit
        self.nonce = nonce
        self.version = version
        self.id = _id

    def json_rpc_format(self, method: str, params: dict = None) -> dict:
        """Returns jsonrpc-2.0 formatted dict.

        :param method: Method to call.
        :param params: Parameters of the method to call.

        :return: jsonrpc-2.0 formatted dict.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.id,
        }
        if params is not None:
            payload['params'] = convert_dict(params)

        return payload

    def json_send_transaction(self, signer: 'IcxSigner', to: str, value: str, nid: str) -> dict:
        """Fill contents of the deploy payload with the given parameters and returns the payload.

        :param signer: It needed to make signature.
        :param to: Address to send icx.
        :param value: Amount of icx to transfer.
        :param nid: Network ID

        :return: Full payload of deploy request.
        """
        payload = self.params_send_transaction(f'hx{signer.address.hex()}', to, value, nid)
        put_signature_to_payload(payload, signer)
        return self.json_rpc_format('icx_sendTransaction', params=payload)

    def json_send_transaction_score(self, signer: 'IcxSigner', to, value, nid, score_method: str,
                                    score_params: dict = {}) -> dict:
        """Fill contents of the icx_sendTransaction(to SCORE) payload with the given parameters and returns the payload.

        :param signer: IcxSigner instanace. it needed to make signature.
        :param to: Address to send icx.
        :param value: Amount of icx to transfer.
        :param nid: Network ID
        :param score_method: The score method to call.
        :param score_params: Parameters to pass to SCORE's method.

        :return: Full payload of icx_sendTransaction(To SCORE).
        """
        payload = self.params_send_transaction(f'hx{signer.address.hex()}', to, value, nid)
        payload['dataType'] = 'call'
        payload['data'] = {}
        payload['data']['method'] = score_method
        payload['data']['params'] = score_params
        put_signature_to_payload(payload, signer)
        return self.json_rpc_format('icx_sendTransaction', params=payload)

    def json_send_transaction_deploy(self, contents: str, signer: 'IcxSigner', nid: str,
                                     score_address: str = None, deploy_params: dict = {}) -> dict:
        """Fill contents of the deploy payload with the given parameters and returns the payload.

        :param contents: Your SCORE's zipped data(bytes).
        :param signer: It needed to make signature.
        :param score_address: Needed when update SCORE.
        :param nid: Network ID
        :param deploy_params: Passed on to the on_init or on_update method calls.

        :return: Full payload of deploy request.
        """
        if not score_address:
            score_address = f'cx{"0"*40}'

        data = {
            'contentType': 'application/zip',
            'content': contents,
            'params': deploy_params
        }
        payload = self.params_send_transaction(f'hx{signer.address.hex()}', score_address, hex(0), nid,
                                               data_type='deploy', data=data)
        put_signature_to_payload(payload, signer)
        return self.json_rpc_format('icx_sendTransaction', params=payload)

    def params_send_transaction(self, fr: str, to: str, value: str, nid: str,
                                data_type=None, data: dict = None) -> dict:
        """Fill contents of the params field of icx_sendTransaction payload with given parameters and returns the params.

        :param fr: Transaction sender.
        :param to: Address to send icx.
        :param value: Amount of icx.
        :param nid: Network ID.
        :param data_type: data_type field. it can be 'call', 'deploy' or None
        :param data: It is needed when 'data_type' is deploy or call.

        :return: Params of icx_sendTransaction payload.
        """
        payload = {
            "from": fr,
            "to": to,
            "value": value,
            "nid": nid,
            "timestamp": hex(int(time.time() * 10 ** 6)),
            "stepLimit": hex(self.step_limit),
            "nonce": hex(self.nonce)
        }
        if self.version >= 3:
            payload['version'] = hex(self.version)
        if data_type == 'deploy' or data_type == 'call':
            payload['dataType'] = data_type
            payload['data'] = data

        return payload

    def json_icx_call(self, fr: str, to: str, score_method: str, score_params: dict = {}) -> dict:
        """Fill contents of the icx_call payload with the given parameters and returns the payload.

        :param fr: Address to call the method of score.
        :param to: SCORE's address.
        :param score_method: The score method to call.
        :param score_params: Parameters to be passed to the SCORE's method.

        :return: Full payload of icx_call
        """
        return self.json_rpc_format('icx_call',
                                    params=JsonContents.params_icx_call(fr, to, score_method, score_params))

    def json_tx_result(self, tx_hash: str) -> dict:
        """Fill contents of the icx_getTransactionResult payload with given tx_hash and returns the payload.

        :param tx_hash: The hash value of the transaction you want to query.

        :return: Full payload of icx_getTransactionResult request.
        """
        return self.json_rpc_format('icx_getTransactionResult', params=JsonContents.params_tx_result(tx_hash))

    def json_get_tx(self, tx_hash: str) -> dict:
        """Fill contents of the icx_getTransactionByHash payload with given tx_hash and returns the payload.

        :param tx_hash: The hash value of the transaction you want to query.

        :return: Full payload of icx_getTransactionResult request.
        """
        return self.json_rpc_format('icx_getTransactionByHash', params=JsonContents.params_get_tx(tx_hash))

    def json_total_supply(self) -> dict:
        """Returns payload of icx_totalSupply request.

        :return: Full payload of icx_totalSupply request.
        """
        return self.json_rpc_format('icx_getTotalSupply')

    def json_get_balance(self, address: str) -> dict:
        """Fill contents of the icx_getBalance payload with given address and returns the payload.

        :param address: Address to query.

        :return: Full payload of icx_getBalance.
        """
        return self.json_rpc_format('icx_getBalance', params=JsonContents.params_get_balance(address))

    def json_score_api(self, address: str) -> dict:
        """Fill contents of icx_getScoreApi payload with given score address and returns the payload.

        :param address: The address of score to query scoreapi.

        :return: Full payload of icx_getScoreApi.
        """
        return self.json_rpc_format('icx_getScoreApi', params=JsonContents.params_score_api(address))

    @staticmethod
    def params_tx_result(tx_hash: str) -> dict:
        return {'txHash': tx_hash}

    @staticmethod
    def params_get_tx(tx_hash: str) -> dict:
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


def convert_dict(dict_value) -> dict:
    """Convert values in dict to str type.

    :param dict_value: Dict to convert

    :return: Converted dict.
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
    """Convert list's values to str type.

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


def convert_value(value) -> str:
    """Convert value to str type.

    :param value: value to convert.

    :return: Converted value.
    """

    if isinstance(value, int):
        return hex(value)
    else:
        return str(value)


def put_signature_to_payload(payload: dict, signer: 'IcxSigner'):
    """Put signature to payload of icx_sendTransaction request.

    :param payload: Payload of icx_sendTransaction request.
    :param signer: IcxSigner instance.
    """
    phrase = generate_origin_for_icx_send_tx_hash(payload)
    msg_hash = hashlib.sha3_256(phrase.encode()).digest()
    signature = signer.sign(msg_hash)
    payload['signature'] = signature.decode()


def get_icx_sendTransaction_deploy_payload(signer: 'IcxSigner', contents, nid,
                                           nonce=1, step_limit=12345, version=3, _id=1, deploy_params={}, to=None):
    """Returns payload of deploy request.

    :param signer: IcxSigner instanace. it is needed to make signature.
    :param contents: SCORE's zipped data(bytes).
    :param nid: Network ID
    :param nonce: optional value.
    :param step_limit: step limit.
    :param version: icon api version.
    :param _id: optional value.
    :param deploy_params: Passed on to the on_init or on_update method calls.
    :param to: Address to send icx.

    :return: Requests.Response object.
    """
    json_contents = JsonContents(step_limit, nonce, version, _id)
    return json_contents.json_send_transaction_deploy(contents, signer, nid, to, deploy_params)


def get_icx_sendTransaction_payload(signer: 'IcxSigner', to, value, nid, nonce=1, step_limit=12345, version=3, _id=1):
    """Payload of icx_sendTransaction. only for send icx.

    :param signer: IcxSigner instanace. it is needed to make signature.
    :param to: Address to send icx.
    :param value: Amount of coin to transfer.
    :param nid: Network ID
    :param nonce: optional value.
    :param step_limit: step limit.
    :param version: icon api version.
    :param _id: optional value.

    :return: Requests.Response object.
    """
    json_contents = JsonContents(step_limit, nonce, version, _id)
    return json_contents.json_send_transaction(signer, to, value, nid)


def get_icx_sendTransaction_score_payload(signer: 'IcxSigner', to, value, nid, score_method,
                                          score_params={}, nonce=1, step_limit=12345, version=3, _id=1):
    """The payload of call the payable function.

    :param signer: IcxSigner instanace. it needed to make signature.
    :param to: Address to send icx.
    :param value: Amount of coin to transfer.
    :param nid: Network ID
    :param nonce: optional value.
    :param step_limit: step limit.
    :param version: icon api version.
    :param _id: optional value.
    :param score_method: The score method to call.
    :param score_params: Parameters to pass to SCORE's method.
    :return: Requests.Response object.
    """
    json_contents = JsonContents(step_limit, nonce, version, _id)
    return json_contents.json_send_transaction_score(signer, to, value, nid, score_method, score_params)


def get_icx_getBalance_payload(address):
    """Inquire balance of given address.

    :param address: Address which you want to inquire balances

    :return: payload for icx_getBalance.
    """
    return JsonContents().json_get_balance(address)


def get_icx_getScoreApi_payload(address):
    """Inquire scoreapi of given score address.

    :param address: SCORE Address which you want to inquire SCOREAPI.

    :return: payload for icx_getScoreApi
    """
    return JsonContents().json_score_api(address)


def get_icx_getTotalSupply_payload() -> dict:
    """Inquire total supply of icx.

    :return: payload for icx_totalSupply
    """
    return JsonContents().json_total_supply()


def get_icx_getTransactionResult_payload(tx_hash) -> dict:
    """Inquire Transaction Result with given transaction hash(tx_hash).

    :param tx_hash: The hash value of the transaction you want to query.

    :return: payload for icx_getTransactionResult.
    """
    return JsonContents().json_tx_result(tx_hash)


def get_icx_call_payload(fr, to, score_method, score_params={}) -> dict:
    """Call SCORE's method.

    :param fr: Address to call the method of score.
    :param to: SCORE's address.
    :param score_method: This is the method of SCORE that you want to call.
    :param score_params: Parameters to be passed to the SCORE's method.

    :return: payload for icx_call
    """
    return JsonContents().json_icx_call(fr, to, score_method, score_params)


def get_dummy_icx_sendTransaction_payload(fr, to, value, nid, nonce=1, step_limit=12345, version=3, _id=1,
                                          signature='dummysign', data_type=None, data=None) -> dict:
    """This function might be used for test.

    :param fr: Address of transaction sender.
    :param to: Address to send icx.
    :param value: Amount of coin to transfer.
    :param nid: Network ID
    :param nonce: optional value.
    :param step_limit: step limit.
    :param version: icon api version.
    :param _id: optional value.
    :param signature: signature
    :param data_type: data_type. it can be 'call', 'deploy' or None
    :param data: It is needed when 'data_type' is deploy or call.

    :return: Full payload of dummy icx_sendTransaction.
    """
    json_contents = JsonContents(step_limit, nonce, version, _id)
    params = json_contents.params_send_transaction(fr, to, value, nid, data_type, data)
    params['signature'] = signature
    payload = json_contents.json_rpc_format('icx_sendTransaction', params)
    return payload


def get_icx_getTransactionByHash(tx_hash) -> dict:
    """Inquire Transaction Result with given transaction hash(tx_hash).
    :param tx_hash: The hash value of the transaction you want to query.
    :return: payload for icx_getTransactionResult.
    """
    return JsonContents().json_get_tx(tx_hash)
