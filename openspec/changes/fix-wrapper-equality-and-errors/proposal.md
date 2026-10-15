# Proposal

## Why

The same review found answers that are wrong, and answers that are right in
CPython's words. A subclass of a wrapper is never equal to the wrapper, so
`{Name("a"): 1}.at("a")` is a `KeyError`; a handler cannot read the fields of
the exception it caught; `range(0)` is truthy; a validator points at a
substitute the runtime refuses; and a dozen messages, most on the class
side, still answer `type object 'A' has no attribute`, `__delete__`, `end
must be None or a string`, `Try.__init__() missing 1 required positional
argument`. Each one is a POOP object answering, in the wrong words or with
the wrong truth value.

## What Changes

- **Value equality is symmetric across a subclass**: `Name("a") == "a"` and
  `"a" == Name("a")` are both `True`, and a dict keyed by one is found by
  the other, as in CPython.
- **A caught error forwards the state its exception carries**: `e.code`
  answers the `code` a program's `__init__` stored, `has_attr`/`get_attr`/
  `dir` see it; methods and dunders stay refused.
- **Two errors wrapping one exception are equal and hash alike**, so the
  error `raise_` re-signals compares equal to the one first caught.
- **`range(0)` is falsy and `range` answers `includes` by membership**, like
  every other collection.
- **`True.class_()` is `bool`**: the two singletons answer one class, equal
  to the bare name, as `(5).class_() == int` already is.
- **`xor` and `eqv` require a `Boolean`** and refuse anything else in the
  `a_block` shape; today `False.xor(5)` answers `5`.
- **Class-side `del_attr`, `format` and `print(end=…)` word their refusals**
  as the instance side does, and `class_side` descriptors refuse deletion with
  the sentence they refuse assignment with.
- **`Try()` and `With()` count their arguments in POOP's words**, as every
  builtin constructor does.
- **Wording on seven data-type messages**: `memoryview` finds a `Boolean`
  needle (`includes`, `count`, `index`); `bytearray.at_put` blames the value
  when the value is wrong; `range("a")` says `#range's stop must be an int,
  got a str`; `str`/`bytes`/`bytearray` `index`/`rindex` say `has no element
  equal to`; `Int.pow` admits a `Boolean` modulus; `frozendict.hash` names the
  value that cannot be hashed; `Slice.indices` refuses a non-int bound in
  the sentence `slice(...)` already uses.
- **`no_private_attribute`'s message tells the truth**: the substitute for
  reading another object's `_x` is a message that object answers, not
  `get_attr`.

Out of scope, and why: `Sentinel` being subclassable where CPython refuses —
a divergence worth a note in `INFECTIONS.md`, not a behavior anyone relies
on either way; the wording of `Foo(5)` on a class with no `__init__`
(`Foo() takes no arguments`) — it names no dunder and no call and the
rewording helper would have to parse CPython's sentence, which `_message.py`
deliberately does for operators only; raw-object leaks, which
`close-raw-python-leaks` closes.

## Capabilities

### New Capabilities

- `value-equality`: how a wrapper, a subclass of one and its raw value
  compare.
- `error-type`: what a caught error answers beyond `message`/`kind`.
- `range-type`: truthiness and membership of a range.
- `boolean-type`: the class the two singletons answer; `xor`/`eqv` guards.
- `class-side`: the messages every class answers, worded like the instance
  side.
- `try-type`, `with-type`: constructor arity in POOP's words.
- `range-transformer`: the converter's refusal of a non-int argument.
- `int-type`: `pow`'s modulus admits the index rung.
- `frozendict-type`: `hash` names the value at fault.
- `no-private-attribute-validator`: the message names a real substitute.

### Modified Capabilities

- `object-type`: `print`'s `end` and `sep` are checked in POOP's words.
- `memoryview-type`: a `Boolean` needle is found.
- `bytearray-type`: `at_put` blames the argument at fault.
- `str-type`, `bytes-type`: `index`/`rindex` miss in the family's words.
- `slice-type`: `indices` refuses a non-int bound as `slice` does.

## Impact

- `poop/types/`: `_value_eq.py`, `error.py`, `range.py`, `boolean.py`,
  `meta.py`, `try_.py`, `with_.py`, `object.py`, `_sequence.py`,
  `memory_view.py`, `byte_array.py`, `string.py`, `_bytes_like.py`,
  `int.py`, `frozen_dict.py`, `slice.py`.
- `poop/transformers/range.py`; `poop/validators/no_private_attribute.py`.
- Tests: one module per surface above; `tests/test_no_python_wording.py`
  gains `print` (stdout redirected) and the class-side `format`/`del_attr`
  receivers in its sweep; `tests/test_transformers/test_range.py:80,89` pin
  the CPython sentence and change.
- Docs: `INFECTIONS.md` paragraphs for each decision; `README.md` is
  unchanged in counts.
