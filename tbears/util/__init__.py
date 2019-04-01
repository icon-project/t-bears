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
import os
import re
import hashlib

import pkg_resources

from ..tbears_exception import TBearsWriteFileException


DIR_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_PATH = os.path.abspath(os.path.join(DIR_PATH, '..', '..'))


def write_file(parent_directory: str, file_name: str, contents: str, overwrite: bool = False) -> None:
    """Create file with the contents in the parents directory.

    :param parent_directory: Location to create the file.
    :param file_name: File name
    :param contents: Contents of file.
    """
    try:
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)
        if os.path.exists(f'{parent_directory}/{file_name}') and not overwrite:
            return
        with open(f'{parent_directory}/{file_name}', mode='w') as file:
            file.write(contents)
    except (PermissionError, IsADirectoryError) as e:
        raise TBearsWriteFileException(f"Can't write file {parent_directory}/{file_name}. {e}")


def get_score_template(score_project: str, score_class: str) -> tuple:
    """
    :param score_project: Your project name.
    :param score_class: Your score class name.
    :return:
    """
    main_py = """from iconservice import *

TAG = 'SampleScore'

class SampleScore(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()
    
    @external(readonly=True)
    def hello(self) -> str:
        Logger.debug(f'Hello, world!', TAG)
        return "Hello"
"""

    test_py = """import os

from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestSampleScore(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT= os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
        self._score_address = self._deploy_score()['scoreAddress']

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \\
            .from_(self._test1.get_address()) \\
            .to(to) \\
            .step_limit(100_000_000_000) \\
            .nid(3) \\
            .nonce(100) \\
            .content_type("application/zip") \\
            .content(gen_deploy_data_content(self.SCORE_PROJECT)) \\
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def test_score_update(self):
        # update SCORE
        tx_result = self._deploy_score(self._score_address)

        self.assertEqual(self._score_address, tx_result['scoreAddress'])

    def test_call_hello(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \\
            .to(self._score_address) \\
            .method("hello") \\
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)

        self.assertEqual("Hello", response)
"""
    test_unit_py = """from ..sample_score import SampleScore
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestSampleScore(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(SampleScore, self.test_account1)

    def test_hello(self):
        self.assertEqual(self.score.hello(), "Hello")
"""
    return main_py.replace("SampleScore", score_class), test_py.replace("SampleScore", score_class), test_unit_py.\
        replace("sample_score", score_project).replace("SampleScore", score_class)


def get_package_json_dict(project: str, score_class: str) -> dict:
    """Returns the template of package.json

    :param project: SCORE's name.
    :param score_class: SCORE's main class name.

    :return: package.json's contents.(dict)
    """
    package_json_dict = {
        "version": "0.0.1",
        "main_module": f"{project}",
        "main_score": f"{score_class}"
    }
    return package_json_dict


def is_lowercase_hex_string(value: str) -> bool:
    """Check whether value is hexadecimal format or not

    :param value: text
    :return: True(lowercase hexadecimal) otherwise False
    """
    try:
        result = re.match('[0-9a-f]+', value)
        return len(result.group(0)) == len(value)
    except:
        pass

    return False


def create_hash(data: bytes) -> str:
    return f'{hashlib.sha3_256(data).hexdigest()}'


def is_valid_hash(_hash: str) -> bool:
    """Check hash is valid.

    :param _hash:
    :return:
    """
    if isinstance(_hash, str) and len(_hash) == 66:
        prefix, body = _hash[:2], _hash[2:]
        return prefix == '0x' and is_lowercase_hex_string(body)

    return False


def get_tbears_version() -> str:
    """Get version of tbears.
    The location of the file that holds the version information is different when packaging and when executing.
    :return: version of tbears.
    """
    try:
        version = pkg_resources.get_distribution('tbears').version
    except pkg_resources.DistributionNotFound:
        version_path = os.path.join(PROJECT_ROOT_PATH, 'VERSION')
        with open(version_path, mode='r') as version_file:
            version = version_file.read()
    except:
        version = 'unknown'
    return version


def jsonrpc_params_to_pep_style(params: dict):
    change_dict_key_name(params, 'from', 'from_')
    change_dict_key_name(params, 'stepLimit', 'step_limit')
    change_dict_key_name(params, 'dataType', 'data_type')


def change_dict_key_name(params: dict, origin_name: str, new_name: str):
    if origin_name in params:
        params[new_name] = params.pop(origin_name)
