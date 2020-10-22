import json
import os
import subprocess
import tarfile
from enum import IntEnum, unique, auto
from time import sleep
from typing import List, TYPE_CHECKING, Union

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import CallTransactionBuilder, DeployTransactionBuilder, TransactionBuilder
from iconsdk.exception import JSONRPCException
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.address import GOVERNANCE_ADDRESS, SYSTEM_ADDRESS
from iconservice.base.type_converter_templates import ConstantKeys
from iconservice.icon_constant import Revision

from tbears.config.tbears_config import TEST_ACCOUNTS, TEST1_PRIVATE_KEY
from tbears.util.arg_parser import uri_parser


DEBUG = 1
DIR_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_STEP_LIMIT = 1_000_000_000
DEFAULT_NID = 3
ICX = 10 ** 18


def debug_print(msg: str):
    if DEBUG:
        print(msg)


@unique
class SyncType(IntEnum):
    REVISION = 0
    GOVERNANCE_SCORE = auto()
    STEP_COST = auto()


sync_list = [
    {
        "type": SyncType.GOVERNANCE_SCORE,
        "params": {
            "version": "0.0.5"
        }
    },
    {
        "type": SyncType.GOVERNANCE_SCORE,
        "params": {
            "version": "0.0.6"
        }
    },
    {
        "type": SyncType.STEP_COST,
        "params": {
            "stepType": "apiCall",
            "cost": "0x2710"
        }
    },
    {
        "type": SyncType.REVISION,
        "params": {
            "code": "0x4",      # not errata
            "name": "1.2.3"
        }
    },
    {
        "type": SyncType.GOVERNANCE_SCORE,
        "params": {
            "version": "0.0.7"
        }
    },
    {
        "type": SyncType.REVISION,
        "params": {
            "code": "0x4",
            "name": "1.3.3"
        }
    },
    {
        "type": SyncType.REVISION,
        "params": {
            "code": "0x5",      # IISS prevote
            "name": "1.4.1"
        }
    },
    {
        "type": SyncType.REVISION,
        "params": {
            "code": "0x6",      # Decentralization
            "name": "1.5.15"
        }
    },
    {
        "type": SyncType.GOVERNANCE_SCORE,
        "params": {
            "version": "1.0.0"  # support network proposal
        }
    },
    {
        "type": SyncType.REVISION,
        "params": {
            "code": "0x8",
            "name": "1.5.20"
        }
    },
    {
        "type": SyncType.GOVERNANCE_SCORE,
        "params": {
            "version": "1.1.1"
        }
    },
    {
        "type": SyncType.REVISION,
        "params": {
            "code": "0x9",
            "name": "1.7.3"
        }
    },
    {
        "type": SyncType.REVISION,
        "params": {
            "code": "0xa",
            "name": "1.7.5"
        }
    },
    {
        "type": SyncType.REVISION,
        "params": {
            "code": "0xb",
            "name": "1.7.7"
        }
    },
]


class Sync:
    PREPS = TEST_ACCOUNTS[:4]

    def __init__(self):
        self.handlers = [
            self._set_revision,
            self._update_governance_score,
            self._set_step_cost,
        ]
        self.revision = 0
        self.gs_version = "0.0.0"

        self.key_wallet = KeyWallet.load(bytes.fromhex(TEST1_PRIVATE_KEY))
        self.preps = []
        for prep in self.PREPS:
            self.preps.append(KeyWallet.load(prep))
        uri, version = uri_parser("http://127.0.0.1:9000/api/v3")
        self.icon_service = IconService(HTTPProvider(uri, version))

    def apply(self):
        # get status
        response = self._get_revision()
        self.revision = int(response.get("code", "0x0"), 16)

        # start sync
        for i, action in enumerate(sync_list):
            print("")
            type_: int = action.get("type", -1)
            params = action.get("params", {})
            self.handlers[type_](params)

    @staticmethod
    def archive():
        root = "./"
        with tarfile.open('mainnet.tar.gz', 'w:gz') as tar:
            for dir in [".score", ".statedb"]:
                for _, _, files in os.walk(os.path.join(root, dir)):
                    for f in files:
                        tar.add(os.path.join(root, dir, f), arcname=f)

    def _is_network_proposal_enabled(self):
        return self.revision >= Revision.DECENTRALIZATION.value and self.gs_version >= "1.0.0"

    def _set_revision(self, params: dict):
        revision = int(params.get('code'), 16)
        print(f"## Set revision {revision}")
        if self.revision > revision:
            print(f"pass revision {revision}. {revision} < {self.revision}")
            return

        if not self._is_network_proposal_enabled():
            # send setRevision TX
            tx_hash = self._call_tx(key_wallet=self.key_wallet,
                                    to=GOVERNANCE_ADDRESS,
                                    method='setRevision',
                                    params=params)
            print(f"transaction hash: {tx_hash}")
        else:
            # register setRevision network proposal and approve it
            register = self.preps[0]
            np_id = self._register_proposal_tx(key_wallet=register,
                                               title=f"set revision {revision}",
                                               desc=f"T-Bears set revision {revision}",
                                               type=1,
                                               value_dict=params)
            for prep in self.preps:
                if prep == register:
                    continue
                tx_hash = self._vote_proposal_tx(key_wallet=prep,
                                                 id_=np_id,
                                                 vote=1)
                debug_print(f"{prep.get_address()} votes agree to {np_id}. transaction hash: {tx_hash}")

            print(f"Network proposal ID: {np_id}")

        self.revision = revision

        if self.revision == Revision.IISS.value:
            # make 4 P-Reps for network proposal
            self._make_preps(self.preps)

        if self.revision == Revision.DECENTRALIZATION.value:
            response = self._call(to=SYSTEM_ADDRESS, method="getIISSInfo")
            block_height = int(response.get("blockHeight"), 16)
            next_calc = int(response.get("nextCalculation"), 16)
            wait_time = (next_calc - block_height) * 2
            print(f"Wait decentralization..... {wait_time} secs")
            sleep(wait_time)
            while True:
                response = self._call(to=SYSTEM_ADDRESS, method="getIISSInfo")
                print(response.get("nextPRepTerm"))
                if response.get("nextPRepTerm", "0x0") != "0x0":
                    print(f"Decentralization is done.")
                    break
                else:
                    sleep(1)

    def _update_governance_score(self, params: dict):
        version = params.get('version')
        print(f"## Update governance SCORE to {version}")

        path = os.path.join(DIR_PATH, f"data/governance_{version}.zip")
        self._deploy_score(key_wallet=self.key_wallet,
                           score_address=GOVERNANCE_ADDRESS,
                           path=path)

        self.gs_version = version

    def _set_step_cost(self, params: dict):
        step_type = params.get('stepType')
        cost = params.get('cost')
        print(f"## Set stepCost.{step_type} to {cost}")
        if not self._is_network_proposal_enabled():
            # send setStepCost TX
            tx_hash = self._call_tx(key_wallet=self.key_wallet,
                                    to=GOVERNANCE_ADDRESS,
                                    method='setStepCost',
                                    params=params)
            print(f"transaction hash: {tx_hash}")
        else:
            # TODO send setStepCost network proposal and approve it
            print(f"Network proposal : ID")

    def _deploy_score(
            self,
            key_wallet: 'KeyWallet',
            path: str,
            score_address: str = SYSTEM_ADDRESS,
    ) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(key_wallet.get_address()) \
            .to(score_address) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(path)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, key_wallet)

        # send transaction
        return self.icon_service.send_transaction(signed_transaction)

    def _call(self,
              to: str,
              method: str,
              params: dict = {}) -> Union[dict, str]:
        call = CallBuilder() \
            .from_(self.key_wallet.get_address()) \
            .to(to) \
            .method(method) \
            .params(params) \
            .build()

        return self.icon_service.call(call)

    def _tx(self,
            key_wallet: 'KeyWallet',
            to: str,
            value: int = 0,
            step_limit: int = DEFAULT_STEP_LIMIT,
            nid: int = DEFAULT_NID,
            nonce: int = 0) -> str:
        transaction = TransactionBuilder() \
            .from_(key_wallet.get_address()) \
            .to(to) \
            .value(value) \
            .step_limit(step_limit) \
            .nid(nid) \
            .nonce(nonce) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, key_wallet)

        # Send transaction
        return self.icon_service.send_transaction(signed_transaction)

    def _call_tx(self,
                 key_wallet: 'KeyWallet',
                 to: str,
                 method: str,
                 params: dict = {},
                 value: int = 0,
                 step_limit: int = DEFAULT_STEP_LIMIT,
                 nid: int = DEFAULT_NID,
                 nonce: int = 0) -> str:
        transaction = CallTransactionBuilder() \
            .from_(key_wallet.get_address()) \
            .to(to) \
            .value(value) \
            .step_limit(step_limit) \
            .nid(nid) \
            .nonce(nonce) \
            .method(method) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, key_wallet)

        # Send transaction
        return self.icon_service.send_transaction(signed_transaction)

    def _get_revision(self) -> dict:
        try:
            return self._call(to=GOVERNANCE_ADDRESS, method="getRevision")
        except JSONRPCException:
            return {"code": "0x0", "name": "0.0.0"}

    def _register_proposal_tx(self,
                              key_wallet: 'KeyWallet',
                              title: str,
                              desc: str,
                              type: int,
                              value_dict: dict,
                              value: int = 0,
                              step_limit: int = DEFAULT_STEP_LIMIT,
                              nid: int = DEFAULT_NID,
                              nonce: int = 0) -> str:
        params = {
            "title": title,
            "description": desc,
            "type": hex(type),
            "value": "0x" + bytes.hex(json.dumps(value_dict).encode())
        }
        return self._call_tx(key_wallet=key_wallet,
                             to=GOVERNANCE_ADDRESS,
                             method="registerProposal",
                             params=params,
                             value=value,
                             step_limit=step_limit,
                             nid=nid,
                             nonce=nonce)

    def _vote_proposal_tx(self,
                          key_wallet: 'KeyWallet',
                          id_: str,
                          vote: int,
                          value: int = 0,
                          step_limit: int = DEFAULT_STEP_LIMIT,
                          nid: int = DEFAULT_NID,
                          nonce: int = 0) -> 'str':
        params = {
            "id": id_,
            "vote": hex(vote)
        }

        return self._call_tx(key_wallet=key_wallet,
                             to=GOVERNANCE_ADDRESS,
                             method="voteProposal",
                             params=params,
                             value=value,
                             step_limit=step_limit,
                             nid=nid,
                             nonce=nonce)

    def _make_preps(self, preps: List[KeyWallet]):
        print(f"#### make P-Reps")
        delegate_value = self.icon_service.get_total_supply() * 2 // 1000
        transfer_value = delegate_value + 3000 * ICX
        for prep in preps:
            # transfer ICX
            tx_hash = self._tx(key_wallet=self.key_wallet,
                               to=prep.get_address(),
                               value=transfer_value)
            debug_print(f"transfer {transfer_value} to {prep.get_address()} tx_hash: {tx_hash}")
        while True:
            sleep(1)
            balance = self.icon_service.get_balance(preps[0].get_address())
            if balance >= transfer_value:
                break

        for prep in preps:
            # register P-Rep
            name = f"node{prep.get_address()}"
            params = {
                ConstantKeys.NAME: name,
                ConstantKeys.COUNTRY: "KOR",
                ConstantKeys.CITY: "Unknown",
                ConstantKeys.EMAIL: f"{name}@example.com",
                ConstantKeys.WEBSITE: f"https://{name}.example.com",
                ConstantKeys.DETAILS: f"https://{name}.example.com/details",
                ConstantKeys.P2P_ENDPOINT: f"{name}.example.com:7100",
            }
            tx_hash = self._call_tx(key_wallet=prep,
                                    to=SYSTEM_ADDRESS,
                                    value=2000 * ICX,
                                    method="registerPRep",
                                    params=params)
            debug_print(f"register {prep.get_address()} tx_hash: {tx_hash}")

            # stake
            tx_hash = self._call_tx(key_wallet=prep,
                                    to=SYSTEM_ADDRESS,
                                    method="setStake",
                                    params={"value": hex(delegate_value)})
            debug_print(f"set stake {prep.get_address()} tx_hash: {tx_hash}")
            # delegate
            tx_hash = self._call_tx(key_wallet=prep,
                                    to=SYSTEM_ADDRESS,
                                    method="setDelegation",
                                    params={
                                        "delegations": [
                                            {
                                                "address": prep.get_address(),
                                                "value": hex(delegate_value)
                                            }
                                        ]
                                    })
            debug_print(f"delegate {prep.get_address()} tx_hash: {tx_hash}")

        while True:
            sleep(1)
            response = self._call(to=SYSTEM_ADDRESS, method="getPReps")
            if len(response.get("preps", 0)) > 0:
                print(f"make 4 P-Reps")
                for prep in preps:
                    address = prep.get_address()
                    resp = self._call(to=SYSTEM_ADDRESS,
                                      method="getPRep",
                                      params={"address": address})
                    print(f" - {address}, delegated: {int(resp.get('delegated'), 16)//ICX:,} ICX")
                print(self._call(to=SYSTEM_ADDRESS, method="getIISSInfo"))
                break

    def check_revision(self) -> int:
        current_revision = int(self._get_revision().get("code"), 16)
        latest_revision = self._get_latest_revision()

        return current_revision - latest_revision


    @staticmethod
    def _get_latest_revision() -> int:
        for cmd in reversed(sync_list):
            if cmd.get("type") == SyncType.REVISION:
                return int(cmd["params"]["code"], 16)
        return 0


if __name__ == '__main__':
    subprocess.run(['tbears', 'stop'], stdout=subprocess.DEVNULL)
    subprocess.run(['tbears', 'clear'], stdout=subprocess.DEVNULL)
    subprocess.run(['tbears', 'start'], stdout=subprocess.DEVNULL)

    syncer = Sync()
    syncer.apply()

    subprocess.run(['tbears', 'stop'], stdout=subprocess.DEVNULL)
    subprocess.run(['tar', 'czvf', '../../../tbears/data/mainnet.tar.gz', '.score/', '.statedb/'], stdout=subprocess.DEVNULL)
