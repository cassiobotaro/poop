from collections.abc import Iterator

from head_first_design_patterns.adapter.iterenum.concrete_enumeration import (
    ConcreteEnumeration,
)
from head_first_design_patterns.adapter.iterenum.enumeration import Enumeration
from head_first_design_patterns.adapter.iterenum.enumeration_iterator import (
    EnumerationIterator,
)

enumeration: Enumeration[int] = ConcreteEnumeration([1, 2, 3, 4, 5])
iterator: Iterator[int] = EnumerationIterator(enumeration)
for i in iterator:
    print(i)
