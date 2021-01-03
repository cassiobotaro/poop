from abc import ABC, abstractmethod

"""
 Notes:
 - ABC is used to force methods implementations
 - Subject class represents a topic to follow,
 when your state changes, all observers will
 be notified
 - Subject is an interface (a protocol) to be implemented
 by its subclasses
"""


class Subject(ABC):
    @abstractmethod
    def register_observer(self, observer):
        raise NotImplementedError

    @abstractmethod
    def remove_observer(self, observer):
        raise NotImplementedError

    @abstractmethod
    def notify_observers(self):
        raise NotImplementedError


"""
 Notes:
 - ABC is used to force methods implementations
 - Observer class represents an observer object, that will receive
 an update by Subject.
 - Observer is an interface (a protocol) to be implemented
 by its subclasses
"""


class Observer(ABC):
    @abstractmethod
    def update(self, temperature, humidity, pressure):
        raise NotImplementedError


"""
Notes:
- DisplayElement it is a mere formality but it is not necessary.
- Forces your subclasses to have an implementation of the display method
"""


class DisplayElement(ABC):
    @abstractmethod
    def display(self):
        raise NotImplementedError
