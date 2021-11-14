from typing import Protocol, TypeVar

_T_co = TypeVar("_T_co", covariant=True)


class Enumeration(Protocol[_T_co]):
    def has_more_elements(self) -> bool:
        ...

    def next_element(self) -> _T_co:
        ...
