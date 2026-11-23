# 44. Diagnostics never name a banned construct; operator errors use a pinned regex

Date: 2026-07-27

## Status

Accepted

## Context

CPython's error messages describe Python's constructs, and many of those constructs are banned in POOP. A wrapper that handed an argument straight to CPython answered in that vocabulary: `at` answered `string index out of range`, `list indices must be integers or slices, not str` and, for a missing key, the bare `'b'`; `pop` answered `pop index out of range` and `pop from empty list`; `list.index(x): x not in list` used the placeholder `x` where the value belongs; `int("abc")` answered `invalid literal for int() with base 10`; `d.do(lambda p: d.at_put("b", 2))` answered `dictionary changed size during iteration`, describing a `for` loop the program did not write. POOP had also authored four such messages itself, in raises through the mirrors: `complex`'s three type refusals and `int`'s base refusal.

The operator path cannot be fixed at the source. `"a" + 1` runs `Str.__add__`, which answers `NotImplemented`, then `Int.__radd__`, which answers `NotImplemented` too, and only then does CPython compose `unsupported operand type(s) for +: 'str' and 'int'`. No wrapper sees the failure, so there is nothing to catch. Matching another language's message text is a dependency on its internals.

Checks program by program left gaps. The program list is opt-in, and a leak survives simply by not being on it. When a third half was added, sending every public message on every wrapper with wrong-typed arguments, it found 47 distinct leaked messages across 114 receiver/message sites the day it was written, among them `isinstance() arg 2 must be a type` from `x.is_instance(…)` on all 15 receivers, `slice indices must be integers or None or have an __index__ method`, and `unsupported format string passed to list.__format__`. Three of CPython's most common sentences carried no call, no dunder and no operator, and ran under the patterns on 64 sites: `'str' object cannot be interpreted as an integer` (29 sites), `'int' object is not iterable` (33 sites) and `startswith first arg must be str or a tuple of str`. The receiver list itself covered only the seventeen values a program writes, none of the fifteen it only receives (`MemoryView`, `MappingProxy`, the dict views, every iterator, `Map`, `Filter`, `Enumerate`, `Zip`, `Block`, `ellipsis` and `Error`).

## Decision

A diagnostic POOP shows never names a construct POOP bans: no free-function call, no dunder, no subscript, no protocol POOP has no word for (it has no word "iterable"; "a collection" is what it says).

- Refusals of a wrong argument live in `poop/types/_argument.py`, one guard per argument kind rather than one per receiver: `a_class`, `a_bound`, `an_int`, `a_collection`, `a_pair`, `text_like`, `a_fill`, `byte_order`, `max_split`, `byte_source`. They answer, for example, `#center's width must be an int, got a str` and `#union expects a collection, got an int`.
- `poop/types/_at.py` owns the wording of `at` and the removing messages for all nine wrappers that answer `at`: `str has no element at 10 — it has 3 elements`, `list.at expects an int index, got a str`, `dict has no key 'b'`, `list has no element to remove — it is empty`, `set has no element equal to 2`. `no_element_equal_to` and `nothing_to_remove` take the mirror class as an argument, because `set.remove` raises `KeyError` where `list.remove` raises `ValueError`. Composing a sentence for `KeyError` gave the mirrors `Exception.__str__`.
- Mutation during iteration is caught where POOP iterates (`_IterableMixin.do` and the cursor in `_PeekMixin`), and only a native `RuntimeError` is reworded. Both name the collection; the cursor's label is derived by `_IteratorBase.__init_subclass__` from the CPython iterator name each iterator declares (`list_iterator` → `list`). The lazy views keep the default label, since the mutated collection is the one behind them.
- The operator path is reworded after the fact by `poop/types/_message.py`, which rewrites the two shapes POOP can reach into `str does not understand #+ with an int` and `int does not understand #< with a str`, the same register as `MessageNotUnderstood`. The operator is kept as the reader typed it, because POOP allows binary operators. Anything unmatched passes through unchanged. `executor._describe` and `Error.message()` both read through it.
- A view or sequence declines a foreign operand with `NotImplemented` rather than guarding it, so the operator refusal reads `list does not understand #+= with an int`.

The rule is swept mechanically by `tests/test_no_python_wording.py`, in three halves: the failing programs run end to end; a static walk of every string literal handed to a `mirrors.<Name>(...)` call in `poop/types` and `poop/transformers`; and every public message on every wrapper sent with wrong-typed arguments. One exemption list carries the phrases a message may legitimately quote, such as a hint showing the POOP spelling (`obj.get_attr(...)`). CPython's wrong-arity shape is exempt; ADR 45 covers it.

## Consequences

- The same sentence reads the same on every receiver that takes the same kind of argument, such as `Str`, `Bytes` and `ByteArray`.
- An unhashable key is left to CPython on purpose: that failure is about the key, and `cannot use 'list' as a dict key` is already in POOP's vocabulary.
- The regex rewording is the fragile half and is kept small. A rewording upstream degrades to the old behaviour rather than to a crash, and `tests/test_message.py` pins both shapes against real operations, so a Python upgrade that changes them fails loudly.
- A new POOP-authored message that names a banned construct fails the static sweep the day it is written.
- The sweep sends only wrong types, so a wrong value of the right type stays the patterns' blind spot; `a_fill` checks the length of a fill as well as its type for that reason.
- `test_every_wrapper_has_a_sweep_sample` walks the classes under `poop/types`, so the receiver list cannot fall behind the wrappers.
- The withheld-builtin `NameError` (ADR 40) goes through the same `poop_message` path.
