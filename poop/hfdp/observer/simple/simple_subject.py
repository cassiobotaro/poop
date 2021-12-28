from poop.hfdp.observer.simple.observer import Observer


class SimpleSubject:
    def __init__(self) -> None:
        self.__observers: list[Observer] = []
        self.__value = 0

    def register_observer(self, observer: Observer) -> None:
        self.__observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        self.__observers.remove(observer)

    def notify_observers(self) -> None:
        for observer in self.__observers:
            observer.update(self.__value)

    def set_value(self, value: int) -> None:
        self.__value = value
        self.notify_observers()
