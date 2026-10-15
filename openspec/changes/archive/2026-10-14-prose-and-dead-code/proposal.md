# Proposal

## Why

The lazy-imports change (commit 772654b) moved 272 function-local imports to
the top of their modules and left the comments that explained the *method*
below them sitting above an import; two other rewrites left prose describing
a path that no longer exists. The same review found dead branches, aliases
that protect nothing, a dead type-ignore, an inert `@abstractmethod`, and a
handful of spellings that differ from their siblings for no reason. None of
it changes what a program observes.

## What Changes

- **Comments go back to what they describe**: `boolean.py:9-15` and `133`
  (`Boolean.format`, `_as_int`), `string.py:39-44` (`Str.format`),
  `byte_array.py:26-27` (`ByteArray.__add__`), `_minmax.py:16-23`,
  `_set_algebra.py:7`, `_dict_view.py:36` and `63-64`, `_mapping.py:11`
  (`_wrapping` builds an instance). The `_bytes_like.py:94-97`, `270-274`
  and `memory_view.py:88-90` comments describe the `a_needle`/`bytes_like`
  guard that runs, not the `getattr`-unwrap path that was removed, and
  `range.py`'s `includes` comment named the same removed path. The four
  sentences that place `__ne__` in `_NumericCompareMixin`
  (`_numeric_compare.py:52`, `int.py:321`, `float.py:212`, `boolean.py:121`)
  say it lives on `Object`.
- **Dead code goes**: the `Boolean` fold in `_repeat.py:37-38`
  (`Boolean.__index__` already folds); the `isinstance(other, Complex)`
  branch before the `(Int, Float)` test in `int.py:202` and `float.py:138`;
  `Range._iter` (one caller, `__iter__`); the two `# type: ignore[assignment]`
  on `__hash__ = None` in `mapping_proxy.py` and `_dict_view.py`; the
  `_complex`, `_bytearray` and `_memoryview` aliases in `complex.py`,
  `byte_array.py` and `memory_view.py`.
- **Spellings align with their siblings**: `_iterable_mixin.py`'s seven
  runtime imports move above the `TYPE_CHECKING` block; its
  `@abstractmethod` on `__iter__` becomes `raise NotImplementedError` like
  every other hook in the family (`PoopMeta` is not `ABCMeta`, so it was
  inert); `boolean.py` imports `MISSING` from `_sentinel` and drops the
  `bool()` inside `to_boolean(...)` in `from_bytes`; `_codec._refusal` is
  typed `UnicodeEncodeError | UnicodeDecodeError` and reads `.start` and
  `.object` directly; `Float.__init__` normalises with `float(...)` so a
  wrapper never holds a raw `int` (`hex` keeps its own `float(...)`, for the
  checker: a `float` annotation admits `int`); the private `Sentinel` enum in
  `_sentinel.py` is renamed (`_Marker`) so it stops sharing a name with the
  user-facing `Sentinel` in `sentinel.py`.
- **Core modules**: `_registry.py` imports `Counter`, `chain`, `iskeyword`
  and `FunctionType` under their own names (the module docstring's reason
  for aliasing covers `dict`/`list`/`object` only); `cli._read_source` uses
  two `except` clauses instead of an `isinstance` inside one;
  `repl._value_text` is a `match` over class patterns; the module-level
  `for` loops in `meta.py` and `exceptions.py` that install operators and
  refusals move into a function so `_dunder`, `_name`, `_native` are not
  module globals; `withheld_builtin` tests membership instead of `is None`.

Out of scope, and why: anything a program can observe (`fix-behaviour-leaks`)
and any helper extraction (`share-type-helpers`,
`trim-transformers-validators`); the long docstrings themselves, which are
the house style; `Boolean`'s thirty hand-written int messages, which the
file explains a loop would hide from `ty`, `dir()` and `:methods`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — comments, dead code and spellings; `skip_specs: true`)

## Impact

- `poop/types/`: `boolean.py`, `string.py`, `byte_array.py`, `_minmax.py`,
  `_set_algebra.py`, `_dict_view.py`, `_mapping.py`, `_bytes_like.py`,
  `memory_view.py`, `_numeric_compare.py`, `int.py`, `float.py`,
  `_repeat.py`, `range.py`, `mapping_proxy.py`, `complex.py`,
  `_iterable_mixin.py`, `_codec.py`, `_sentinel.py`, `meta.py`,
  `exceptions.py`, `_message.py`.
- `poop/transformers/_registry.py`, `poop/cli.py`, `poop/repl.py`.
- Tests: `tests/test_types/test_float.py` (a `Float(1)` holds `1.0`);
  `tests/test_transformers/test_range.py` (iterates a `Range` instead of
  calling `_iter`); `tests/test_types/test_sentinel.py` (imports `_Marker`);
  `tests/test_cli.py` and `tests/test_repl.py` must pass unchanged.
- Docs: `CONTRIBUTING.md` if it names `Sentinel` from `_sentinel.py`;
  otherwise none.
