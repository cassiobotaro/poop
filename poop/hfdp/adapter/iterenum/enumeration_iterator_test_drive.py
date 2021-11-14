from collections.abc import Iterator

from poop.hfdp.adapter.iterenum.concrete_enumeration import ConcreteEnumeration
from poop.hfdp.adapter.iterenum.enumeration import Enumeration
from poop.hfdp.adapter.iterenum.enumeration_iterator import EnumerationIterator


def main() -> None:
    enumeration: Enumeration[int] = ConcreteEnumeration([1, 2, 3, 4, 5])
    iterator: Iterator[int] = EnumerationIterator(enumeration)
    for i in iterator:
        print(i)
