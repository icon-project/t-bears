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
import sys
import argparse
import time
import setproctitle
from copy import deepcopy

from earlgrey import MessageQueueService
from iconcommons.logger import Logger
from iconcommons.icon_config import IconConfig
from iconservice.icon_constant import DATA_BYTE_ORDER, DEFAULT_BYTE_SIZE

from tbears.config.tbears_config import ConfigKey, tbears_server_config
from tbears.block_manager.channel_service import ChannelService
from tbears.block_manager.block import Block
from tbears.block_manager.icon_service import IconStub
from tbears.block_manager.periodic import Periodic
from tbears.util import create_hash


TBEARS_BLOCK_MANAGER = 'tbears_block_manager'


CHANNEL_QUEUE_NAME_FORMAT = "Channel.{channel_name}.{amqp_key}"
ICON_SCORE_QUEUE_NAME_FORMAT = "IconScore.{channel_name}.{amqp_key}"


class BlockManager(object):
    def __init__(self, conf: 'IconConfig'):
        self._conf = conf
        self._channel_mq_name = None
        self._icon_mq_name = None
        self._amqp_target = None
        self._channel_service = None
        self._icon_stub = None
        self._block = Block(conf=conf)
        self._tx_queue = []

    def serve(self):
        async def _serve():
            await self.init()
            Logger.info(f'Start tbears block_manager serve!', TBEARS_BLOCK_MANAGER)

        channel = self._conf[ConfigKey.CHANNEL]
        amqp_key = self._conf[ConfigKey.AMQP_KEY]
        amqp_target = self._conf[ConfigKey.AMQP_TARGET]

        self._icon_mq_name = ICON_SCORE_QUEUE_NAME_FORMAT.format(channel_name=channel, amqp_key=amqp_key)
        self._channel_mq_name = CHANNEL_QUEUE_NAME_FORMAT.format(channel_name=channel, amqp_key=amqp_key)
        self._amqp_target = amqp_target

        Logger.info(f'==========tbears block_manager params==========', TBEARS_BLOCK_MANAGER)
        Logger.info(f'amqp_target  : {amqp_target}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'amqp_key  :  {amqp_key}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'queue_name  : {self._channel_mq_name}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'            : {self._icon_mq_name}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'==========tbears block_manager params==========', TBEARS_BLOCK_MANAGER)

        # start message queue service
        loop = MessageQueueService.loop
        loop.create_task(_serve())
        loop.run_forever()

    async def init(self):
        Logger.debug(f'Initialize started!!', TBEARS_BLOCK_MANAGER)

        await self._init_channel()

        await self._init_icon()

        await self._init_periodic()

        Logger.debug(f'Initialize done!!', TBEARS_BLOCK_MANAGER)

    async def _init_channel(self):
        Logger.debug(f'Initialize channel started!!', TBEARS_BLOCK_MANAGER)

        self._channel_service = ChannelService(self._amqp_target, self._channel_mq_name,
                                               conf=self._conf,
                                               block_manager=self)

        await self._channel_service.connect(exclusive=True)

        Logger.debug(f'Initialize channel done!!', TBEARS_BLOCK_MANAGER)

    async def _init_icon(self):
        Logger.debug(f'Initialize ICON started!!', TBEARS_BLOCK_MANAGER)

        # make MQ stub
        self._icon_stub = IconStub(amqp_target=self._amqp_target, route_key=self._icon_mq_name)

        await self._icon_stub.connect()
        await self._icon_stub.async_task().hello()

        # send genesis block
        if self._block.get_prev_block_hash():
            Logger.debug(f'Initialize ICON done!!', TBEARS_BLOCK_MANAGER)
            return None

        tx_hash = create_hash(b'genesis')
        tx_timestamp_us = int(time.time() * 10 ** 6)
        request_params = {'txHash': tx_hash, 'timestamp': hex(tx_timestamp_us)}

        tx = {
            'method': '',
            'params': request_params,
            'genesisData': self._conf['genesis']
        }

        request = {'transactions': [tx]}
        block_height: int = self._block.get_block_height() + 1
        block_timestamp_us = tx_timestamp_us
        block_hash = create_hash(block_timestamp_us.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER))

        request['block'] = {
            'blockHeight': hex(block_height),
            'blockHash': block_hash,
            'timestamp': hex(block_timestamp_us)
        }

        response = await self._icon_stub.async_task().invoke(request)

        response = response['txResults']

        precommit_request = {'blockHeight': hex(block_height),
                             'blockHash': block_hash}
        await self._icon_stub.async_task().write_precommit_state(precommit_request)

        # confirm block
        self._block.confirm_block(prev_block_hash=block_hash)

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
        self._block.save_txresult(tx_hash, tx_result)

        # save block
        self._block.save_block(block_hash=block_hash, tx=self._conf['genesis'], timestamp=block_timestamp_us)

        Logger.debug(f'Initialize ICON done!!', TBEARS_BLOCK_MANAGER)

    async def _init_periodic(self):
        Logger.debug(f'Initialize periodic task started!!', TBEARS_BLOCK_MANAGER)

        self.periodic = Periodic(func=self.confirm_block, interval=10)
        await self.periodic.start()

        Logger.debug(f'Initialize periodic task done!!', TBEARS_BLOCK_MANAGER)

    def add_tx(self, tx_hash: str, tx: dict):
        tx_copy = deepcopy(tx)

        # add txHash
        tx_copy['txHash'] = tx_hash
        # add from
        tx_copy['from'] = tx_copy.get('from', '')

        self._tx_queue.append((tx_hash, tx_copy))

    def get_tx(self) -> list:
        return self._tx_queue

    def clear_tx(self) -> list:
        tx_queue: list = self._tx_queue
        self._tx_queue = []

        return tx_queue

    async def confirm_block(self):
        Logger.debug(f'confirm block started!!', TBEARS_BLOCK_MANAGER)

        # clear tx_queue
        tx_list = self.clear_tx()

        # make block hash. tbears block_manager is dev util
        block_timestamp_us = int(time.time() * 10 ** 6)
        block_hash = create_hash(block_timestamp_us.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER))

        # send invoke message to ICON
        response = await self._invoke_block(tx_list=tx_list, block_hash=block_hash, block_timestamp=block_timestamp_us)
        if response is None:
            return

        # confirm block
        self._block.confirm_block(prev_block_hash=block_hash)

        # save transaction result
        self._block.save_txresults(tx_list, response)

        # save transactions
        self._block.save_transactions(tx_list=tx_list, block_hash=block_hash)

        # save block
        self._block.save_block(block_hash=block_hash, tx=tx_list, timestamp=block_timestamp_us)

        Logger.debug(f'confirm block done!!', TBEARS_BLOCK_MANAGER)

    async def _invoke_block(self, tx_list: list, block_hash: str, block_timestamp) -> dict:
        block = self._block
        block_height = block.get_block_height() + 1
        prev_block_hash = block.get_prev_block_hash()

        transactions = []
        for tx in tx_list:
            transaction = {
                "method": 'icx_sendTransaction',
                "params": tx[1]
            }
            transactions.append(transaction)

        request = {
            'block': {
                'blockHeight': hex(block_height),
                'blockHash': block_hash,
                'prevBlockHash': prev_block_hash,
                'timestamp': hex(block_timestamp)
            },
            'transactions': transactions
        }

        # send invoke to iconservice
        response = await self._icon_stub.async_task().invoke(request)

        if 'error' in response:
            return None

        precommit_request = {'blockHeight': hex(block_height),
                             'blockHash': block_hash}

        # send write_prevommit_state to iconservice
        await self._icon_stub.async_task().write_precommit_state(precommit_request)

        return response["txResults"]


def create_parser():
    parser = argparse.ArgumentParser(prog='tbears_block_manager',
                                     description=f'tbears_block_manager v arguments')
    parser.add_argument('-ch', dest=ConfigKey.CHANNEL, help='Message Queue channel')
    parser.add_argument('-at', dest=ConfigKey.AMQP_TARGET, help='AMQP traget info')
    parser.add_argument('-ak', dest=ConfigKey.AMQP_KEY,
                        help="key sharing peer group using queue name. use it if one more peers connect one MQ")
    parser.add_argument('-c', '--config', help='Configuration file path')

    return parser


def main():
    # Parse arguments.
    try:
        parser = create_parser()
    except Exception as e:
        exit(f"Argument parsing exception : {e}")

    args = parser.parse_args(sys.argv[1:])

    if args.config:
        conf_path = args.config
        if not IconConfig.valid_conf_path(conf_path):
            print(f'Invalid configuration file : {conf_path}')
            sys.exit(1)
    else:
        conf_path = str()

    # Load configuration
    conf = IconConfig(conf_path, tbears_server_config)
    conf.load()
    conf.update_conf(dict(vars(args)))
    Logger.load_config(conf)
    Logger.print_config(conf, TBEARS_BLOCK_MANAGER)

    setproctitle.setproctitle(f'{TBEARS_BLOCK_MANAGER}.{conf[ConfigKey.CHANNEL]}.{conf[ConfigKey.AMQP_KEY]}')

    # run block_manager service
    block_manager = BlockManager(conf=conf)
    block_manager.serve()

    Logger.info('===============tbears block_manager done================', TBEARS_BLOCK_MANAGER)


if __name__ == '__main__':
    main()
