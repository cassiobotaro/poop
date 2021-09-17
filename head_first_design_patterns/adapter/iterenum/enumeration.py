"""
- _T_co is a covariant type used to specify the type used
in the Enumeration protocol
Great explanation about covariance:
https://blog.daftcode.pl/covariance-contravariance-and-invariance-the-ultimate-python-guide-8fabc0c24278
- To keep the code like the original, I have to define Enumeration Protocol
In Java this protocol exists.
- ConcreteEnumeration is a class that implements the Enumeration Protocol
- EnumerationIterator  is a wrapper in which the enumeration is stored
- Iterator interface is used to get values from the enumeration
- It's is generic and can contains any type T of enumeration
- Inherit from Iterator and win the method __iter__ returning itself
- EnumerationIterator is an adapter that adapts the Enumeration
to the Iterator protocol
"""
from collections.abc import Iterator, Iterable
from typing import Generic, Protocol, TypeVar

_T_co = TypeVar("_T_co", covariant=True)
_T = TypeVar("_T")


class Enumeration(Protocol[_T_co]):
    def has_more_elements(self) -> bool:
        ...

    def next_element(self) -> _T_co:
        ...


class ConcreteEnumeration(Generic[_T]):
    def __init__(self, values: Iterable[_T]) -> None:
        self.__values = list(values)

    def has_more_elements(self) -> bool:
        return bool(self.__values)

    def next_element(self) -> _T:
        return self.__values.pop(0)


class EnumerationIterator(Iterator[_T]):
    def __init__(self, enumeration: Enumeration[_T]) -> None:
        self.enumeration = enumeration

    def __next__(self) -> _T:
        if self.enumeration.has_more_elements():
            return self.enumeration.next_element()
        else:
            raise StopIteration
