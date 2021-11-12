from head_first_design_patterns.adapter.iterenum.enumeration import Enumeration
from head_first_design_patterns.adapter.iterenum.iterator_enumeration import (
    IteratorEnumeration,
)

iterator_enumeration: Enumeration[int] = IteratorEnumeration(
    iter([1, 2, 3, 4, 5])
)
while iterator_enumeration.has_more_elements():
    print(iterator_enumeration.next_element())
