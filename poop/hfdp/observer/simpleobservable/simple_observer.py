from typing import Any

from poop.hfdp.observer.simpleobservable.simple_subject import SimpleSubject
from poop.hfdp.observer.util import Observable


class SimpleOberver:
    def __init__(self, observable: Observable) -> None:
        self.__value = 0
        self.__observable = observable
        self.__observable.add_observer(self)

    def update(self, observable: "Observable", arg: Any) -> None:
        print(arg)
        self.__value = int(arg)
        self.display()
        if isinstance(observable, SimpleSubject):
            self.value = observable.get_value()
            self.display()

    def display(self) -> None:
        print(f"Value: {self.__value}")
