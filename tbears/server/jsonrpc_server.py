# Copyright 2017-2018 theloop Inc.
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
from json import JSONDecodeError
import argparse
from ipaddress import ip_address

from iconservice.icon_constant import DATA_BYTE_ORDER, ICON_SCORE_QUEUE_NAME_FORMAT, ConfigKey
from jsonrpcserver import status
from jsonrpcserver.aio import methods
from jsonrpcserver.exceptions import JsonRpcServerError, InvalidParams
from sanic import Sanic, response as sanic_response

from iconservice.icon_inner_service import IconScoreInnerService, IconScoreInnerStub
from iconservice.utils import check_error_response
from iconservice.icon_config import default_icon_config
from tbears.config.tbears_config import tbears_config
from icon_common.icon_config import IconConfig
from icon_common.logger import Logger

from typing import Optional

from tbears.server.tbears_db import TbearsDB
from tbears.command.command_server import CommandServer

MQ_TEST = False
if not MQ_TEST:
    from iconservice.icon_inner_service import IconScoreInnerTask

TBEARS_LOG_TAG = 'tbears'
SEPARATE_PROCESS_DEBUG = False

__block_height = -1
__prev_block_hash = None
__icon_score_service = None
__icon_score_stub = None
__icon_inner_task = None
__tx_result_mapper = None

sys.path.append('..')
sys.path.append('.')

TBEARS_DB = None


def create_hash(data: bytes) -> str:
    return f'{hashlib.sha3_256(data).hexdigest()}'


def get_icon_inner_task() -> Optional['IconScoreInnerTask']:
    global __icon_inner_task
    return __icon_inner_task


def get_icon_score_stub() -> 'IconScoreInnerStub':
    global __icon_score_stub
    return __icon_score_stub


def create_icon_score_service() -> 'IconScoreInnerService':
    conf = IconConfig("", default_icon_config)
    conf.load()

    icon_score_root_path = conf[ConfigKey.ICON_SCORE_ROOT]
    icon_score_state_db_root_path = conf[ConfigKey.ICON_SCORE_STATE_DB_ROOT_PATH]
    amqp_target = conf[ConfigKey.AMQP_TARGET]

    icon_score_queue_name = ICON_SCORE_QUEUE_NAME_FORMAT.format(**
                                                                {ConfigKey.CHANNEL: conf[ConfigKey.CHANNEL],
                                                                 ConfigKey.AMQP_KEY: conf[ConfigKey.AMQP_KEY]})

    Logger.debug(f'==========create_icon_score_service==========', TBEARS_LOG_TAG)
    Logger.debug(f'icon_score_root_path : {icon_score_root_path}', TBEARS_LOG_TAG)
    Logger.debug(f'icon_score_state_db_root_path  : {icon_score_state_db_root_path}', TBEARS_LOG_TAG)
    Logger.debug(f'amqp_target  : {amqp_target}', TBEARS_LOG_TAG)
    Logger.debug(f'icon_score_queue_name  : {icon_score_queue_name}', TBEARS_LOG_TAG)
    Logger.debug(f'==========create_icon_score_service==========', TBEARS_LOG_TAG)

    return IconScoreInnerService(amqp_target, icon_score_queue_name, conf=conf)


def create_icon_score_stub() -> 'IconScoreInnerStub':
    conf = IconConfig("", default_icon_config)
    conf.load()

    icon_score_queue_name = ICON_SCORE_QUEUE_NAME_FORMAT.format(**
                                                                {ConfigKey.CHANNEL: conf[ConfigKey.CHANNEL],
                                                                 ConfigKey.AMQP_KEY: conf[ConfigKey.AMQP_KEY]})

    Logger.debug(f'==========create_icon_score_stub==========', TBEARS_LOG_TAG)
    Logger.debug(f'icon_score_queue_name  : {icon_score_queue_name}', TBEARS_LOG_TAG)
    Logger.debug(f'==========create_icon_score_stub==========', TBEARS_LOG_TAG)

    return IconScoreInnerStub(conf[ConfigKey.AMQP_TARGET], icon_score_queue_name)


def get_block_height():
    global __block_height
    __block_height += 1
    TBEARS_DB.put(b'blockHeight', str(__block_height).encode())
    return __block_height


def get_prev_block_hash():
    global __prev_block_hash
    return __prev_block_hash


def set_prev_block_hash(block_hash: str):
    global __prev_block_hash
    __prev_block_hash = block_hash
    TBEARS_DB.put(b'prevBlockHash', bytes.fromhex(__prev_block_hash))


def rollback_block():
    global __block_height
    __block_height -= 1
    TBEARS_DB.put(b'blockHeight', str(__block_height).encode())


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

        method = 'icx_sendTransaction'
        # Insert txHash into request params
        tx_hash = create_hash(json.dumps(request_params).encode())
        request_params['txHash'] = tx_hash
        tx = {
            'method': method,
            'params': request_params
        }

        # pre validate
        if MQ_TEST:
            response = await get_icon_score_stub().async_task().validate_transaction(tx)
            response_to_json_query(response)
        else:
            response = await get_icon_inner_task().validate_transaction(tx)
            response_to_json_query(response)

        # prepare request data to invoke
        make_request = {'transactions': [tx]}
        block_height: int = get_block_height()
        block_timestamp_us = int(time.time() * 10 ** 6)
        block_hash = create_hash(block_timestamp_us.to_bytes(8, DATA_BYTE_ORDER))

        make_request['block'] = {
            'blockHeight': hex(block_height),
            'blockHash': block_hash,
            'timestamp': hex(block_timestamp_us),
            'prevBlockHash': get_prev_block_hash()
        }

        precommit_request = {'blockHeight': hex(block_height),
                             'blockHash': block_hash}
        # invoke
        if MQ_TEST:
            response = await get_icon_score_stub().async_task().invoke(make_request)
            response = response['txResults']
            if not isinstance(response, dict):
                rollback_block()
                await get_icon_score_stub().async_task().remove_precommit_state(precommit_request)
            elif check_error_response(response):
                rollback_block()
                await get_icon_score_stub().async_task().remove_precommit_state(precommit_request)
            elif response[tx_hash]['status'] == hex(1):
                set_prev_block_hash(block_hash)
                await get_icon_score_stub().async_task().write_precommit_state(precommit_request)
            else:
                rollback_block()
                await get_icon_score_stub().async_task().remove_precommit_state(precommit_request)

            tx_result = response[tx_hash]
            tx_hash = f'0x{tx_result["txHash"]}'
            tx_result['from'] = request_params.get('from', '')
            tx_result['txHash'] = tx_hash
            TBEARS_DB.put(f'{tx_hash}-result'.encode(), json.dumps(tx_result).encode())
            return response_to_json_invoke(response)
        else:
            response = await get_icon_inner_task().invoke(make_request)
            response = response['txResults']
            if not isinstance(response, dict):
                rollback_block()
                await get_icon_inner_task().remove_precommit_state(precommit_request)
            elif check_error_response(response):
                rollback_block()
                await get_icon_inner_task().remove_precommit_state(precommit_request)
            elif response[tx_hash]['status'] == hex(1):
                set_prev_block_hash(block_hash)
                await get_icon_inner_task().write_precommit_state(precommit_request)
            else:
                rollback_block()
                await get_icon_inner_task().remove_precommit_state(precommit_request)

            tx_result = response[tx_hash]
            tx_hash = f'0x{tx_result["txHash"]}'
            tx_result['from'] = request_params.get('from', '')
            tx_result['txHash'] = tx_hash
            TBEARS_DB.put(f'{tx_hash}-result'.encode(), json.dumps(tx_result).encode())
            return response_to_json_invoke(response)

    @staticmethod
    @methods.add
    async def icx_call(**request_params):
        Logger.debug(f'json_rpc_server icx_call!', TBEARS_LOG_TAG)

        method = 'icx_call'
        make_request = {'method': method, 'params': request_params}

        if MQ_TEST:
            response = await get_icon_score_stub().async_task().query(make_request)
            return response_to_json_query(response)
        else:
            response = await get_icon_inner_task().query(make_request)
            return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getBalance(**request_params):
        Logger.debug(f'json_rpc_server icx_getBalance!', TBEARS_LOG_TAG)

        method = 'icx_getBalance'
        make_request = {'method': method, 'params': request_params}

        if MQ_TEST:
            response = await get_icon_score_stub().async_task().query(make_request)
            return response_to_json_query(response)
        else:
            response = await get_icon_inner_task().query(make_request)
            return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(**request_params):
        Logger.debug(f'json_rpc_server icx_getTotalSupply!', TBEARS_LOG_TAG)

        method = 'icx_getTotalSupply'
        make_request = {'method': method, 'params': request_params}

        if MQ_TEST:
            response = await get_icon_score_stub().async_task().query(make_request)
            return response_to_json_query(response)
        else:
            response = await get_icon_inner_task().query(make_request)
            return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def icx_getTransactionResult(**request_params):
        Logger.debug(f'json_rpc_server getTransactionResult!', TBEARS_LOG_TAG)

        try:
            tx_hash = request_params['txHash']
            tx_hash_result = TBEARS_DB.get(f'{tx_hash}-result'.encode())
            tx_hash_result_str = tx_hash_result.decode()
            tx_result_json = json.loads(tx_hash_result_str)
            return tx_result_json
        except Exception:
            raise GenericJsonRpcServerError(
                code=InvalidParams.code,
                message='TransactionResult not found',
                http_status=status.HTTP_BAD_REQUEST)

    @staticmethod
    @methods.add
    async def icx_getScoreApi(**request_params):
        Logger.debug(f'json_rpc_server icx_getScoreApi!', TBEARS_LOG_TAG)

        method = 'icx_getScoreApi'
        make_request = {'method': method, 'params': request_params}

        if MQ_TEST:
            response = await get_icon_score_stub().async_task().query(make_request)
            return response_to_json_query(response)
        else:
            response = await get_icon_inner_task().query(make_request)
            return response_to_json_query(response)

    @staticmethod
    @methods.add
    async def server_exit(**request_params):
        Logger.debug(f'json_rpc_server server_exit!', TBEARS_LOG_TAG)

        if MQ_TEST:
            await get_icon_score_stub().async_task().close()

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
    parser.add_argument('-c', '--config', help='tbears configuration file path (default: ./tbears.json)')

    return parser


def serve():
    async def __serve():
        init_tbears(conf)
        if MQ_TEST:
            if not SEPARATE_PROCESS_DEBUG:
                await init_icon_score_service()
            await init_icon_score_stub(conf)
        else:
            await init_icon_inner_task(conf)

    # create parser
    parser = create_parser()

    # parse argument
    args = parser.parse_args(sys.argv[1:])

    if args.config:
        path = args.config
    else:
        path = './tbears.json'

    conf = _load_config(path, args)

    # init logger
    Logger.load_config(conf)
    Logger.info(f'config_file: {path}', TBEARS_LOG_TAG)

    # write conf for tbears_cli
    CommandServer.write_server_conf(host=conf.get('hostAddress'), port=conf.get('port'))

    # start server
    server = SimpleRestServer(port=conf.get('port'), ip_address=conf.get('hostAddress'))
    server.get_app().add_task(__serve)

    server.run()


def _load_config(path: str, args) -> 'IconConfig':
    conf = IconConfig(path, tbears_config)
    if args:
        if args.address:
            Logger.debug(f'args.address: {args.address}', TBEARS_LOG_TAG)
            conf['hostAddress'] = str(args.address)
        if args.port:
            conf['port'] = args.port

    return conf


async def init_icon_score_service():
    global __icon_score_service
    __icon_score_service = create_icon_score_service()
    await __icon_score_service.connect(exclusive=True)


async def init_icon_score_stub(conf: 'IconConfig'):
    global __icon_score_stub
    __icon_score_stub = create_icon_score_stub()

    if is_done_genesis_invoke():
        return None

    tx_hash = create_hash('genesis'.encode())
    tx_timestamp_us = int(time.time() * 10 ** 6)
    request_params = {'txHash': tx_hash, 'timestamp': hex(tx_timestamp_us)}
    tx = {
        'method': '',
        'params': request_params,
        'genesisData': {'accounts': conf['accounts']}
    }

    make_request = {'transactions': [tx]}
    block_height: int = get_block_height()
    block_timestamp_us = tx_timestamp_us
    block_hash = create_hash(block_timestamp_us.to_bytes(8, DATA_BYTE_ORDER))

    make_request['block'] = {
        'blockHeight': hex(block_height),
        'blockHash': block_hash,
        'timestamp': hex(block_timestamp_us)
    }

    precommit_request = {'blockHeight': hex(block_height),
                         'blockHash': block_hash}

    response = await get_icon_score_stub().async_task().invoke(make_request)
    if not isinstance(response, dict):
        rollback_block()
        await get_icon_score_stub().async_task().remove_precommit_state(precommit_request)
    elif check_error_response(response):
        rollback_block()
        await get_icon_score_stub().async_task().remove_precommit_state(precommit_request)
    elif response[tx_hash]['status'] == hex(1):
        set_prev_block_hash(block_hash)
        await get_icon_score_stub().async_task().write_precommit_state(precommit_request)
    else:
        rollback_block()
        await get_icon_score_stub().async_task().remove_precommit_state(precommit_request)

    tx_result = response[tx_hash]
    tx_hash = tx_result['txHash']
    tx_hash = f'0x{tx_hash}'
    tx_result['from'] = request_params.get('from', '')
    tx_result['tx_hash'] = tx_hash
    TBEARS_DB.put(tx_hash.encode(), json.dumps(tx_result).encode())
    return response_to_json_invoke(response)


async def init_icon_inner_task(conf: 'IconConfig'):
    global __icon_inner_task
    config = IconConfig("", default_icon_config)
    config.load({ConfigKey.ADMIN_ADDRESS: conf['accounts'][0]['address'],
                 ConfigKey.ICON_SCORE_ROOT: conf['scoreRoot'],
                 ConfigKey.ICON_SCORE_STATE_DB_ROOT_PATH: conf['dbRoot']})
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
        'genesisData': {'accounts': conf['accounts']}
    }

    make_request = {'transactions': [tx]}
    block_height: int = get_block_height()
    block_timestamp_us = tx_timestamp_us
    block_hash = create_hash(block_timestamp_us.to_bytes(8, DATA_BYTE_ORDER))

    make_request['block'] = {
        'blockHeight': hex(block_height),
        'blockHash': block_hash,
        'timestamp': hex(block_timestamp_us)
    }

    precommit_request = {'blockHeight': hex(block_height),
                         'blockHash': block_hash}

    response = await get_icon_inner_task().invoke(make_request)
    response = response['txResults']
    if not isinstance(response, dict):
        rollback_block()
        await get_icon_inner_task().remove_precommit_state(precommit_request)
    elif check_error_response(response):
        rollback_block()
        await get_icon_inner_task().remove_precommit_state(precommit_request)
    elif response[tx_hash]['status'] == hex(1):
        set_prev_block_hash(block_hash)
        await get_icon_inner_task().write_precommit_state(precommit_request)
    else:
        rollback_block()
        await get_icon_inner_task().remove_precommit_state(precommit_request)

    tx_result = response[tx_hash]
    tx_hash = tx_result['txHash']
    tx_hash = f'0x{tx_hash}'
    tx_result['from'] = request_params.get('from', '')
    tx_result['tx_hash'] = tx_hash
    TBEARS_DB.put(tx_hash.encode(), json.dumps(tx_result).encode())
    return response_to_json_invoke(response)


def init_tbears(conf: 'IconConfig'):
    global __tx_result_mapper
    __tx_result_mapper = TxResultMapper()
    global TBEARS_DB
    TBEARS_DB = TbearsDB(TbearsDB.make_db(f'{conf["dbRoot"]}/tbears'))
    load_tbears_global_variable()


def load_tbears_global_variable():
    global __block_height
    global __prev_block_hash

    byte_block_height = TBEARS_DB.get(b'blockHeight')
    byte_prev_block_hash = TBEARS_DB.get(b'prevBlockHash')

    if byte_block_height is not None:
        block_height = byte_block_height.decode()
        __block_height = int(block_height)
    if byte_prev_block_hash is not None:
        __prev_block_hash = bytes.hex(byte_prev_block_hash)


def is_done_genesis_invoke() -> bool:
    return get_prev_block_hash()


if __name__ == '__main__':
    serve()
