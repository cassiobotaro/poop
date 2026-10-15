# Proposal

## Why

The review of `poop/types/`, `poop/transformers/`, `poop/validators/` and
`tests/` found bodies written twice, a derived registry with one hand-kept
exception, docstrings that justify overrides the mixins already cover,
validator sentences in three registers, and a test suite that discovers
examples four times and drives the real REPL seventeen times by hand. None
of it changes what a program observes; all of it is one more place to keep
in step.

## What Changes

- **`_ExceptionRewriter` declares `names`**, so `RESERVED_NAMES` derives the
  mirror names the way `ellipsis.py` derives `Ellipsis`; the hand union and
  its twelve-line comment in `no_builtin_shadow.py` go.
- **One literal rewriter for `[…]`, `(…)` and `{…}`**: a `LiteralRewriter`
  in `_collection.py` with `literal_node`/`literal_target` class attributes
  replaces the three identical `visit_List`/`visit_Tuple`/`visit_Set`
  bodies, and `_LITERAL_KIND` is derived from the same declaration.
- **Three redundant overrides go**: `List.sorted` (byte-for-byte the
  mixin's), `Str.min`/`max` and `_MappingMixin.min`/`max` (the mixin's with
  the iterator spelled by hand); the `_minmax.py` paragraph that says `Str`
  and `Dict` do not inherit the iterable mixin is rewritten, and the
  `INFECTIONS.md` sentence that keeps `List`'s override goes.
- **Smaller type alignments**: `Boolean.__repr__` (a copy of `Object`'s)
  goes; `_endow` reads `_slots` off the alias like its two siblings, dropping
  a parameter and its `noqa`; `Try` and `With` spell single-use the same
  way; `_TrueClass`/`_FalseClass` drop the default `role="a block"` on four
  calls; `Bytes.fromhex` and `ByteArray.fromhex` share one helper; the
  orphaned `+` comment inside `ByteArray.iter` goes; `Int.max`/`min`,
  `Boolean.max`/`min` and the sequence `index` bounds are annotated as wide
  as they behave.
- **Validator vocabulary**: one class placeholder (`Klass`), `()` after
  every banned builtin name, one "no substitute" sentence across
  `no_breakpoint`/`no_exit`/`no_help`/`no_open`, `no_comprehension`'s four
  rows generated from one tail, and `dunder_message` naming a class-body
  `__slots__` correctly.
- **Tests**: `EXAMPLES_DIR`/`EXAMPLE_FILES` live in `tests/_support.py` and
  a parametrised test asserts every example's docstring carries a
  `Smalltalk` header (three spell it `Smalltalk (…):`, which the test admits
  by prefix); the slow import-recorder test is a module fixture plus one
  parametrised case per example; `tests/test_repl.py` uses its `repl`
  fixture everywhere and parametrises `_indent_for`/`_value_text`;
  `tests/test_cli.py` parametrises the three "clean diagnostic" cases.

Out of scope, and why: any change a program can observe — those are in
`fix-wrapper-equality-and-errors`; the eleven `*_iterator.py` files, a
deliberate one-class-per-file pattern the review found no better design
for; `visit_Dict`, whose rewriter also folds `**` merges and is not the
same shape.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — source-level refactor; `skip_specs: true`)

## Impact

- `poop/transformers/`: `exception.py`, `_collection.py`, `list.py`,
  `tuple.py`, `set.py`.
- `poop/validators/`: `no_builtin_shadow.py`, `no_comprehension.py`,
  `no_isinstance.py`, `no_issubclass.py`, `no_dunder_attribute.py`,
  `no_print.py`, `no_breakpoint.py`, `no_exit.py`, `no_help.py`,
  `no_open.py`.
- `poop/types/`: `list.py`, `string.py`, `_mapping.py`, `_minmax.py`,
  `boolean.py`, `_alias.py`, `try_.py`, `with_.py`, `bytes.py`,
  `byte_array.py`, `_bytes_like.py`, `int.py`, `_sequence.py`, `tuple.py`.
- `tests/`: `_support.py`, `test_pipeline.py`, `test_no_local_imports.py`,
  `test_doc_counts.py`, `test_validators/test_no_private_attribute.py`,
  `test_repl.py`, `test_cli.py`, the validator tests that pin the reworded
  sentences, `test_examples_docstring.py` (new).
- Docs: `INFECTIONS.md` (`List.sorted` sentence, reworded validator
  sentences where quoted), `README.md` ban list where a sentence is quoted.
