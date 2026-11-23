# 17. A class may not define lookup, creation or descriptor dunders

Date: 2026-04-22

## Status

Accepted

## Context

Reading a dunder is `no_dunder_attribute`'s concern and a bare dunder name is `no_dunder_name`'s, but a class body could still define one with no validator looking. `def __getattribute__(self, name): return 1` silently answered `1` for every message sent to the instance. The `2026-10-15-close-raw-python-leaks` change found this among six doors that still reached raw Python from inside a program.

A user class is allowed to define the operator and protocol slots (`__init__`, `__str__`, `__repr__`, `__bool__`, `__hash__`, `__len__`, `__call__`, the comparisons, every operator slot, `__enter__` / `__exit__`), and `PoopMeta.__new__` adapts the CPython reads among them itself. An allow-list was the alternative and was rejected: it would refuse every operator slot nobody thought to enumerate (there are forty), and the cost of missing one is a legal program refused. The cost of missing a deny-list entry is one more leak, which the wording sweep catches.

## Decision

`no_dunder_def` (`poop/validators/no_dunder_def.py`) refuses an `ast.FunctionDef` in an `ast.ClassDef` body that defines one of three protocols a POOP program has no business in:

- the lookup protocol, `__getattribute__`, `__getattr__`, `__setattr__`, `__delattr__`, `__dir__`: defining one rewires every message sent to the instance. The substitute is `does_not_understand(self, name)` for the messages a class does not answer; `set_attr`, `del_attr` and `dir` already exist.
- class creation, `__new__`, `__init_subclass__`, `__class_getitem__`, `__subclasshook__`: CPython calls them with raw arguments. A class is built from its bases alone (ADR 19).
- the descriptor protocol, `__set_name__`, `__get__`, `__set__`, `__delete__`: CPython hands `__set_name__` a raw `str` and `__get__` a raw `None`. A POOP object is reached by messages, not by descriptors.

Each row carries its own sentence, so `__getattr__` is refused by name with its substitute spelt. The validator runs after `no_class_keyword` in `DEFAULT_VALIDATORS`.

## Consequences

The operator and protocol slots stay legal, so this is a deny-list of three protocols rather than an allow-list. No example defined `__getattr__` (`grep -rn "__getattr__" examples/` was empty), and the refusal names the substitute for a program that did. The validator's test parametrises over `dir(object)` and asserts each name is either refused, in the documented legal set, or absent from the language, and `tests/test_no_python_wording.py` sweeps a user class against every dunder it can spell.
