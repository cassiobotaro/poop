from poop.hfdp.observer.util import Observable


class SimpleSubject(Observable):
    def __init__(self) -> None:
        super().__init__()
        self.__value = 0

    def set_value(self, value: int) -> None:
        self.__value = value
        self.set_changed()
        self.notify_observers(value)

    def get_value(self) -> int:
        return self.__value
