from collections.abc import Iterator
from typing import TypeVar

from head_first_design_patterns.adapter.iterenum.enumeration import Enumeration

_T = TypeVar("_T")


class EnumerationIterator(Iterator[_T]):
    def __init__(self, enumeration: Enumeration[_T]) -> None:
        self.enumeration = enumeration

    def __next__(self) -> _T:
        if self.enumeration.has_more_elements():
            return self.enumeration.next_element()
        else:
            raise StopIteration
