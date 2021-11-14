from collections.abc import Iterator
from typing import Generic, TypeVar

_T = TypeVar("_T")


class IteratorEnumeration(Generic[_T]):
    def __init__(self, iterator: Iterator[_T]) -> None:
        self.__iterator = iterator
        self.__next = next(self.__iterator, None)

    def has_more_elements(self) -> bool:
        return bool(self.__next)

    def next_element(self) -> _T:
        if self.__next is not None:
            # as we check if there is a next element, mypy don't complain
            # about the return type
            current, self.__next = self.__next, next(self.__iterator, None)
            return current
        raise StopIteration
