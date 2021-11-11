"""Notes:
- IteratorEnumeration is a wrapper in which the iterator is stored.
- Enumeration interface is used to get values from the iterator.
- It's is generic and can contains any type T of iterator.
- We don't need to inherit from Enumeration because of structural typing.
- IteratorEnumeration is an adapter which adapts the iterator to the
 Enumeration interface.
"""
from collections.abc import Iterator
from typing import Generic, TypeVar

_T = TypeVar("_T")


class IteratorEnumeration(Generic[_T]):
    def __init__(self, iterator: Iterator[_T]) -> None:
        self.iterator = iterator
        self.next = next(self.iterator, None)

    def has_more_elements(self) -> bool:
        return bool(self.next)

    def next_element(self) -> _T:
        if self.next is not None:
            # as we check if there is a next element, mypy don't complain
            # about the return type
            current, self.next = self.next, next(self.iterator, None)
            return current
        raise StopIteration
