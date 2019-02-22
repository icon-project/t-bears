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
|\<project>/package.json    | Contains the information needed when SCORE is loaded. <br> "main_file" and "main_class" is necessary. |
|\<project>/<project>.py    | SCORE main file.                  |
|\<project>/tests           | Directory for SCORE test code.                              |
|\<project>/tests/\_\_init\_\_.py | \_\_init\_\_.py file to make the test directory recognized as a python package. |
|\<project>/tests/test\_integrate\_\<project>.py    | SCORE integrate test file.  |
|\<project>/tests/test\_unit\_\<project>.py    | SCORE unit test file.  |

* When T-Bears deploys SCORE, the `tests` directory is not included.

## How to write SCORE unit test code

The SCORE unit test code works as follows

1. get SCORE instance to be tested
2. Call SCORE method
3. Check the result

#### ScoreTestCase in T-Bears

Every SCORE unit test class must inherit `ScoreTestCase`.

ScoreTestCase class provides three functions

1. Support python unittest

   1. You can write and run the test method with prefix 'test_'
   2. You can initialize and finalize the test by override setUp and tearDown method

2. Set properties used inside SCOREs.

   1. set_msg(sender, value)

      Set msg property in SCORE

   2. set_tx(origin, timestamp, _hash, index, nonce)

      Set tx property in SCORE
      
   3. set_block(height, timestamp)

      Set block property in SCORE
      
3. Get instantiated SCORE

   1. get_score_instance(score_class, owner, on_install_params)
      Get an instance of the SCORE class passed as an score_class arguments
      
   2. update_score(prev_score_address, score_class, on_update_params)
      Update SCORE at `prev_score_address` with `score_class` instance and get updated SCORE

After this method is called, the msg property is set to sender is owner, and value is set to 0.

4. Mock Internal Call(Calling other SCORE method)

   1. register_interface_score(internal_score_address)
      
      This method should be called before testing the internal_call that calls the SCORE method with an `internal_score_address` address.
      If you call this method, you can use the `assert_internal_call` method to evaluate whether internal_call is called properly with specified arguments.
      
   
   2. patch_internal_method(score_address, method, new_method)
   
      You will use this method for patching query method to set return value.
      Since this function internally calls `register_interface_score`, you don't need to call `register_interface_score` when calling this function.
      The third argument, the new method, must be a function with the same number of arguments as the actual method.
      

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

    def on_update(self) -> None:
        super().on_update()
    
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

    def tearDown(self):
        super().tearDown()

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
        # Patch the getValue function of SCORE at self.mock_score_address address with a function that takes no argument and returns 150
        self.patch_internal_method(self.mock_score_address, 'getValue', lambda: 150)
        value = self.score2.getSCOREValue()
        self.assertEqual(value, 150)
        self.assert_internal_call(self.mock_score_address, 'getValue')
        
        # You only need to call patch_internal_method or register_interface_score called once.
        self.score2.setSCOREValue('asdf')
        self.assert_internal_call(self.mock_score_address, 'setValue', 'asdf')

    # internal call
    def test_internal_call2(self):
        # To determine whether a method is called properly with specified arguments, calling register_interface_score method is enough
        self.register_interface_score(self.mock_score_address)
        self.score2.setSCOREValue('asdf')
        self.assert_internal_call(self.mock_score_address, 'setValue', 'asdf')
```

#### Run test code

```bash
$ tbears test simple_score2
....
----------------------------------------------------------------------
Ran 5 tests in 0.006s

OK
```
