# ICON SCORE unit test

## Overview
Provide simple explanations for ICON SCORE unit test.

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

## How to write SCORE unit test code

SCORE unittest should inherit `ScoreTestCase`. The SCORE unit test code works as follows

- get SCORE instance to be tested
- Call SCORE method
- Check the result

## Functions provided by ScoreTestCase

- Instantiate SCORE
  - Instantiate SCORE. So,  you can access attributes and methods of SCORE like a general object.
- Set  `property` in SCORE
  - Provide the ability to set properties used inside SCORE methods.
- Mock state DB
  - Store changed state due to SCORE method invocation. State stored in memory, not in file system.
- Mock event log
  - It is sufficient to check that the event log has been called
- Mock internalCall(call external function in SCORE).
  - The operation on the other SCORE is considered to be reliable. so, what you need is InternalCall called with specified arguments.

### methods

ScoreTestCase has 11 main methods. Inside setUp method and tearDown method, ScoreTestCase sets environment for SCORE unit-test and clear them.
So, if you want to override setUp or tearDown, you should call `super()` top of the overriden method.

- Getting SCORE instance
  - get_score_instance(score_class, owner, on_install_params)<br>
    - Get an instance of the SCORE class passed as an `score_class` argument<br>
    - **parameters**
      - **score_class** : SCORE  to instantiate
      - **owner** : Address to set as owner of SCORE
      - **on_install_params** : parameters of on_install_method
    - Refer `setUp` method in [example](#simple_score2/tests/test_unit_simple_score2.py)
  - update_score(prev_score_address, score_class, on_update_params)<br>
    - Update SCORE at `prev_score_address` with `score_class` instance and get updated SCORE<br>
    - **parameters**
      - **Prev_score_address** : address of SCORE to update
      - **score_class** : SCORE class to update
      - **on_update_params** : parameters of on_update method
    - Refer `test_update` method in [example](#simple_score2/tests/test_unit_simple_score2.py)

- Setting SCORE's properties
  - set_msg(sender, value)<br>
    - Set msg property in SCORE<br>
    - **parameters**
      - **sender** : Set sender attribute of msg to given sender argument
      - **value** : Set value attribute of msg to given sender argument
    - Refer `test_msg` method in [example](#simple_score2/tests/test_unit_simple_score2.py)
  - set_tx(origin, timestamp, _hash, index, nonce)<br>
    - Set tx property in SCORE<br>
    - **parameters**
      - **origin** : Set origin attribute of tx to given origin argument
      - **timestamp** : Set timestamp attribute of tx to given timestamp argument
      - **_hash** : Set hash attribute of tx to given _hash argument
      - **index** : Set index attribute of tx to given index argument
      - **nonce** : Set nonce attribute of tx to given nonce argument
    - Refer `test_tx` method in [example](#simple_score2/tests/test_unit_simple_score2.py)
  - set_block(height, timestamp)<br>
    - Set the block property inside SCORE.
      If you pass only height, the value of block.timestamp is set to height * 2 seconds.<br>
      When this method is called, the block_height inside the SCORE associated with the block is set to height, and the return value of the now () method is set to timestamp.<br>
      It should be called if you use the value associated with the block information in the SCORE method you are calling.<br>
    - **parameters**
      - **height** : Set height attribute of block to given height argument
      - **timestamp** : Set timestamp attribute of block to given timestamp argument
    - Refer `test_block` method in [example](#simple_score2/tests/test_unit_simple_score2.py)

- Patching InternalCall & asserting InternalCall
  - register_interface_score(internal_score_address)<br>
    - This method should be called before testing the internal_call that calls the SCORE method with an `internal_score_address` address.
      If you call this method, you can use the `assert_internal_call` method to evaluate whether internal_call is called properly with specified arguments.<br>
    - **parameters**
      - **internal_score_address** : address of interface SCORE
    - Refer `test_internal2` method in [example](#simple_score2/tests/test_unit_simple_score2.py) 
  - patch_internal_method(score_address, method, new_method)<br>
    - You will use this method for patching query method to set return value.
      Since this function internally calls `register_interface_score`, you don't need to call `register_interface_score` when calling this function.
      The third argument, the new method, must be a function with the same number of arguments as the actual method.<br>
    - **parameters**
      - **internal_score_address** : address of the SCORE having method to be called
      - **method** : method to be patched
      - **new_method** : method to patch
    - Refer `test_interanl` method in [example](#simple_score2/tests/test_unit_simple_score2.py)
  - assert_internal_call(internal_score_address, method, *params)<br>
    - assert that internal call(mock) was called with the specified arguments. Raises an AssertionError if the params passed in are different to the last call to the mock.<br>
    - **parameters**
      - **internal_score_address** : address of internal call SCORE
      - **method** : method to check
      - **params** : params to check
    - Refer `test_internal` method in [example](#simple_score2/tests/test_unit_simple_score2.py)

- Utils 
    - transfer(_from, to, amount)<br>

      - Transfer icx to given 'to' address. If you pass a SCORE address to the `to` argument, this method calls the SCORE fallback method.<br>
      - **parameters**
        - **_from** : address of sender
        - **to** : address of receiver
        - **amount** : amount to transfer
      - Refer `test_transfer` method in [example](#simple_score2/tests/test_unit_simple_score2.py)

    - get_balance(address)<br>

      - Query icx balance of given address.<br>
      - **parameters**
        - **address** : address to query for icx balance
      - Refer `test_get_balance` method in [example](#simple_score2/tests/test_unit_simple_score2.py)

    - initialize_accounts(accounts_info)<br>

      - Initialize accounts using given dictionary info.<br>
      - **parameters**
        - **accounts_info** : dictionary with address as key and balance as value
      - Refer `setUp` method in [example](#simple_score2/tests/test_unit_simple_score2.py)

### examples

In this example, we'll use two simple SCORE only have getter and setter.(first SCORE has getter and setter and other SCORE has internalCall, getter and setter)

#### simple_score/simple_score.py

```python
from iconservice import *


class SimpleScore(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.value = VarDB("value", db, value_type=str)

    @eventlog()
    def SetValue(self, value: str): pass

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()
        self.value.set("updated value")
    
    @external(readonly=True)
    def hello(self) -> str:
        return "Hello"

    @external
    def setValue(self, value: str):
        self.value.set(value)

        self.SetValue(value)

    @external(readonly=True)
    def getValue(self) -> str:
        return self.value.get()
        
```

#### simple_score2/simple_score2.py

```python
from iconservice import *


class SimpleScoreInterface(InterfaceScore):
    @interface
    def setValue(self, value): pass

    @interface
    def getValue(self)->str: pass


class SimpleScore2(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.value = VarDB("value1", db, value_type=str)
        self.score_address = VarDB("score_address", db, value_type=Address)

    @eventlog(indexed=0)
    def SetValue(self, value: str): pass

    @eventlog(indexed=1)
    def SetSCOREValue(self, value: str): pass

    def on_install(self, score_address: 'Address') -> None:
        super().on_install()
        self.score_address.set(score_address)

    def on_update(self, value: str) -> None:
        super().on_update()
        self.value.set(value)
    
    @external(readonly=True)
    def getValue(self) -> str:
        return self.value.get()

    @external
    def setValue(self, value: str):
        self.value.set(value)

        self.SetValue(value)

    @external
    def setSCOREValue(self, value: str):
        score = self.create_interface_score(self.score_address.get(), SimpleScoreInterface)
        score.setValue(value)

        self.SetSCOREValue(value)

    @external(readonly=True)
    def getSCOREValue(self) ->str:
        score = self.create_interface_score(self.score_address.get(), SimpleScoreInterface)

        return score.getValue()

    @external(readonly=True)
    def write_on_readonly(self) ->str:
        self.value.set('3')
        return 'd'
        
    # This method is for understanding the ScoreTestCase.set_msg method.
    def t_msg(self):
        assert self.msg.sender == Address.from_string(f"hx{'1234'*10}")
        assert self.msg.value == 3
    
    # This method is for understanding the ScoreTestCase.set_tx method.
    def t_tx(self):
        assert self.tx.origin == Address.from_string(f"hx{'1234'*10}")
    
    # This method is for understanding the ScoreTestCase.set_block method.
    def t_block(self):
        assert self.block.height == 3
        assert self.block.timestamp == 30
        assert self.block_height ==3
        assert self.now() == 30

```

#### simple_score2/tests/test_unit_simple_score2.py
```python
from iconservice import Address
from iconservice.base.exception import DatabaseException
from tbears.libs.scoretest.score_unit_test_base import ScoreTestCase

from ..simple_score2 import SimpleScore2


class TestSimple(ScoreTestCase):
    def setUp(self):
        super().setUp()
        self.mock_score_address = Address.from_string(f"cx{'1234'*10}")
        self.score2 = self.get_score_instance(SimpleScore2, self.test_account1,
                                              on_install_params={'score_address': self.mock_score_address})
                                              
        self.test_account3 = Address.from_string(f"hx{'12345'*8}")
        self.test_account4 = Address.from_string(f"hx{'1234'*10}")
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

    # try writing value inside readonly method
    def test_write_on_readonly(self):
        self.assertRaises(DatabaseException, self.score2.write_on_readonly)

    # internal call
    def test_internal_call(self):
        self.patch_internal_method(self.mock_score_address, 'getValue', lambda: 150) # Patch the getValue function of SCORE at self.mock_score_address address with a function that takes no argument and returns 150
        value = self.score2.getSCOREValue()
        self.assertEqual(value, 150)
        self.assert_internal_call(self.mock_score_address, 'getValue') # assert getValue in self.mock_score_address is called.
        
        self.score2.setSCOREValue('asdf')
        self.assert_internal_call(self.mock_score_address, 'setValue', 'asdf') # assert setValue in self.mock_score_address is called with 'asdf'

    # internal call
    def test_internal_call2(self):
        # To determine whether a method is called properly with specified arguments, calling register_interface_score method is enough
        self.register_interface_score(self.mock_score_address)
        self.score2.setSCOREValue('asdf')
        self.assert_internal_call(self.mock_score_address, 'setValue', 'asdf')
        
    def test_msg(self):
        self.set_msg(Address.from_string(f"hx{'1234'*10}"), 3)
        self.score2.t_msg() # On the upper line, set the msg property to pass the assert statement so that no exception is raised.

        self.set_msg(Address.from_string(f"hx{'12'*20}"), 3)
        self.assertRaises(AssertionError, self.score2.t_msg) # On the upper line, set the msg property not to pass the assert statement, and raise an exception.

    def test_tx(self):
        self.set_tx(Address.from_string(f"hx{'1234'*10}"))
        self.score2.t_tx() # On the upper line, set the tx property to pass the assert statement so that no exception is raised.

        self.set_tx(Address.from_string(f"hx{'12'*20}"))
        self.assertRaises(AssertionError, self.score2.t_tx) # On the upper line, set the tx property not to pass the assert statement, and raise an exception.

    def test_block(self):
        self.set_block(3, 30)
        self.score2.t_block() # On the upper line, set the block property to pass the assert statement so that no exception is raised.

        self.set_block(3)
        self.assertRaises(AssertionError, self.score2.t_block) # On the upper line, set the block property not to pass the assert statement, and raise an exception.
        
    def test_update(self):
        self.score2 = self.update_score(self.score2.address, SimpleScore2, on_update_params={"value": "updated_value"})
        self.assertEqual(self.score2.value.get(), "updated_value") # In the on_update method of SimpleScore2, set the value of the value to "updated_value".

    def test_get_balance(self):
        balance = self.get_balance(self.test_account3)
        self.assertEqual(balance, 10**21)

    def test_transfer(self):
        # before calling transfer method, check balance of test_account3 and test_account4
        amount = 10**21
        balance_3 = self.get_balance(self.test_account3)
        self.assertEqual(balance_3, amount)
        balance_4 = self.get_balance(self.test_account4)
        self.assertEqual(balance_4, amount)

        self.transfer(self.test_account3, self.test_account4, amount)
        # after calling transfer method, check balance of test_account3 and test_account4
        balance_3 = self.get_balance(self.test_account3)
        self.assertEqual(balance_3, 0)
        balance_4 = self.get_balance(self.test_account4)
        self.assertEqual(balance_4, amount*2)
```

#### Run test code

```bash
$ tbears test simple_score2
........
----------------------------------------------------------------------
Ran 11 tests in 0.027s

OK
```
