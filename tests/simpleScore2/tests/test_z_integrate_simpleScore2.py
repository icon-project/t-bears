import json
import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, CallTransactionBuilder
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

# We put simpleScore test-cases to test SCORE test framework work properly.
# Prefix 'z' is included to run this test file later than test_unit_simpleScore2 test.
# (Since some functions are patched in SCORE unittest, to make sure that they are properly restored)


class TestTest(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SIMPLE_SCORE_PATH = os.path.abspath(os.path.join(DIR_PATH, "..", "..", "simpleScore"))
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
        self._score_address1 = self._deploy_score(score_path=self.SIMPLE_SCORE_PATH)['scoreAddress']
        self._score_address = self._deploy_score(params={"score_address": self._score_address1},
                                                 score_path=self.SCORE_PROJECT)['scoreAddress']

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS, params: dict = {}, score_path: str = "") -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder().from_(self._test1.get_address()).to(to).step_limit(
            100_000_000_000).nid(3).nonce(100).content_type("application/zip").params(params).content(
            gen_deploy_data_content(score_path)).build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertEqual(True, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def test_call_hello(self):
        call = CallBuilder().from_(self._test1.get_address()).to(self._score_address).method("getSCOREValue").build()
        response = self.process_call(call, self.icon_service)
        self.assertEqual(response, "")

        new_value = "new_value"
        call_tx = CallTransactionBuilder().from_(self._test1.get_address()).to(self._score_address).\
            method("setSCOREValue").params({"value": new_value}).step_limit(10000000).build()
        signed_tx = SignedTransaction(call_tx, self._test1)
        tx_result = self.process_transaction(signed_tx, self.icon_service)
        self.assertTrue(tx_result['status'])

        call = CallBuilder().from_(self._test1.get_address()).to(self._score_address).method("getSCOREValue").build()
        response = self.process_call(call, self.icon_service)
        self.assertEqual(new_value, response)

        call = CallBuilder().from_(self._test1.get_address()).to(self._score_address).method("get_owner").build()
        response = self.process_call(call, self.icon_service)
        self.assertEqual(self._test1.get_address(), response)

        call = CallBuilder().from_(self._test1.get_address()).to(self._score_address).method("get_balance").\
            params({"address": self._test1.get_address()}).build()
        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(10**24), response)

        call = CallBuilder().from_(self._test1.get_address()).to(self._score_address).method("simple_json_dumps")\
            .build()
        response = self.process_call(call, self.icon_service)
        expected = json.dumps({"simple": "value"})
        self.assertEqual(expected, response)
