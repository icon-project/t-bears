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

import argparse
from typing import Optional

import setproctitle
import sys
import time
from asyncio import get_event_loop
from copy import deepcopy

from earlgrey import MessageQueueService
from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger
from iconservice.icon_constant import DATA_BYTE_ORDER, DEFAULT_BYTE_SIZE

from tbears.block_manager.block import Block
from tbears.block_manager.channel_service import ChannelService, ChannelTxCreatorService
from tbears.block_manager.icon_service import IconStub
from tbears.block_manager.periodic import Periodic
from tbears.config.tbears_config import ConfigKey, tbears_server_config
from tbears.util import create_hash, get_tbears_version

TBEARS_BLOCK_MANAGER = 'tbears_block_manager'

ICON_SCORE_QUEUE_NAME_FORMAT = "IconScore.{channel_name}.{amqp_key}"
CHANNEL_QUEUE_NAME_FORMAT = "Channel.{channel_name}.{amqp_key}"
CHANNEL_TX_CREATOR_QUEUE_NAME_FORMAT = "ChannelTxCreator.{channel_name}.{amqp_key}"


class PRepManager(object):
    def __init__(self, is_generator_rotation: bool, prep_list: list):
        self._is_generator_rotation: bool = is_generator_rotation
        self._prep_list: list = prep_list

    @staticmethod
    def _create_prev_block_contributors_format(generator: str, validators: list) -> dict:
        prev_block_contributors_format = \
            {"prevBlockContributors": {
                "generator": generator,
                "validators": validators
            }}
        return prev_block_contributors_format

    def get_prev_block_contributors_info(self):
        if len(self._prep_list) == 0:
            prev_block_contributors_format = self._create_prev_block_contributors_format("", [])
            return prev_block_contributors_format

        prev_block_contributors_format = self._create_prev_block_contributors_format(self._prep_list[0],
                                                                                     self._prep_list[1:])
        Logger.debug(f"set block contributors format {prev_block_contributors_format}", TBEARS_BLOCK_MANAGER)
        if self._is_generator_rotation:
            self._prep_list.append(self._prep_list.pop(0))
            Logger.debug(f"generator rotated. generator: {self._prep_list[0]}", TBEARS_BLOCK_MANAGER)
        return prev_block_contributors_format


class BlockManager(object):
    def __init__(self, conf: 'IconConfig'):
        self._conf = conf
        self._channel_mq_name = None
        self._tx_creator_mq_name = None
        self._icon_mq_name = None
        self._amqp_target = None
        self._channel_service = None
        self._tx_creator_service = None
        self._icon_stub = None
        self._block: 'Block' = Block(f'{conf["stateDbRootPath"]}/tbears')
        self._tx_queue = []
        self._icon_is_issuable_version = False
        self._prep_manager: Optional['PRepManager'] = None
        
    @property
    def block(self) -> 'Block':
        return self._block

    def serve(self):
        async def _serve():
            try:
                await self.init()
            except RuntimeError as e:
                msg = f'Failed to connect to MQ. Check rabbitMQ service. ({e})'
                Logger.error(msg, TBEARS_BLOCK_MANAGER)
                print(msg)
                self.close()
                # TODO how to notify process status to parent process or system
                return

            Logger.info(f'tbears block_manager service started!', TBEARS_BLOCK_MANAGER)

        channel = self._conf[ConfigKey.CHANNEL]
        amqp_key = self._conf[ConfigKey.AMQP_KEY]
        amqp_target = self._conf[ConfigKey.AMQP_TARGET]

        self._channel_mq_name = CHANNEL_QUEUE_NAME_FORMAT.format(channel_name=channel, amqp_key=amqp_key)
        self._tx_creator_mq_name = CHANNEL_TX_CREATOR_QUEUE_NAME_FORMAT.format(channel_name=channel, amqp_key=amqp_key)
        self._icon_mq_name = ICON_SCORE_QUEUE_NAME_FORMAT.format(channel_name=channel, amqp_key=amqp_key)
        self._amqp_target = amqp_target

        Logger.info(f'==========tbears block_manager params==========', TBEARS_BLOCK_MANAGER)
        Logger.info(f'amqp_target : {amqp_target}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'amqp_key    : {amqp_key}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'queue_name  : {self._channel_mq_name}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'            : {self._tx_creator_mq_name}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'            : {self._icon_mq_name}', TBEARS_BLOCK_MANAGER)
        Logger.info(f'==========tbears block_manager params==========', TBEARS_BLOCK_MANAGER)

        # start message queue service
        loop = MessageQueueService.loop
        loop.create_task(_serve())
        loop.run_forever()

    async def init(self):
        """
        Initialize tbears block_manager
        :return:
        """
        Logger.debug(f'Initialize started!!', TBEARS_BLOCK_MANAGER)

        await self._init_channel()
        await self._init_tx_creator()
        await self._init_icon()
        await self._init_periodic()

        Logger.debug(f'Initialize done!!', TBEARS_BLOCK_MANAGER)

    async def _init_channel(self):
        """
        Initialize 'Channel' message queue
        :return:
        """
        Logger.debug(f'Initialize channel started!!', TBEARS_BLOCK_MANAGER)

        self._channel_service = ChannelService(self._amqp_target, self._channel_mq_name,
                                               block_manager=self)

        await self._channel_service.connect(exclusive=True)

        Logger.debug(f'Initialize channel done!!', TBEARS_BLOCK_MANAGER)

    async def _init_tx_creator(self):
        """
        Initialize 'ChannelTxCreator' message queue
        :return:
        """
        Logger.debug(f'Initialize tx creator started!!', TBEARS_BLOCK_MANAGER)

        self._tx_creator_service = ChannelTxCreatorService(self._amqp_target, self._tx_creator_mq_name,
                                                           block_manager=self)

        await self._tx_creator_service.connect(exclusive=True)

        Logger.debug(f'Initialize tx creator done!!', TBEARS_BLOCK_MANAGER)

    async def _init_icon(self):
        """
        Initialize 'IconScore' message queue and load genesis block if needed
        :return:
        """
        Logger.debug(f'Initialize ICON started!!', TBEARS_BLOCK_MANAGER)

        # make MQ stub
        self._icon_stub = IconStub(amqp_target=self._amqp_target, route_key=self._icon_mq_name)

        await self._icon_stub.connect()
        hello_response = await self._icon_stub.async_task().hello()
        Logger.debug(f'hello response with {hello_response}')

        if hello_response and hello_response.get('isIssuable') is not None:
            self._icon_is_issuable_version = bool(int(hello_response['isIssuable'], 16))
            # todo: modify naming: icon_is_issuable_version
            if self._icon_is_issuable_version:
                # todo: getting prep list using hello API is temporary
                #  solution, after define API, should change the code
                prep_list = hello_response.get('pRepList', [])
                Logger.debug(f'ICON service is issuable', TBEARS_BLOCK_MANAGER)
                Logger.debug(f'Prep list: {prep_list}', TBEARS_BLOCK_MANAGER)
                if len(prep_list) == 0:
                    Logger.warning(
                        "There is no prep to set even though icon service is issuable version. "
                        "insert prep using icon service config otherwise, icon service will not run properly",
                        TBEARS_BLOCK_MANAGER)
                self._prep_manager = PRepManager(
                    is_generator_rotation=self._conf[ConfigKey.BLOCK_GENERATOR_ROTATION],
                    prep_list=prep_list)

        # send genesis block
        if self.block.block_height != -1:
            Logger.debug(f'Initialize ICON done!! block_height: {self.block.block_height}', TBEARS_BLOCK_MANAGER)
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
        block_height: int = self.block.block_height + 1
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
        self.block.save_txresult(tx_hash, tx_result)

        # save block
        self.block.save_block(block_hash=block_hash, tx=self._conf['genesis'], timestamp=block_timestamp_us)

        # update block information
        self.block.commit_block(prev_block_hash=block_hash)

        Logger.debug(f'Initialize ICON done!! Load genesis block. block_height: {self.block.block_height}',
                     TBEARS_BLOCK_MANAGER)

    async def _init_periodic(self):
        """
        Initialize periodic task.
         - block confirmation
        :return:
        """
        Logger.debug(f'Initialize periodic task started!!', TBEARS_BLOCK_MANAGER)

        self.periodic = Periodic(func=self.process_block_data, interval=self._conf[ConfigKey.BLOCK_CONFIRM_INTERVAL])
        await self.periodic.start()

        Logger.debug(f'Initialize periodic task done!!', TBEARS_BLOCK_MANAGER)

    def close(self):
        Logger.debug(f'close {TBEARS_BLOCK_MANAGER}', TBEARS_BLOCK_MANAGER)
        get_event_loop().stop()

    def add_tx(self, tx_hash: str, tx: dict):
        """
        Add transactions to queue for block confirmation
        :param tx_hash: transaction hash
        :param tx: transaction
        :return:
        """
        tx_copy = deepcopy(tx)

        # add txHash
        tx_copy['txHash'] = tx_hash

        self._tx_queue.append(tx_copy)
        Logger.debug(f'Append tx to tx_queue: {self._tx_queue}', TBEARS_BLOCK_MANAGER)

    @property
    def tx_queue(self) -> list:
        """
        Get transaction queue
        :return:
        """
        return self._tx_queue

    def clear_tx(self) -> list:
        """
        return transaction queue and clear
        :return: transaction queue
        """
        tx_queue: list = self._tx_queue
        self._tx_queue = []

        return tx_queue

    @staticmethod
    def _generate_issue_tx(data: dict) -> dict:
        tx_timestamp = int(time.time() * 10 ** 6)
        hex(int(time.time() * 10 ** 6))
        issue_tx = {
            "version": hex(3),
            "nid": hex(1),
            "timestamp": hex(tx_timestamp),
            "dataType": "issue",
            "data": data,
            # txHash is not not official
            'txHash': create_hash(tx_timestamp.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER))
        }
        return issue_tx

    async def process_block_data(self):
        """
        Process block data. Invoke block and save transactions, transaction results and block. Update block height and previous block hash.
        :return:
        """
        Logger.debug(f'process_block_data started!!', TBEARS_BLOCK_MANAGER)

        # clear tx_queue
        tx_list = self.clear_tx()

        if len(tx_list) == 0:
            if self._conf[ConfigKey.BLOCK_CONFIRM_EMPTY]:
                Logger.debug(f'Confirm empty block', TBEARS_BLOCK_MANAGER)
            else:
                Logger.debug(f'There are no transactions for block confirm. Bye~', TBEARS_BLOCK_MANAGER)
                return

        # todo: 빈 블럭에도 이슈 tx 넣는걸로 수정
        if self._icon_is_issuable_version:
            issue_info = await self._icon_stub.async_task().get_issue_info()
            if not issue_info["prep"]["value"] == hex(0):
                issue_tx = self._generate_issue_tx(issue_info)
                tx_list.insert(0, issue_tx)
                Logger.debug(f'Create issue transaction:{issue_tx}', TBEARS_BLOCK_MANAGER)
            else:
                Logger.debug(
                    f'Do not create issue transaction as current icon service revision is not issuable version',
                    TBEARS_BLOCK_MANAGER)

        # make block hash. tbears block_manager is dev util
        block_timestamp_us = int(time.time() * 10 ** 6)
        block_hash = create_hash(block_timestamp_us.to_bytes(DEFAULT_BYTE_SIZE, DATA_BYTE_ORDER))

        # send invoke message to ICON
        response = await self._invoke_block(tx_list=tx_list, block_hash=block_hash, block_timestamp=block_timestamp_us)
        if response is None:
            Logger.debug(f'iconservice response None for invoke request.', TBEARS_BLOCK_MANAGER)
            return

        # send write precommit message and confirm block
        await self._confirm_block(tx_list=tx_list, tx_result=response, block_hash=block_hash,
                                  timestamp=block_timestamp_us)
        Logger.debug(f'process_block_data done!!', TBEARS_BLOCK_MANAGER)

    async def _invoke_block(self, tx_list: list, block_hash: str, block_timestamp) -> dict:
        """
        Invoke block. Send 'invoke' message to iconservice and get response
        :param tx_list: transaction list
        :param block_hash: block hash
        :param block_timestamp: block confirm timestamp
        :return:
        """
        Logger.debug(f'invoke block start', TBEARS_BLOCK_MANAGER)
        block_height = self.block.block_height + 1
        prev_block_hash = self.block.prev_block_hash

        transactions = []
        for tx in tx_list:
            transaction = {
                "method": 'icx_sendTransaction',
                "params": tx
            }
            transactions.append(transaction)

        request = {
            'block': {
                'blockHeight': hex(block_height),
                'blockHash': block_hash,
                'prevBlockHash': prev_block_hash,
                'timestamp': hex(block_timestamp)
            },
            'transactions': transactions,
        }
        if self._icon_is_issuable_version:
            prev_block_contributors = self._prep_manager.get_prev_block_contributors_info()
            request.update(prev_block_contributors)
            Logger.debug(f'Insert preBlockContributors in invoke requests: {prev_block_contributors}',
                         TBEARS_BLOCK_MANAGER)

        # send invoke message to iconservice
        response = await self._icon_stub.async_task().invoke(request)

        if 'error' in response:
            Logger.debug(f'Get error response from iconservice: {response}!!', TBEARS_BLOCK_MANAGER)
            return None

        Logger.debug(f'invoke block done. txResults: {response["txResults"]}!!', TBEARS_BLOCK_MANAGER)
        return response["txResults"]

    async def _confirm_block(self, tx_list: list, tx_result: dict, block_hash: str, timestamp: int):
        """
        Confirm block. Send 'write_precommit_state' message and save transaction, transaction result and block data
        :param tx_list: transaction list
        :param tx_result: transaction result
        :param block_hash: block hash
        :param timestamp: block timestamp
        :return:
        """
        Logger.debug(f'confirm block start!!', TBEARS_BLOCK_MANAGER)

        # save transaction result
        self.block.save_txresults(tx_list=tx_list, results=tx_result)

        # save transactions
        self.block.save_transactions(tx_list=tx_list, block_hash=block_hash)

        # save block
        self.block.save_block(block_hash=block_hash, tx=tx_list, timestamp=timestamp)

        # update block information
        self.block.commit_block(prev_block_hash=block_hash)

        block_height = self.block.block_height + 1
        precommit_request = {'blockHeight': hex(block_height),
                             'blockHash': block_hash}

        # send write_precommit_state message to iconservice
        await self._icon_stub.async_task().write_precommit_state(precommit_request)

        Logger.debug(f'confirm block done.', TBEARS_BLOCK_MANAGER)


def create_parser():
    """
    Create tbears_block_manager argument parser
    :return:
    """
    parser = argparse.ArgumentParser(prog=TBEARS_BLOCK_MANAGER,
                                     description=f'{TBEARS_BLOCK_MANAGER} v{get_tbears_version()} arguments')
    parser.add_argument('-ch', dest=ConfigKey.CHANNEL, help='Message Queue channel')
    parser.add_argument('-at', dest=ConfigKey.AMQP_TARGET, help='AMQP target info')
    parser.add_argument('-ak', dest=ConfigKey.AMQP_KEY,
                        help="Key sharing peer group using queue name. Use it if more than one peer connect to a single MQ")
    parser.add_argument('-bi', '--block-confirm-interval', dest=ConfigKey.BLOCK_CONFIRM_INTERVAL, type=int,
                        help='Block confirm interval in second')
    parser.add_argument('-be', '--block-confirm-empty', dest=ConfigKey.BLOCK_CONFIRM_EMPTY, type=bool,
                        help='Confirm empty block')
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
