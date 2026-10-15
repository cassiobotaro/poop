# Proposal

## Why

A review that tried to reach raw Python from inside a POOP program found six
doors still open: two syntactic forms no validator reads (PEP 695 type
parameters, `class` keywords), one hook that hands user code a native `str`,
one alias with the convert-versus-build gap every other constructor closed,
exception *instances* that answer three `BaseException` natives and none of
the messages a caught error answers, and dunder *definitions* that rewire the
message protocol without any guard. Each one answers CPython's sentence —
`'str' object has no attribute 'print'`, `KeyError: '__import__'` — where
`INFECTIONS.md` says "no naked Python primitive ever reaches runtime".

## What Changes

- **`no_type_alias` also refuses type parameters**: `class X[T]:` and
  `def m[T](self):` are rejected at validation, where today the first dies
  with an internal `KeyError: '__import__'` and the second hands the program
  a raw `typing.TypeVar`. Three rows in the existing node table.
- **A new validator, `no_class_keyword`**, refuses every keyword in a `class`
  statement (`class X(foo=1)`, `metaclass=…`), which today reach CPython's
  `__init_subclass__` and metaclass machinery and answer its sentences.
  README's validator count becomes 72 (73 with the next item).
- **A new validator, `no_dunder_def`**, refuses defining a dunder method a
  user class is not allowed to satisfy: `__getattribute__`, `__getattr__`,
  `__init_subclass__`, `__set_name__`, `__new__`, `__class_getitem__`,
  `__get__`/`__set__`/`__delete__`, `__slots__` as a body assignment is
  already `no_dunder_name`'s. The protocol slots `INFECTIONS.md` says a class
  *may* define (`__init__`, `__str__`, `__repr__`, `__bool__`, `__hash__`,
  `__len__`, `__call__`, the comparisons, every operator slot, `__enter__` /
  `__exit__`) stay legal. `__getattr__` is refused by name with its substitute
  spelled: `does_not_understand`.
- **`no_class_machinery` refuses two more positions**: `super()` inside a
  `lambda` (CPython answers `RuntimeError: super(): no arguments`, a sentence
  about a cell the lambda has no way to own), and `return <value>` directly in
  an `__init__` body (CPython answers `__init__() should return None`).
- **`does_not_understand` and a user `__getattr__` receive a `Str`**, so a
  hook that answers the name it was asked answers a POOP string.
- **A bare `slice` is an alias, not the class**: `s = slice; s(5)` and
  `class S(slice): pass; S(5)` build through the one-argument-is-stop
  converter like the twelve sibling constructors, instead of calling the
  class directly and silently answering a different slice.
- **An exception instance a program builds is a whole POOP object**:
  `ValueError("x")` answers `message()`, `kind()`, `raise_()` and prints as
  `ValueError: x` like a caught `Error`; `args`, `add_note` and
  `with_traceback` are refused on the instance with the sentences the class
  side already uses.

Out of scope, and why: the wording of constructor arity failures on user
classes (`Foo() takes no arguments`, `E.__init__() missing …`) and every other
*sentence* leak — those are answers in the wrong words, not raw objects, and
belong to `fix-wrapper-equality-and-errors`; `@x.setter`, a banned form with
no substitute named, which is a language-surface decision rather than a leak
and deserves its own change; `nonlocal`, which `no_global` already refuses.

## Capabilities

### New Capabilities

- `no-class-keyword-validator`: a `class` statement carries no keywords.
- `no-dunder-def-validator`: a user class defines only the dunders POOP can
  honour.
- `exception-mirrors`: what an exception instance built by a program answers.

### Modified Capabilities

- `no-type-alias-validator`: type parameters are refused alongside `type`
  aliases.
- `no-class-machinery-validator`: `super()` in a lambda and `return <value>`
  in `__init__` are refused.
- `slice-transformer`: a bare `slice` names an alias whose call converts.
- `object-type`: the `does_not_understand` hook receives a `Str`.

## Impact

- `poop/validators/`: `no_type_alias.py`, new `no_class_keyword.py`, new
  `no_dunder_def.py`, `no_class_machinery.py`, `__init__.py` ordering.
- `poop/transformers/slice.py`: a `builtin_alias` binding as `_cls`.
- `poop/types/object.py` (`__getattr__` → hook argument),
  `poop/types/exceptions.py` (`_build` instance side, instance refusals).
- `poop/repl.py`: `:explain` derives its topics from the validators, so the
  two new ones need snippets in `_EXPLAIN_SNIPPETS`.
- Docs: `README.md` validator count and ban list, `INFECTIONS.md` sections for
  the two new validators and the exception instance side, `MIGRATION.md` rows
  for `class X[T]`, `class X(metaclass=…)` and `__getattr__`.
