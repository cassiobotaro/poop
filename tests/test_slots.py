"""No POOP class carries a per-instance `__dict__`.

`__slots__` is step 1 of adding a type, and every wrapper declared it — but a
single slot-less class anywhere in an MRO restores the `__dict__` for
everything below it, and three shared mixins were slot-less. The declaration
was defeated on 36 of the 49 classes, so `"abc".set_attr("x", 1)` succeeded
while `(5).set_attr("x", 1)` refused: attached state on a value object, and
one message meaning two things on two rungs of the same tower.

A sweep rather than a per-mixin assertion, for the reason `test_cloak.py`
gives about its own leak: the next mixin is free to reopen it, and it would
reopen it for a third of the language at once.
"""

import pytest

from tests.test_cloak import _classes


@pytest.mark.parametrize(
    ("index", "cls"),
    list(enumerate(_classes())),
    ids=lambda arg: arg.__name__ if isinstance(arg, type) else str(arg),
)
def test_class_declares_slots(index: int, cls: type) -> None:
    assert "__slots__" in vars(cls), f"{cls.__name__} declares no __slots__"


@pytest.mark.parametrize(
    ("index", "cls"),
    list(enumerate(_classes())),
    ids=lambda arg: arg.__name__ if isinstance(arg, type) else str(arg),
)
def test_instances_carry_no_dict(index: int, cls: type) -> None:
    # The whole MRO, not `vars(cls)`: the descriptor that hands every instance
    # its own dict is installed on the *first* slot-less class in the chain,
    # which is exactly where the bug lived — the wrappers all declared
    # `__slots__` and carried a `__dict__` anyway.
    leaking = [base.__name__ for base in cls.__mro__ if "__dict__" in vars(base)]
    assert leaking == [], f"{cls.__name__} instances carry a __dict__ from {leaking}"
