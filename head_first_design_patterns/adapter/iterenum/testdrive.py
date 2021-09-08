from collections.abc import Iterator

from enumeration import ConcreteEnumeration, Enumeration, EnumerationIterator
from iterator import IteratorEnumeration

enumeration: Enumeration[int] = ConcreteEnumeration([1, 2, 3, 4, 5])

iterator: Iterator[int] = EnumerationIterator(enumeration)
for i in iterator:
    print(i)


iterator_enumeration: Enumeration[int] = IteratorEnumeration(
    iter([1, 2, 3, 4, 5])
)
while iterator_enumeration.has_more_elements():
    print(iterator_enumeration.next_element())
