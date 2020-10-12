from iconservice import Address
from iconservice.base.exception import DatabaseException

from tbears.libs.scoretest.score_test_case import ScoreTestCase
from ..simpleScore2 import SimpleScore2


class TestSimple(ScoreTestCase):
    def setUp(self):
        super().setUp()
        self.mock_score_address = Address.from_string(f"cx{'1234' * 10}")
        self.score2 = self.get_score_instance(SimpleScore2, self.test_account1,
                                              on_install_params={'score_address': self.mock_score_address})

        self.test_account3 = Address.from_string(f"hx{'12345' * 8}")
        self.test_account4 = Address.from_string(f"hx{'1234' * 10}")
        account_info = {
            self.test_account3: 10 ** 21,
            self.test_account4: 10 ** 21}
        self.initialize_accounts(account_info)

    def test_set_value(self):
        str_value = 'string_value'
        self.score2.setValue(str_value)
        # assert event log called with specified arguments
        self.score2.SetValue.assert_called_with(str_value)

        self.assertEqual(self.score2.getValue(), str_value)

    def test_get_value_and_set_value(self):
        # at first, value is empty string
        self.assertEqual(self.score2.getValue(), '')

        str_value = 'strValue'
        self.score2.setValue(str_value)

        self.assertEqual(self.score2.getValue(), str_value)

    def test_array(self):
        self.assertEqual(0, self.score2.arrayLength())
        for v in range(10):
            self.score2.appendValue(v)
        self.assertEqual(10, self.score2.arrayLength())
        self.assertEqual(sum(range(10)), self.score2.arraySum())

        self.score2.arraySetItem(3, 45)
        self.assertEqual(45, self.score2.arrayGetItem(3))

    def test_dict(self):
        for v in range(10):
            self.score2.dictSetItem(v, v+10)

        for v in range(10):
            self.assertTrue(self.score2.dictContains(v))
            self.assertEqual(v+10, self.score2.dictGetItem(v))

    # try writing value inside readonly method
    def test_write_on_readonly(self):
        self.assertRaises(DatabaseException, self.score2.write_on_readonly)

    # internal call
    def test_internal_call(self):
        self.patch_internal_method(self.mock_score_address, 'getValue',
                                   lambda: 150)  # Patch the getValue function of SCORE at self.mock_score_address address with a function that takes no argument and returns 150
        value = self.score2.getSCOREValue()
        self.assertEqual(value, 150)
        self.assert_internal_call(self.mock_score_address,
                                  'getValue')  # assert getValue in self.mock_score_address is called.

        self.score2.setSCOREValue('asdf')
        self.assert_internal_call(self.mock_score_address, 'setValue',
                                  'asdf')  # assert setValue in self.mock_score_address is called with 'asdf'

    # internal call
    def test_internal_call2(self):
        # To determine whether a method is called properly with specified arguments, calling register_interface_score method is enough
        self.register_interface_score(self.mock_score_address)
        self.score2.setSCOREValue('asdf')
        self.assert_internal_call(self.mock_score_address, 'setValue', 'asdf')

    # internal call
    def test_internal_call3(self):
        self.patch_call(self.score2, lambda score, method, args={}, amount=0: 150)
        # Patch the score2.call() to return 150
        value = self.score2.getSCOREValue2()
        self.assertEqual(value, 150)
        self.score2.call.assert_called_with(self.mock_score_address, "getValue", {}) # assert getValue in self.mock_score_address is called

    def test_msg(self):
        self.set_msg(Address.from_string(f"hx{'1234' * 10}"), 3)
        self.score2.t_msg()  # On the upper line, set the msg property to pass the assert statement so that no exception is raised.

        self.set_msg(Address.from_string(f"hx{'12' * 20}"), 3)
        self.assertRaises(AssertionError,
                          self.score2.t_msg)  # On the upper line, set the msg property not to pass the assert statement, and raise an exception.

    def test_tx(self):
        self.set_tx(Address.from_string(f"hx{'1234' * 10}"))
        self.score2.t_tx()  # On the upper line, set the tx property to pass the assert statement so that no exception is raised.

        self.set_tx(Address.from_string(f"hx{'12' * 20}"))
        self.assertRaises(AssertionError,
                          self.score2.t_tx)  # On the upper line, set the tx property not to pass the assert statement, and raise an exception.

    def test_block(self):
        self.set_block(3, 30)
        self.score2.t_block()  # On the upper line, set the block property to pass the assert statement so that no exception is raised.

        self.set_block(3)
        self.assertRaises(AssertionError,
                          self.score2.t_block)  # On the upper line, set the block property not to pass the assert statement, and raise an exception.

    def test_update(self):
        self.score2 = self.update_score(self.score2.address, SimpleScore2, on_update_params={"value": "updated_value"})
        self.assertEqual(self.score2.value.get(),
                         "updated_value")  # In the on_update method of SimpleScore2, set the value of the value to "updated_value".

    def test_get_balance(self):
        balance = self.get_balance(self.test_account3)
        self.assertEqual(balance, 10 ** 21)

    def test_get_balance2(self):
        balance = self.score2.get_balance(self.test_account3)
        self.assertEqual(balance, 10 ** 21)

    def test_transfer(self):
        # before calling transfer method, check balance of test_account3 and test_account4
        amount = 10 ** 21
        balance_3 = self.get_balance(self.test_account3)
        self.assertEqual(balance_3, amount)
        balance_4 = self.get_balance(self.test_account4)
        self.assertEqual(balance_4, amount)

        self.transfer(self.test_account3, self.test_account4, amount)
        # after calling transfer method, check balance of test_account3 and test_account4
        balance_3 = self.get_balance(self.test_account3)
        self.assertEqual(balance_3, 0)
        balance_4 = self.get_balance(self.test_account4)
        self.assertEqual(balance_4, amount * 2)

    def test_transfer2(self):
        # before calling transfer method, check balance of test_account3 and test_account4
        amount = 10 ** 21
        balance_3 = self.get_balance(self.test_account3)
        self.assertEqual(balance_3, amount)
        balance_4 = self.get_balance(self.test_account4)
        self.assertEqual(balance_4, amount)

        self.set_msg(self.test_account3)
        self.score2.transfer(self.test_account4, amount)
        # after calling transfer method, check balance of test_account3 and test_account4
        balance_3 = self.get_balance(self.test_account3)
        self.assertEqual(balance_3, 0)
        balance_4 = self.get_balance(self.test_account4)
        self.assertEqual(balance_4, amount * 2)

    def test_call(self):
        self.score2.call(self.mock_score_address, "asdf", {})

    def test_owner(self):
        self.assertEqual(self.score2.owner, self.test_account1)

    def test_send(self):
        self.set_msg(self.test_account1, 123123)
        self.score2.send(self.test_account3)

    def test_put_on_general_method(self):
        self.score2._setValue('value')
        self.assertEqual(self.score2.getValue(), 'value')
        self.score2._setValue('value2')
        self.assertEqual(self.score2.getValue(), 'value2')

    def test_general_method(self):
        # test for context properly set after readonly method called
        self.score2.setValue("value")
        self.score2.general_method()
        self.assertEqual("value"*2, self.score2.getValue())

    def test_payable(self):
        score2_balance = self.get_balance(self.score2.address)
        self.assertEqual(score2_balance, 0)
        donation_value = 10**20
        self.set_msg(self.test_account3, donation_value)
        self.score2.donate()
        score2_balance = self.get_balance(self.score2.address)
        self.assertEqual(score2_balance, donation_value)

    def test_call_payable_in_none_payable(self):
        score2_balance = self.get_balance(self.score2.address)
        self.assertEqual(score2_balance, 0)
        donation_value = 10**20

        self.set_msg(self.test_account3, donation_value)
        self.score2.call_donate()
        score2_balance = self.get_balance(self.score2.address)
        self.assertEqual(score2_balance, 0)

        self.score2.call_donate_external()
        score2_balance = self.get_balance(self.score2.address)
        self.assertEqual(score2_balance, 0)

        self.score2.call_donate_readonly()
        score2_balance = self.get_balance(self.score2.address)
        self.assertEqual(score2_balance, 0)

        self.score2.call_donate_payable()
        score2_balance = self.get_balance(self.score2.address)
        self.assertEqual(score2_balance, donation_value)
