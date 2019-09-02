# -*- coding: utf-8 -*-

# Copyright 2019 ICON Foundation
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
import unittest
from typing import Optional

from iconservice.base.block import Block
from iconservice.icon_service_engine import IconServiceEngine

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, create_block_hash, create_timestamp


class TestScoreTestCommand(unittest.TestCase):
    # since supporting new block hash, commit and rollback method in icon service engine has changed.
    # so tests about compatibility.
    def test_instant_block_hash_compatibility(self):
        # success case: when icon service version is under 1.3.0 (these versions only get instant block hash)

        # define mocked commit method
        def prev_commit(obj, block: 'Block'):
            assert isinstance(obj, IconServiceEngine)
            assert isinstance(block, Block)
        IconServiceEngine.commit = prev_commit

        icon_integrate_test_base = IconIntegrateTestBase()
        icon_integrate_test_base.setUpClass()
        icon_integrate_test_base.setUp()

        instant_block = Block(block_height=1,
                              block_hash=create_block_hash(),
                              timestamp=create_timestamp(),
                              prev_hash=create_block_hash(),
                              cumulative_fee=0)
        icon_integrate_test_base._write_precommit_state(instant_block)
        icon_integrate_test_base.tearDown()

        # success case: when icon service version is 1.3.0 and more
        # (these versions get instant block hash and new block hash)

        # define mocked commit method
        def new_commit(obj, block_height: int, instant_block_hash: bytes, block_hash: Optional[bytes]):
            assert isinstance(obj, IconServiceEngine)
            assert isinstance(block_height, int)
            assert isinstance(instant_block_hash, bytes)
            assert isinstance(block_hash, bytes)

        IconServiceEngine.commit = new_commit
        icon_integrate_test_base = IconIntegrateTestBase()
        icon_integrate_test_base.setUpClass()
        icon_integrate_test_base.setUp()

        instant_block = Block(block_height=1,
                              block_hash=create_block_hash(),
                              timestamp=create_timestamp(),
                              prev_hash=create_block_hash(),
                              cumulative_fee=0)
        icon_integrate_test_base._write_precommit_state(instant_block)
        icon_integrate_test_base.tearDown()
