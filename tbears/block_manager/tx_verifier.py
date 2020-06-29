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

import hashlib

from iconcommons import Logger
from coincurve import PublicKey


def address_from_pubkey(pubkey: bytes):
    hash_pub = hashlib.sha3_256(pubkey[1:]).hexdigest()
    return f"hx{hash_pub[-40:]}"


def verify_signature(msg_hash: bytes, signature: bytes, sender: str) -> bool:
    if isinstance(msg_hash, bytes) \
            and len(msg_hash) == 32 \
            and isinstance(signature, bytes) \
            and len(signature) == 65:

        public_key = PublicKey.from_signature_and_message(
            serialized_sig=signature,
            message=msg_hash,
            hasher=None
        )

        address: str = address_from_pubkey(public_key.format(compressed=False))
        if address == sender:
            return True

        Logger.info(f'Expected address={sender}', "verify_signature")
        Logger.info(f'Signed address={address}', "verify_signature")

    return False
