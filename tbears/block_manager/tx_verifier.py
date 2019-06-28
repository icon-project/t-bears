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
from secp256k1 import PublicKey, ALL_FLAGS

_public_key = PublicKey(flags=ALL_FLAGS)


def address_from_pubkey(pubkey: bytes):
    hash_pub = hashlib.sha3_256(pubkey[1:]).hexdigest()
    return f"hx{hash_pub[-40:]}"


def verify_signature(msg_hash: bytes, signature: bytes, sender: str) -> bool:
    if isinstance(msg_hash, bytes) \
            and len(msg_hash) == 32 \
            and isinstance(signature, bytes) \
            and len(signature) == 65:

        origin_sig, rec_id = signature[:-1], signature[-1]
        recoverable_sig = _public_key.ecdsa_recoverable_deserialize(origin_sig, rec_id)
        internal_pubkey = _public_key.ecdsa_recover(msg_hash,
                                                    recoverable_sig,
                                                    raw=True, digest=None)
        public_key = PublicKey(internal_pubkey,
                               raw=False,
                               ctx=_public_key.ctx).serialize(compressed=False)

        address: str = address_from_pubkey(public_key)
        Logger.info(f'Expected address={sender}', "verify_signature")
        Logger.info(f'Signed address={address}', "verify_signature")
        if address == sender:
            return True

    return False
