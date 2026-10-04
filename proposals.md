# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Item 1 comes from probing the operators after the argument guards closed the
same sentence on the message side.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 2. Once every
item has been implemented and deleted, numbering starts over at 1.

### 1. Seventeen operator sites still answer `'int' object is not iterable`

`a_collection` words a scalar handed where a collection was expected, for every
*message* that takes one. The same mistake written as an *operator* still
reaches CPython, on two receivers:

- **The set operators of `DictKeys` and `DictItems` — 16 sites.** `|`, `&`,
  `-` and `^`, each in both directions: `{"a": 1}.keys() | 5` and
  `5 | {"a": 1}.keys()`. `_elements` in `poop/types/_dict_view.py` calls
  `set(other)` unguarded.
- **`List.__iadd__` — 1 site.** `xs += 5` hands the operand straight to
  `list.extend`.

Every other receiver already answers the operator shape — `{1} | 5` says `set
does not understand #| with an int`, and so does `xs |= 5` on a `Set`.

The wording sweep cannot see either. The operator test in
`tests/test_no_python_wording.py` pairs `_OPERANDS`, which holds no dict view,
and the only augmented assignment anywhere in the file is the one `*=` line in
`_FAILING`; the wrong-argument sweep sends messages, not operators, and has no
dict view among its receivers.

**Fix.** Not `a_collection`: an operator refusal is `binary_refusal`'s
sentence, and it is reached by answering `NotImplemented`. The view operators
return `NotImplemented` for an operand that is not a collection, as the
comparisons beside them already do for one that is not set-like; `__iadd__`
does the same, so `xs += 5` reads `list does not understand #+= with an int`.
Add a dict view to `_OPERANDS` and sweep the augmented operators over the same
pairs, so the test fails first.
