from collections.abc import Iterable
from typing import Generic, TypeVar

_T = TypeVar("_T")


class ConcreteEnumeration(Generic[_T]):
    def __init__(self, values: Iterable[_T]) -> None:
        self.__values = list(values)

    def has_more_elements(self) -> bool:
        return bool(self.__values)

    def next_element(self) -> _T:
        return self.__values.pop(0)
