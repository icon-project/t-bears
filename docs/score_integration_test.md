# ICON SCORE integration test

## Overview
Provide simple explanations for ICON SCORE integration test.

## How to Run the SCORE test
```bash
# with T-Bears command
$ tbears test <score_project_path>

# with python
$ python -m unittest discover <score_project_path>
```

## SCORE project File organization

| **Item**                   | **Description**                          |
| :------------------------- | :----------------------------------------------------------- |
|\<project>                 | SCORE project name. Project directory is created with the same name. |
|\<project>/\_\_init\_\_.py | \_\_init\_\_.py file to make the project directory recognized as a python package. |
|\<project>/package.json    | Contains the information needed when SCORE is loaded. <br> "main_module" and "main_class" should be specified. |
|\<project>/<project>.py    | SCORE main file.                  |
|\<project>/tests           | Directory for SCORE test code.                              |
|\<project>/tests/\_\_init\_\_.py | \_\_init\_\_.py file to make the test directory recognized as a python package. |
|\<project>/tests/test\_integrate\_\<project>.py    | SCORE integrate test file.  |
|\<project>/tests/test\_unit\_\<project>.py    | SCORE unit test file.  |

* When T-Bears deploys SCORE, the `tests` directory is not included.

## How to write SCORE integration test code

The SCORE integration test code works as follows

1. Deploy SCORE to be tested
2. Create a ICON JSON-RPC API request for the SCORE API you want to test
3. If neccessary, sign a ICON JSON-RPC API request
4. Invoke a ICON JSON-RPC API request and get the result
5. Check the result

### Packages and modules

#### ICON python SDK
You can create and sign a ICON JSON-RPC API request using the ICON python SDK

```python
# create key wallet
self._test = KeyWallet.create()

# Generates an instance of transaction for deploying SCORE.
transaction = DeployTransactionBuilder() \
    .from_(self._test.get_address()) \
    .to(to) \
    .step_limit(100_000_000_000) \
    .nid(3) \
    .nonce(100) \
    .content_type("application/zip") \
    .content(gen_deploy_data_content(self.SCORE_PROJECT)) \
    .build()

# Returns the signed transaction object having a signature
signed_transaction = SignedTransaction(transaction, self._test)
```



#### IconIntegrateTestBase in T-Bears

Every SCORE integration test class must inherit `IconIntegrateTestBase`.

IconIntegrateTestBase class provides three functions

1. Support python unittest

   1. You can write and run the test method with prefix 'test_'
   2. You can initalize and finalize the test by override setUp and tearDown method

2. Emulate ICON service for test

   1. Initialize ICON service and confirm genesis block
   2. Create accounts for test
      1. self._test1 : Account with 1,000,000 ICX
      2. self._wallet_array[] : 10 empty accounts in list

3. Provide API for SCORE integration test

   1. process_transaction()

      Invoke transaction and return transaction result

   2. process_call()

      Calls SCORE's external function which is read-only and return result

### examples

You can get source code with `tbears init score_test ScoreTest` command.

#### score_test.py

```python
from iconservice import *

TAG = 'ScoreTest'

class ScoreTest(IconScoreBase):

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
```

#### score_tests/test_score_test.py

```python
import os

from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestScoreTest(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT= os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        # Initialize IconIntegrateTestBase
        super().setUp()

        self.icon_service = None
        # If you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # 1. deploy SCORE
        self._score_address = self._deploy_score()['scoreAddress']

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(self.SCORE_PROJECT)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        tx_result = self._process_transaction(signed_transaction)

        # check transaction result
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def test_score_update(self):
        # update SCORE
        tx_result = self._deploy_score(self._score_address)

        self.assertEqual(self._score_address, tx_result['scoreAddress'])

    def test_call_hello(self):
        # 2. Create a ICON JSON-RPC API call reques
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("hello") \
            .build()

        # 3. If neccessary, sign a ICON JSON-RPC API request
        # call request needs no signing

        # 4. Invoke a ICON JSON-RPC API request and get the result
        response = self._process_call(call, self.icon_service)

        # 5. check the call result
        self.assertEqual("Hello", response)
```

#### Run test code

```bash
$ tbears test score_test
..
----------------------------------------------------------------------
Ran 2 tests in 0.172s

OK
```



## References

* [ICON python SDK] (https://repo.theloop.co.kr/icon/icon-sdk/icon-sdk-python)
* [ICON SCORE samples] (https://github.com/icon-project/samples)

