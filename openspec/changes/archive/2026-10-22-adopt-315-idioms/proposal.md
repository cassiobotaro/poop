# Proposal

## Why

POOP requires Python 3.15 and already wraps its user-facing additions
(`sentinel`, `frozendict`, `take_bytes`, the `math.integer` six, the
foreign-language hints). Three of 3.15's own idioms are still written the
3.14 way in the interpreter's source: flattening goes through
`itertools.chain` and nested `for` clauses where PEP 798 writes `[*xs for xs
in lists]`, the internal "argument not given" markers are an `Enum` built to
imitate what PEP 661's `sentinel` builtin now gives natively (identity,
narrowing in `ty`, a named repr), and seven anchored regex calls use
`re.match`, soft-deprecated in 3.15 for `prefixmatch`. None of it changes
what a program observes; all of it is the language's source not speaking the
dialect it requires.

## What Changes

- **Unpacking in comprehensions (PEP 798)** replaces `chain.from_iterable`
  and the nested `for` at six sites: `_registry.py` (`Counter(*src for src
  in sources)`, `{**src for src in sources}`, `frozenset(*names for cls in
  ...)`), `dict.py` (`[*pair for pair in pairs]`, twice), `repl.py` and
  `_alias.py` (one nested `for` each). The `chain` import leaves `dict.py`
  and `_registry.py`.
- **`_sentinel.py` is built on the `sentinel` builtin.** The `_Marker` enum
  and its five `type X = Literal[...]` aliases go; the five markers become
  `MISSING = sentinel("MISSING")` and so on, and a signature reads `block:
  Block | MISSING = MISSING`, which `ty` 0.0.87 narrows to `MISSING` on the
  `is` branch and to `Block` after it (verified). The module docstring is
  rewritten, and the `INFECTIONS.md` sentence that says the internal module
  "predates the builtin and is unrelated" is corrected.
- **`prefixmatch` for `re.match`** on the seven compiled-pattern calls in
  `poop/types/_message.py` and `poop/types/string.py`.

Out of scope, and why: anything a program can observe — the markers never
reach user code, and the comprehension and regex rewrites are byte-for-byte
in behaviour; the `Sentinel` wrapper type (`poop/types/sentinel.py`), which
already mirrors the builtin; `Float`'s new `math` predicates, which are a
language decision and live in `float-answers-315-math`; 3.15 additions with
no site in this code base (`inspect.getdoc` keywords, `ast.dump(color=)`,
`compile(module=)`, `typing.disjoint_base`), checked and left alone.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — source-level refactor; `skip_specs: true`)

## Impact

- `poop/transformers/`: `_registry.py`, `dict.py`.
- `poop/repl.py`, `poop/types/_alias.py`.
- `poop/types/_sentinel.py` and its 22 importers under `poop/types/`
  (`_numeric_compare`, `_repeat`, `none`, `meta`, `int`, `_bytes_like`,
  `float`, `_minmax`, `_iterator_base`, `block`, `try_`, `dict`, `complex`,
  `_argument`, `_iterable_mixin`, `object`, `boolean`, `list`, `with_`,
  `string`, `_sequence`, `_peek`): the annotation names `Missing`,
  `Unpeeked`, `NotACount`, `NotNumeric`, `NotIntegral` become the markers
  themselves.
- `poop/types/_message.py`, `poop/types/string.py`: the regex calls.
- Docs: `INFECTIONS.md` (the `sentinel` paragraph's last sentence).
- Tests: none change behaviour; `tests/test_types/` runs as the regression
  net, and `uv run ty check` is the proof for the sentinel rewrite.
