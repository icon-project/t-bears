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
