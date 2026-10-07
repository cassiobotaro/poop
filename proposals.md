# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Item 12 comes from a Pythonic-code review of the whole package and the test
suite, after the wording sweeps closed. It removes duplication or hand-rolled
spellings of things the stdlib or the codebase already has. Each was verified against the
code at the commit that opened it; counts are from `grep`.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 13. Once every
item has been implemented and deleted, numbering starts over at 1.

### 12. Small stdlib and consistency spellings, one commit each

- `_user_lineno` in `poop/executor.py` walks `tb_next` by hand; the loop is
  `traceback.walk_tb`, which yields `(frame, lineno)` and touches no source,
  so the docstring's `linecache` argument still holds.
- `encoding_name` in `poop/types/_codec.py` scans a dict of frozensets on
  every call; a reverse map built once at import answers in one lookup and
  reads as the question being asked.
- `getattr(value, "_value", value)` is spelled inline five times in
  `poop/types/_argument.py`, once in `_repeat.py` and once in `object.py`;
  `_unwrap._faithful` *is* that expression. Move `_faithful` to a leaf module
  so `_argument.py` can import it at the top instead of its four local
  imports of `_unwrap`.
- `false if X else true` where the sibling line writes `to_boolean(...)`:
  `object.py` (three sites) and `meta.py` (two); `has_attr` in `meta.py` and
  `block.py` write `to_boolean(False)` / `to_boolean(True)` for the constants
  `false` / `true`; `Slice.__eq__` is a three-branch `return true` /
  `return false` ladder that is one `to_boolean(isinstance(...) and all(...))`.
- `visit_AsyncFunctionDef` and `visit_ClassDef` duplicate `visit_FunctionDef`
  bodily in `no_decorator.py`, `no_class_machinery.py`,
  `no_free_functions.py` and `no_namespace_shadow.py`; `no_poop_prefix.py`
  already uses the idiom `visit_AsyncFunctionDef = visit_FunctionDef`.
- `Block._accepted` and `Block._keyword_message` in `poop/types/block.py`
  each read `signature(self._fn)` under the same `try` and filter the same
  positional kinds; one `_params()` helper and two `frozenset` kind constants.
- `try_.py` and `with_.py` write `def __repr__(self): return str(self)` where
  every other wrapper writes `__repr__ = __str__`; `frozen_set.py` keeps a
  `_frozenset = frozenset` alias whose comment names a shadowing that does not
  occur.
