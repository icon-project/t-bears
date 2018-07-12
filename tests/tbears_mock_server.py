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


from tbears.server.jsonrpc_server import init_tbears, init_icon_inner_task, load_config, SimpleRestServer, \
    destruct_engine


def init_mock_server(path: str='./tbears.json'):
    """Mock sanic server for unit testing.

    :param path: Configuration file path to refer.
    :return:
    """

    async def __serve():
        init_tbears(conf)
        await init_icon_inner_task(conf)
    conf = load_config(path, None)
    server = SimpleRestServer(conf['port'], "0.0.0.0")
    server.get_app().add_task(__serve)

    return server.get_app()


API_PATH = '/api/v3/'
