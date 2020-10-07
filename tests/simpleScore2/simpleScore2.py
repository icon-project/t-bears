from iconservice import *


class SimpleScoreInterface(InterfaceScore):
    @interface
    def setValue(self, value): pass

    @interface
    def getValue(self) -> str: pass


class SimpleScore2(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.value = VarDB("value1", db, value_type=str)
        self.array = ArrayDB("arrayDB", db, value_type=int)
        self.dict = DictDB("dictDB", db, value_type=int)
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
        self._setValue(value)

        self.SetValue(value)

    @external
    def setSCOREValue(self, value: str):
        score = self.create_interface_score(self.score_address.get(), SimpleScoreInterface)
        score.setValue(value)

        self.SetSCOREValue(value)

    @external(readonly=True)
    def getSCOREValue(self) -> str:
        score = self.create_interface_score(self.score_address.get(), SimpleScoreInterface)

        return score.getValue()

    @external(readonly=True)
    def getSCOREValue2(self) -> str:
        ret = self.call(self.score_address.get(), "getValue", {})
        return ret

    @external
    def appendValue(self, value: int):
        self.array.put(value)

    @external(readonly=True)
    def arrayLength(self) -> int:
        return len(self.array)

    @external
    def arraySetItem(self, index: int, value: int):
        self.array[index] = value

    @external(readonly=True)
    def arrayGetItem(self, index: int) -> int:
        return self.array[index]

    @external(readonly=True)
    def arraySum(self) -> int:
        # written for testing __iter__
        return sum(self.array)

    @external
    def dictSetItem(self, key: int, value: int):
        self.dict[key] = value

    @external(readonly=True)
    def dictGetItem(self, key: int) -> int:
        return self.dict[key]

    @external(readonly=True)
    def dictContains(self, key: int) -> int:
        return key in self.dict

    @external(readonly=True)
    def write_on_readonly(self) -> str:
        self._setValue('3')
        return 'd'

    # This method is for understanding the ScoreTestCase.set_msg method.
    def t_msg(self):
        assert self.msg.sender == Address.from_string(f"hx{'1234' * 10}")
        assert self.msg.value == 3

    # This method is for understanding the ScoreTestCase.set_tx method.
    def t_tx(self):
        assert self.tx.origin == Address.from_string(f"hx{'1234' * 10}")

    # This method is for understanding the ScoreTestCase.set_block method.
    def t_block(self):
        assert self.block.height == 3
        assert self.block.timestamp == 30
        assert self.block_height == 3
        assert self.now() == 30

    @external(readonly=True)
    def get_balance(self, address: Address) -> int:
        return self.icx.get_balance(address)

    @external
    def transfer(self, to: Address, amount: int):
        self.icx.transfer(to, amount)

    @external
    def send(self, to: Address):
        self.icx.send(to, self.msg.value)

    @external
    def get_owner(self) -> Address:
        return self.owner

    @external
    def simple_json_dumps(self) -> str:
        return json_dumps({"simple": "value"})

    def _setValue(self, value: str):
        self.value.set(value)
