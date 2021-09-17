"""Notes:
- The adapter pattern is used to convert the interface of a class into another
interface the clients expect.
- EnumerationIterator is an adapter that converts an Enumeration into an
Iterator.
- IteratorEnumeration is an adapter that converts an Iterator into an
Enumeration.
"""
from collections.abc import Iterator

from enumeration import ConcreteEnumeration, Enumeration, EnumerationIterator
from iterator import IteratorEnumeration

enumeration: Enumeration[int] = ConcreteEnumeration([1, 2, 3, 4, 5])

# we can iterate a enumeration using the iterator interface (protocol)
iterator: Iterator[int] = EnumerationIterator(enumeration)
for i in iterator:
    print(i)

# we iterate a iterator using  the enumerator interface (protocol)
iterator_enumeration: Enumeration[int] = IteratorEnumeration(
    iter([1, 2, 3, 4, 5])
)
while iterator_enumeration.has_more_elements():
    print(iterator_enumeration.next_element())
