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
import logging
import sys
import time
import hashlib

from jsonrpcserver.aio import methods
from sanic import Sanic, response

from iconservice.icon_inner_service import IconScoreInnerStub
from iconservice import configure as conf
from iconservice.utils.type_converter import TypeConverter

sys.path.append('..')
sys.path.append('.')

__block_height = 0
__icon_score_stub = None
__type_converter = None


def get_icon_score_stub() -> IconScoreInnerStub:
    global __icon_score_stub
    return __icon_score_stub


def get_type_converter() -> TypeConverter:
    global __type_converter
    return __type_converter


def create_icon_score_stub(channel: str, amqp_key: str, amqp_target: str, peer_id: str, peer_port: str,
                           **kwargs) -> IconScoreInnerStub:
    icon_score_queue_name = conf.ICON_SCORE_QUEUE_NAME_FORMAT.format(channel_name=channel,
                                                                     amqp_key=amqp_key,
                                                                     peer_id=peer_id,
                                                                     peer_port=peer_port)
    return IconScoreInnerStub(amqp_target, icon_score_queue_name)


def get_block_height():
    global __block_height
    __block_height += 1
    return __block_height


def shutdown():
    """Shutdown flask server.
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


class MockDispatcher:

    @staticmethod
    async def dispatch(request):
        req = json.loads(request.body.decode())
        print(req)
        req["params"] = req.get("params", {})
        req["params"]["method"] = request.json["method"]

        dispatch_response = await methods.dispatch(req)
        return response.json(dispatch_response, status=dispatch_response.http_status)

    @staticmethod
    @methods.add
    async def hello(**kwargs):
        print(f'json_rpc_server hello! {kwargs}')

    @staticmethod
    @methods.add
    async def icx_sendTransaction(**kwargs):
        """ icx_sendTransaction jsonrpc handler.
        We assume that only one tx in a block.

        :param kwargs: jsonrpc params field.
        """

        print(f'json_rpc_server icx_sendTransaction! {kwargs}')

        make_request = dict()

        block_height: int = get_block_height()
        data: str = f'block_height{block_height}'
        block_hash: str = hashlib.sha3_256(data.encode()).digest()
        block_timestamp_us = int(time.time() * 10 ** 6)
        make_request['block'] = {'block_height': block_height,
                                 'block_hash': block_hash,
                                 'block_timestamp': block_timestamp_us}
        params = get_type_converter().convert(kwargs, recursive=False)
        tx = {
            'method': 'icx_send_transaction',
            'params': params
        }
        make_request['transactions'] = [tx]
        response = await get_icon_score_stub().task().icx_send_transaction(make_request)
        return response

    @staticmethod
    @methods.add
    async def icx_call(**params):
        params = get_type_converter.convert(params, recursive=False)
        make_request = {'method': 'icx_call', 'params': params}
        response = await get_icon_score_stub().task().icx_call(make_request)
        return response

    @staticmethod
    @methods.add
    async def icx_getBalance(**params):
        params = get_type_converter.convert(params, recursive=False)
        make_request = {'method': 'icx_get_balance', 'params': params}
        response = await get_icon_score_stub().task().icx_call(make_request)
        return response

    @staticmethod
    @methods.add
    async def icx_getTotalSupply(**params):
        params = get_type_converter().convert(params, recursive=False)
        make_request = {'method': 'icx_get_total_supply', 'params': params}
        response = await get_icon_score_stub().task().icx_call(make_request)
        return response

    @staticmethod
    @methods.add
    async def server_exit():
        await get_icon_score_stub().task().close()
        shutdown()


class FlaskServer():
    def __init__(self):
        self.__app = Sanic(__name__)

    @property
    def app(self):
        return self.__app

    @property
    def ssl_context(self):
        return self.__ssl_context

    def set_resource(self):
        self.__app.add_route(MockDispatcher.dispatch, '/api/v2', methods=['POST'])


class SimpleRestServer():
    def __init__(self, port, ip_address=None):
        self.__port = port
        self.__ip_address = ip_address

        self.__server = FlaskServer()
        self.__server.set_resource()

    def get_app(self):
        return self.__server.app

    def run(self):
        logging.error(f"SimpleRestServer run... {self.__port}")
        self.__server.app.run(port=self.__port,
                              host=self.__ip_address,
                              debug=False)


def serve():
    async def __serve():
        init_type_converter()
        await init_icon_score_stub(tbears_conf)

    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = './tbears.json'

    logging.info(f'config_file: {path}')
    tbears_conf = load_config(path)

    server = SimpleRestServer(tbears_conf['port'])
    server.get_app().add_task(__serve)
    server.run()


def load_config(path: str) -> dict:
    default_conf = {
        "from": "hxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "port": 9000,
        "score_root": "./.score",
        "db_root": "./.db",
        "accounts": [
            {
                "name": "genesis",
                "address": "hx0000000000000000000000000000000000000000",
                "balance": "0x2961fff8ca4a62327800000"
            },
            {
                "name": "treasury",
                "address": "hx1000000000000000000000000000000000000000",
                "balance": "0x0"
            }
        ]
    }

    try:
        with open(path) as f:
            tbears_conf = json.load(f)
    except (OSError, IOError):
        return default_conf

    for key in default_conf:
        if key not in tbears_conf:
            tbears_conf[key] = default_conf[key]

    return tbears_conf


async def init_icon_score_stub(tbears_conf: dict):
    global __icon_score_stub
    __icon_score_stub = create_icon_score_stub(**conf.DEFAULT_ICON_SERVICE_FOR_TBEARS_ARGUMENT)
    await __icon_score_stub.connect()

    accounts = get_type_converter().convert(tbears_conf['accounts'], recursive=False)
    await __icon_score_stub.task().genesis_invoke(accounts)


def init_type_converter():
    global __type_converter

    type_table = {
        'from': 'address',
        'to': 'address',
        'address': 'address',
        'fee': 'int',
        'value': 'int',
        'balance': 'int'
    }
    __type_converter = TypeConverter(type_table)


if __name__ == '__main__':
    serve()
