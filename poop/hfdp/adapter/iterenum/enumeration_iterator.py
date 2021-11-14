from collections.abc import Iterator
from typing import TypeVar

from poop.hfdp.adapter.iterenum.enumeration import Enumeration

_T = TypeVar("_T")


class EnumerationIterator(Iterator[_T]):
    def __init__(self, enumeration: Enumeration[_T]) -> None:
        self.__enumeration = enumeration

    def __next__(self) -> _T:
        if self.__enumeration.has_more_elements():
            return self.__enumeration.next_element()
        else:
            raise StopIteration
