# Copyright 2019 ICON Foundation
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
from iconservice.utils.hashing.hash_generator import HashGenerator, RootHashGenerator

TRANSACTION_HASH_SALT = "icx_sendTransaction"


def generate_hash(data: list, salt: str = TRANSACTION_HASH_SALT):
    if not data:
        return "0" * 64
    HashGenerator._SALT = salt
    values = []
    for elem in data:
        if isinstance(elem, dict):
            value = HashGenerator.generate_hash(elem).encode()
        elif elem is None:
            continue
        else:
            value = elem
        values.append(value)
    return RootHashGenerator.generate_root_hash(values, True).hex()
