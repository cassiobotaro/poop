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
