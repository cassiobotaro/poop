from poop.hfdp.observer.simple.subject import Subject


class SimpleObserver:
    def __init__(self, simple_subject: Subject) -> None:
        self.__value = 0
        self.__simple_subject = simple_subject
        self.__simple_subject.register_observer(self)

    def update(self, value: int) -> None:
        self.__value = value
        self.display()

    def display(self) -> None:
        print(f"Value: {self.__value}")
