# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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

from iconservice.base.address import Address
from iconservice.base.exception import DatabaseException
from iconservice.database.db import KeyValueDatabase, _is_db_writable_on_context

value_type = (int, str, bytes, bool, Address, None)


class MockKeyValueDatabase(KeyValueDatabase):
    """Plyvel database wrapper
    """

    @staticmethod
    def create_db() -> 'MockPlyvelDB':
        db = MockPlyvelDB(MockPlyvelDB.make_db())
        return db


class MockPlyvelDB(object):
    """Plyvel database wrapper
    """

    @staticmethod
    def make_db() -> dict:
        return dict()

    def __init__(self, db: dict) -> None:
        self._db = db

    def get(self, context, bytes_key: bytes) -> value_type:
        return self._db.get(bytes_key)

    def put(self, context, bytes_key: bytes, value: value_type) -> None:

        if not _is_db_writable_on_context(context):
            raise DatabaseException('put is not allowed')

        self._db[bytes_key] = value

    def delete(self, context, bytes_key: bytes) -> None:
        if not _is_db_writable_on_context(context):
            raise DatabaseException('delete is not allowed')

        if bytes_key in self._db:
            del self._db[bytes_key]

    def close(self) -> None:
        pass

    def get_sub_db(self, key: bytes):
        return MockPlyvelDB(self.make_db())

    def iterator(self) -> iter:
        return iter(self._db)

    def prefixed_db(self, bytes_prefix) -> 'MockPlyvelDB':
        return MockPlyvelDB(MockPlyvelDB.make_db())
