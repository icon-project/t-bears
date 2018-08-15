# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import sys
import time
import hashlib
import uuid
import argparse
from json import JSONDecodeError
from ipaddress import ip_address
from typing import Optional, Union
from copy import deepcopy

from iconservice.icon_constant import DATA_BYTE_ORDER, ConfigKey
from jsonrpcserver import status
from jsonrpcserver.aio import methods
from jsonrpcserver.exceptions import JsonRpcServerError, InvalidParams
from sanic import Sanic, response as sanic_response

from iconservice.utils import check_error_response
from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger
from iconservice.icon_inner_service import IconScoreInnerTask
from tbears.config.tbears_config import FN_SERVER_CONF, tbears_server_config
from tbears.block_manager.tbears_db import TbearsDB
from tbears.command.command_server import CommandServer
from tbears.util.argparse_type import IconPath

TBEARS_LOG_TAG = 'tbears'

__block_height = -1
__prev_block_hash = None
__icon_score_service = None
__icon_score_stub = None
__icon_inner_task = None
__tx_result_mapper = None

sys.path.append('..')
sys.path.append('.')

TBEARS_DB = None
DB_PREFIX_TX = b'tx|'
DB_PREFIX_TXRESULT = b'txResult|'
DB_PREFIX_BLOCK = b'block|'
DB_PREFIX_BLOCK_INDEX = b'blockIndex|'
DB_PREFIX_BLOCK_HEIGHT = b'blockHeight|'
DB_PREFIX_PREV_BLOCK = b'prevBlockHash|'


def create_hash(data: bytes) -> str:
    return f'{hashlib.sha3_256(data).hexdigest()}'


def get_icon_inner_task() -> Optional['IconScoreInnerTask']:
    global __icon_inner_task
    return __icon_inner_task


def get_block_height():
    return __block_height


def set_block_height():
    global __block_height
    __block_height += 1
    TBEARS_DB.put(DB_PREFIX_BLOCK_HEIGHT, str(__block_height).encode())


def get_prev_block_hash():
    global __prev_block_hash
    return __prev_block_hash


def set_prev_block_hash(block_hash: str):
    global __prev_block_hash
    __prev_block_hash = block_hash
    TBEARS_DB.put(DB_PREFIX_PREV_BLOCK, bytes.fromhex(__prev_block_hash))


def rollback_block():
    global __block_height

    # delete block
    block_hash = TBEARS_DB.get(DB_PREFIX_BLOCK_INDEX + __block_height.to_bytes(32, DATA_BYTE_ORDER))
    TBEARS_DB.delete(DB_PREFIX_BLOCK + bytes.fromhex(block_hash))

    # delete block index
    TBEARS_DB.delete(DB_PREFIX_BLOCK_INDEX + __block_height.to_bytes(32, DATA_BYTE_ORDER))

    # decrease block_height
    __block_height -= 1
    TBEARS_DB.put(DB_PREFIX_BLOCK_HEIGHT, str(__block_height).encode())


def get_tx_result_mapper():
    global __tx_result_mapper
    return __tx_result_mapper


def response_to_json_invoke(response):
    # if response is tx_result list
    if check_error_response(response):
        response = response['error']
        raise GenericJsonRpcServerError(
            code=-int(response['code']),
            message=response['message'],
            http_status=status.HTTP_BAD_REQUEST
        )
    elif isinstance(response, dict):
        tx_result = list(response.values())
        tx_result = tx_result[0]
        tx_hash = tx_result['txHash']

        get_tx_result_mapper().put(tx_hash, tx_result)
        return tx_hash
    else:
        raise GenericJsonRpcServerError(
            code=-32603,
            message="can't response_to_json_invoke_convert",
            http_status=status.HTTP_BAD_REQUEST
        )


def response_to_json_query(response):
    if check_error_response(response):
        response: dict = response['error']
        raise GenericJsonRpcServerError(
            code=-int(response['code']),
            message=response['message'],
            http_status=status.HTTP_BAD_REQUEST
        )
    return response


class GenericJsonRpcServerError(JsonRpcServerError):
    """Raised when the request is not a valid JSON-RPC object.
    User can change code and message properly

    :param data: Extra information about the error that occurred (optional).
    """

    def __init__(self, code: int, message: str, http_status: int, data=None):
        """

        :param code: json-rpc error code
        :param message: json-rpc error message
        :param http_status: http status code
        :param data: json-rpc error data (optional)
        """
        super().__init__(data)

        self.code = code
        self.message = message
        self.http_status = http_status


class TxResultMapper(object):
    def __init__(self, limit_capacity=1000):
        self.__limit_capacity = limit_capacity
        self.__mapper = dict()
        self.__key_list = []

    def put(self, key, value) -> None:
        self.__check_limit()
        self.__key_list.append(key)
        self.__mapper[key] = value

    def get(self, key):
        return self.__mapper.get(key, None)

    def __getitem__(self, item):
        return self.__mapper[item]

    def __check_limit(self):
        if self.len() > self.__limit_capacity:
            key = self.__key_list[0]
            self.__key_list.pop(0)
            del self.__mapper[key]

    def len(self) -> int:
        return len(self.__mapper)


class MockDispatcher:
    flask_server = None

    @staticmethod
    async def dispatch(request):
        try:
            req = json.loads(request.body.decode())
            req["params"] = req.get("params", {})
        except JSONDecodeError:
            raise GenericJsonRpcServerError(
                code=-32700,
                message="Parse error",
                http_status=status.HTTP_BAD_REQUEST
            )
        else:
            res = await methods.dispatch(req)
            return sanic_response.json(res, status=res.http_status)

    @staticmethod
    @methods.add
    async def icx_sendTransaction(**request_params):
        """ icx_sendTransaction jsonrpc handler.
        We assume that only one tx in a block.

        :param request_params: jsonrpc params field.
        """
        Logger.debug(f'json_rpc_server icx_sendTransaction!', TBEARS_LOG_TAG)

        # check duplication
        tx_hash = create_hash(json.dumps(request_params).encode())
        result = TBEARS_DB.get(DB_PREFIX_TXRESULT + bytes.fromhex(tx_hash))
        if result:
            result = {"error": {"code": 32000, "message": "Duplicated transaction"}}
            return response_to_json_invoke(result)

        # Insert txHash into request params
        method = 'icx_sendTransaction'
        request_params['txHash'] = tx_hash
        tx = {
            'method': method,
            'params': request_params
        }

        # pre validate
        response = await get_icon_inner_task().validate_transaction(tx)
        response_to_json_query(response)

        # prepare request data to invoke
        request = {'transactions': [tx]}
        block_height: int = get_block_height() + 1
        block_timestamp_us = int(time.time() * 10 ** 6)
        block_hash = create_hash(block_timestamp_us.to_bytes(8, DATA_BYTE_ORDER))
        prev_block_hash = get_prev_block_hash()

        request['block'] = {
            'blockHeight': hex(block_height),
            'blockHash': block_hash,
            'timestamp': hex(block_timestamp_us),
            'prevBlockHash': prev_block_hash
        }

        precommit_request = {'blockHeight': hex(block_height),
                             'blockHash': block_hash}
        # invoke
        response = await get_icon_inner_task().invoke(request)
        tx_results = response['txResults']
        if not isinstance(tx_results, dict):
            rollback_block()
            await get_icon_inner_task().remove_precommit_state(precommit_request)
        elif check_error_response(tx_results):
            rollback_block()
            await get_icon_inner_task().remove_precommit_state(precommit_request)
        else:
            set_prev_block_hash(block_hash)
            set_block_height()
            await get_icon_inner_task().write_precommit_state(precommit_request)

        tx_result = tx_results[tx_hash]
        # tx_result['txHash'] must start with '0x'
        # tx_hash must not start with '0x'
        if tx_hash[:2] != '0x':
            tx_result['txHash'] = f'0x{tx_hash}'
        else:
            tx_result['txHash'] = tx_hash
            tx_hash = tx_hash[2:]

        # save transaction result
        save_txresult(tx_hash, tx_result)

        # save transaction
        save_transaction(tx_hash=tx_hash, params=request_params, block_hash=block_hash, block_height=block_height)

        # save block
        save_block(block_hash, block_height, tx_hash, prev_block_hash)

        return response_to_json_invoke(tx_results)

    @staticmethod
    @methods.add
    async def icx_call(**request_params):
        Logger.debug(f'json_rpc_server icx_call!', TBEARS_LOG_TAG)

        method = 'icx_call'
        request = {'method': method, 'params': request_params}
        response = await get_icon_inner_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getBalance(**request_params):
        Logger.debug(f'json_rpc_server icx_getBalance!', TBEARS_LOG_TAG)

        method = 'icx_getBalance'
        request = {'method': method, 'params': request_params}
        response = await get_icon_inner_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(**request_params):
        Logger.debug(f'json_rpc_server icx_getTotalSupply!', TBEARS_LOG_TAG)

        method = 'icx_getTotalSupply'
        request = {'method': method, 'params': request_params}
        response = await get_icon_inner_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getTransactionResult(**request_params):
        Logger.debug(f'json_rpc_server getTransactionResult!', TBEARS_LOG_TAG)

        try:
            tx_hash = request_params['txHash']
            tx_hash_result = TBEARS_DB.get(DB_PREFIX_TXRESULT + bytes.fromhex(tx_hash[2:]))
            tx_hash_result_str = tx_hash_result.decode()
            tx_result_json = json.loads(tx_hash_result_str)
        except Exception:
            raise GenericJsonRpcServerError(
                code=InvalidParams.code,
                message='TransactionResult not found',
                http_status=status.HTTP_BAD_REQUEST)
        else:
            return tx_result_json

    @staticmethod
    @methods.add
    async def icx_getTransactionByHash(**request_params):
        Logger.debug(f'json_rpc_server getTransactionByHash!', TBEARS_LOG_TAG)

        try:
            tx_payload_json = get_transaction(request_params['txHash'])
        except Exception:
            raise GenericJsonRpcServerError(
                code=InvalidParams.code,
                message='Transaction not found',
                http_status=status.HTTP_BAD_REQUEST)
        else:
            return tx_payload_json

    @staticmethod
    @methods.add
    async def icx_getScoreApi(**request_params):
        Logger.debug(f'json_rpc_server icx_getScoreApi!', TBEARS_LOG_TAG)

        method = 'icx_getScoreApi'
        request = {'method': method, 'params': request_params}
        response = await get_icon_inner_task().query(request)
        return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getLastBlock(**_request_params):
        Logger.debug(f'json_rpc_server icx_getLastBlock!', TBEARS_LOG_TAG)

        return get_block_by_height(get_block_height())

    @staticmethod
    @methods.add
    async def icx_getBlockByHeight(**request_params):
        Logger.debug(f'json_rpc_server icx_getBlockByHeight!', TBEARS_LOG_TAG)

        return get_block_by_height(int(request_params['height'], 16))

    @staticmethod
    @methods.add
    async def icx_getBlockByHash(**request_params):
        Logger.debug(f'json_rpc_server icx_getBlockByHash!', TBEARS_LOG_TAG)

        hash = request_params['hash']

        return get_block_by_hash(bytes.fromhex(hash[2:]))

    @staticmethod
    @methods.add
    async def server_exit(**request_params):
        Logger.debug(f'json_rpc_server server_exit!', TBEARS_LOG_TAG)

        if MockDispatcher.flask_server is not None:
            global TBEARS_DB
            TBEARS_DB.close()
            MockDispatcher.flask_server.app.stop()

        return '0x0'


class FlaskServer:
    def __init__(self):
        self.__app = Sanic(__name__)
        self.__app.config['ENV'] = 'development'  # Block flask warning message
        MockDispatcher.flask_server = self

    @property
    def app(self):
        return self.__app

    def set_resource(self):
        self.__app.add_route(MockDispatcher.dispatch, '/api/v3/', methods=['POST'], strict_slashes=False)


class SimpleRestServer:
    def __init__(self, port, ip_address=None):
        self.__port = port
        self.__ip_address = ip_address

        self.__server = FlaskServer()
        self.__server.set_resource()

    def get_app(self):
        return self.__server.app

    def run(self):
        port = self.__port
        Logger.info(f"SimpleRestServer run... {port}", TBEARS_LOG_TAG)

        self.__server.app.run(port=self.__port,
                              host=self.__ip_address,
                              debug=False)


def create_parser():
    parser = argparse.ArgumentParser(description='jsonrpc_server for tbears')
    parser.add_argument('-a', '--address', help='Address to host on (default: 0.0.0.0)', type=ip_address)
    parser.add_argument('-p', '--port', help='Listen port (default: 9000)', type=int)
    parser.add_argument('-c', '--config', type=IconPath(),
                        help=f'tbears configuration file path (default: {FN_SERVER_CONF})')

    return parser


def serve():
    async def __serve():
        init_tbears(conf)
        await init_icon_inner_task(conf)

    # create parser
    parser = create_parser()

    # parse argument
    args = parser.parse_args(sys.argv[1:])

    if args.config:
        path = args.config
    else:
        path = FN_SERVER_CONF

    conf = IconConfig(path, tbears_server_config)
    conf.load()
    conf.update_conf(vars(args))
    # init logger
    Logger.load_config(conf)
    Logger.info(f'config_file: {path}', TBEARS_LOG_TAG)

    # write conf for tbears_cli
    CommandServer.write_server_conf(host=conf.get('hostAddress'), port=conf.get('port'),
                                    score_root=conf['scoreRootPath'], score_db_root=conf['stateDbRootPath'])

    # start server
    server = SimpleRestServer(port=conf.get('port'), ip_address=conf.get('hostAddress'))
    server.get_app().add_task(__serve)

    server.run()


async def init_icon_inner_task(conf: 'IconConfig'):
    global __icon_inner_task
    config = IconConfig("", conf)
    config.update_conf({ConfigKey.BUILTIN_SCORE_OWNER: conf['genesis']['accounts'][0]['address']})
    # TODO genesis address를 admin_address로 한다
    __icon_inner_task = IconScoreInnerTask(config)

    if is_done_genesis_invoke():
        return None

    tx_hash = create_hash(b'genesis')
    tx_timestamp_us = int(time.time() * 10 ** 6)
    request_params = {'txHash': tx_hash, 'timestamp': hex(tx_timestamp_us)}

    tx = {
        'method': '',
        'params': request_params,
        'genesisData': conf['genesis']
    }

    request = {'transactions': [tx]}
    block_height: int = get_block_height() + 1
    block_timestamp_us = tx_timestamp_us
    block_hash = create_hash(block_timestamp_us.to_bytes(8, DATA_BYTE_ORDER))

    request['block'] = {
        'blockHeight': hex(block_height),
        'blockHash': block_hash,
        'timestamp': hex(block_timestamp_us)
    }

    precommit_request = {'blockHeight': hex(block_height),
                         'blockHash': block_hash}

    response = await get_icon_inner_task().invoke(request)
    response = response['txResults']
    if not isinstance(response, dict):
        rollback_block()
        await get_icon_inner_task().remove_precommit_state(precommit_request)
    elif check_error_response(response):
        rollback_block()
        await get_icon_inner_task().remove_precommit_state(precommit_request)
    elif response[tx_hash]['status'] == hex(1):
        set_prev_block_hash(block_hash)
        set_block_height()
        await get_icon_inner_task().write_precommit_state(precommit_request)
    else:
        rollback_block()
        await get_icon_inner_task().remove_precommit_state(precommit_request)

    tx_result = response[tx_hash]
    tx_result['from'] = request_params.get('from', '')
    # tx_result['txHash'] must start with '0x'
    # tx_hash must not start with '0x'
    if tx_hash[:2] != '0x':
        tx_result['txHash'] = f'0x{tx_hash}'
    else:
        tx_result['txHash'] = tx_hash
        tx_hash = tx_hash[2:]

    # save transaction result
    save_txresult(tx_hash, tx_result)

    # save block
    save_block(block_hash=block_hash, block_height=block_height, tx=conf['genesis'])

    return response_to_json_invoke(response)


def init_tbears(conf: 'IconConfig'):
    global __tx_result_mapper
    __tx_result_mapper = TxResultMapper()
    global TBEARS_DB
    TBEARS_DB = TbearsDB(TbearsDB.make_db(f'{conf["stateDbRootPath"]}/tbears'))
    load_tbears_global_variable()


def load_tbears_global_variable():
    global __block_height
    global __prev_block_hash

    byte_block_height = TBEARS_DB.get(DB_PREFIX_BLOCK_HEIGHT)
    byte_prev_block_hash = TBEARS_DB.get(DB_PREFIX_PREV_BLOCK)

    if byte_block_height is not None:
        block_height = byte_block_height.decode()
        __block_height = int(block_height)
    if byte_prev_block_hash is not None:
        __prev_block_hash = bytes.hex(byte_prev_block_hash)


def is_done_genesis_invoke() -> bool:
    return get_prev_block_hash()


def save_transaction(tx_hash: str, params: dict, block_hash: str, block_height: int):
    value = deepcopy(params)
    del value['txHash']
    value['txIndex'] = "0x0"
    value['blockHeight'] = hex(block_height)
    value['blockHash'] = f'0x{block_hash}'

    TBEARS_DB.put(DB_PREFIX_TX + bytes.fromhex(tx_hash), json.dumps(value).encode())


def save_txresult(tx_hash: str, tx_result):
    TBEARS_DB.put(DB_PREFIX_TXRESULT + bytes.fromhex(tx_hash), json.dumps(tx_result).encode())


def save_block(block_hash: str, block_height: int, tx: Union[str, dict], prev_block_hash: str = ""):
    is_genesis = isinstance(tx, dict)
    block = {
        "version": "tbears",
        "prev_block_hash": prev_block_hash,
        "merkle_tree_root_hash": "tbears_does_not_support_merkel_tree",
        "time_stamp": int(time.time() * 10 ** 6),
        "confirmed_transaction_list": [f'0x{tx}'] if not is_genesis else tx,
        "block_hash": block_hash,
        "height": block_height,
        "peer_id": str(uuid.uuid1()) if not is_genesis else "",
        "signature": "tbears_does_not_support_signature" if not is_genesis else ""
    }

    # save block
    TBEARS_DB.put(DB_PREFIX_BLOCK + bytes.fromhex(block_hash), json.dumps(block).encode())

    # save block id/hash
    TBEARS_DB.put(DB_PREFIX_BLOCK_INDEX + block_height.to_bytes(32, DATA_BYTE_ORDER), bytes.fromhex(block_hash))


def get_block_by_height(block_height: int):
    block_hash: bytes = TBEARS_DB.get(DB_PREFIX_BLOCK_INDEX + block_height.to_bytes(32, DATA_BYTE_ORDER))

    return get_block_by_hash(block_hash=block_hash)


def get_block_by_hash(block_hash: bytes):
        try:
            block: bytes = TBEARS_DB.get(DB_PREFIX_BLOCK + block_hash)
            block_json = get_block_result(json.loads(block))
        except Exception:
            raise GenericJsonRpcServerError(
                code=InvalidParams.code,
                message=f"Can't get block information",
                http_status=status.HTTP_BAD_REQUEST)
        else:
            return block_json


def get_block_result(block: dict):
    tx_list = block.get('confirmed_transaction_list', None)
    if tx_list is not None and isinstance(tx_list, list):
        result_list = []
        for tx in tx_list:
            if isinstance(tx, dict):
                # genesis block
                result_list.append(tx)
                break
            tx_result = get_transaction(tx_hash=tx)
            del tx_result['txIndex']
            del tx_result['blockHeight']
            del tx_result['blockHash']
            result_list.append(tx_result)

        block['confirmed_transaction_list'] = result_list

    return block


def get_transaction(tx_hash: str):
    tx_payload = TBEARS_DB.get(DB_PREFIX_TX + bytes.fromhex(tx_hash[2:]))
    tx_payload_json = json.loads(tx_payload)

    return tx_payload_json


if __name__ == '__main__':
    serve()
