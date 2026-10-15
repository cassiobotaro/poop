# Spec Delta

## Purpose

A user class defines only the dunder methods POOP can honour as messages; the
slots that would rewire attribute lookup, class creation or descriptors are
refused with their substitute named.

## ADDED Requirements

### Requirement: Lookup and creation dunders cannot be defined
The validator SHALL refuse a `def` in a class body whose name is
`__getattribute__`, `__getattr__`, `__setattr__`, `__delattr__`, `__new__`,
`__init_subclass__`, `__set_name__`, `__class_getitem__`, `__get__`,
`__set__`, `__delete__`, `__dir__` or `__subclasshook__`.

#### Scenario: Rewiring every message is refused
- **WHEN** a class body contains `def __getattribute__(self, name):`
- **THEN** validation fails with `defining __getattribute__ is forbidden — it is Python's lookup protocol; define does_not_understand(self, name) for the messages the class does not answer`

#### Scenario: The fallback hook has a POOP spelling
- **WHEN** a class body contains `def __getattr__(self, name):`
- **THEN** validation fails with `defining __getattr__ is forbidden — define does_not_understand(self, name) instead`

#### Scenario: A creation hook is refused
- **WHEN** a class body contains `def __init_subclass__(cls):`
- **THEN** validation fails with `defining __init_subclass__ is forbidden — a class is built from its bases alone`

#### Scenario: A descriptor slot is refused
- **WHEN** a class body contains `def __set_name__(self, owner, name):`
- **THEN** validation fails with `defining __set_name__ is forbidden — a POOP object is reached by messages, not by descriptors`

### Requirement: Protocol slots a class may satisfy stay legal
The validator SHALL leave `__init__`, `__str__`, `__repr__`, `__bool__`,
`__hash__`, `__len__`, `__call__`, `__iter__`, `__next__`, `__enter__`,
`__exit__`, the six comparison slots and every binary, reflected, in-place
and unary operator slot untouched.

#### Scenario: The documented slots pass
- **WHEN** a class body defines `__init__`, `__eq__`, `__lt__`, `__add__`, `__radd__`, `__neg__`, `__str__`, `__enter__` and `__exit__`
- **THEN** this validator reports nothing and the program runs as before
