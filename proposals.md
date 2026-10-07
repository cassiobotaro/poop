# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 1–16 come from a second Pythonic-code review of the package and the test
suite, opened once the first twelve closed. The first three change behaviour a
program can observe; the rest remove duplication, hand-rolled dispatch or
spellings of things the stdlib or the codebase already has. Each was verified
against the code at the commit that opened it: the leaks were reproduced with
`poop`, the counts are from `grep`.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 17. Once every
item has been implemented and deleted, numbering starts over at 1.

### 14. The transformers spell stdlib shapes by hand

- `_DictRewriter._fold_parts` in `poop/transformers/dict.py` is a run-length
  state machine over "splat or not" with a `pending` list it flushes — the
  `itertools.groupby(entries, key=lambda kv: kv[0] is None)` fold, where a
  splat run extends `parts` and a pair run becomes one
  `_pairs_call(list(chain.from_iterable(run)))`. Verified on a mixed entry list
  to produce the same parts in the same order. `visit_Dict`'s `flat` loop is
  `chain.from_iterable(zip(node.keys, node.values, strict=True))`. `visit_Call`
  there tests `node.func.id == self.builtin` instead of the `is_builtin` hook
  every other rewriter uses.
- `VarargsTransformer` in `poop/transformers/varargs.py` builds an
  `ast.arguments` with six empty fields and an `ast.Call` with
  `keywords=[]`; since 3.13 every list field defaults to `[]` and every
  optional one to `None`, and the project targets 3.14 only. `_variadics` is a
  filter loop a comprehension writes.
- `_poop_memoryview_from` in `poop/transformers/memory_view.py` has two
  consecutive `if isinstance(arg, X): return MemoryView(memoryview(arg._value))`
  with identical bodies (ruff's SIM114 merges only `if`/`elif`).
- `_merge_bindings` in `poop/transformers/_registry.py` finds duplicates by
  incremental `keys() & keys()`; a `Counter` over every key reports all
  duplicates at once with the same message.
- The `int` / `float` / `complex` converters and `_spelling` in
  `poop/validators/no_decorator.py` are four-to-six-rung `isinstance` ladders;
  `base.py`'s literal fold already uses `match`, and class patterns read as
  the type table they are. `ComplexTransformer`'s literal join
  (`isinstance(node.op, ...) and isinstance(node.left, ...) and ...`, five
  clauses) is one `case ast.BinOp(left=ast.Constant(value=int() | float() as
  real), op=ast.Add() | ast.Sub() as op, right=ast.Constant(value=complex()
  as imag))`.

**Fix.** As listed, one commit per bullet. Rewrites only; the transformer
tests cover every branch.

### 15. Dead and doubled bits worth a sweep

- `_opt_int` in `poop/types/_unwrap.py` has no caller in `poop/` or `tests/`
  (one test comment mentions it); ruff does not flag unused module-level
  functions.
- `PoopMeta.__ne__` restates `__eq__` with `is not`, while `Object.__ne__`
  documents itself as "the one `__ne__`" precisely so no rule is kept in two
  copies; `to_boolean(not bool(cls == other))` keeps the rule in `__eq__`.
- `refuse.__name__ = name; refuse.__qualname__ = name` in
  `poop/types/exceptions.py` is dead: the loop below calls `__set_name__`,
  whose `cloak_callable` sets both again; that loop also re-reads
  `vars(PoopExcMeta)[_name]` for the object it just built.
- The `is a value — it holds no state of its own` sentence is spelt twice in
  `poop/types/object.py` (`__setattr__`, `del_attr`); the `_attr_guard`
  docstring already warns about drift in this family.
- `_PROTOCOL_SLOTS` in `meta.py` carries a middle column equal to
  `native.__name__` on every row. `superclass` builds a list of bases to read
  its head: `next((b for b in cls.__bases__ if isinstance(b, PoopMeta)), None)`.
- `_MethodBlock`'s `MessageNotUnderstood(explain-style prefix, name=, obj=)`
  is composed by hand at five sites across `meta.py`, `exceptions.py` and
  `error.py`; one `does_not_understand(label, name, hint)` in `_selectors.py`
  next to `explain` would spell the prefix once.
- `_display_width` in `poop/errors.py` nests a two-level conditional inside
  `sum`; a `_column_width(char)` with three early returns (or a `match` on
  `east_asian_width`) is the rule the docstring spends a paragraph on, and
  `sum(map(_column_width, text))` is the fold.
- `Slice.__eq__` compares three fields through a `_field_eq` `None` dance
  while `__hash__` already hashes the tuple; tuple equality answers the same.
  `Range._iter` is a `for`/`yield` where `_bytes_like` and `memory_view` write
  `map(Int, ...)`, and `Str.__iter__` could be `map(Str, self._value)`.
  `Zip` stores `_strict` as a `Boolean` only to read it back with `bool(...)`.
  `Dict.setdefault` takes `default: Object | None = None` and translates
  `None` to `none`, where the sibling `get` simply defaults to `none`.
- `poop/repl.py`: the completer's `_name_matches` and `_attr_matches` are
  append loops sharing a `"(" if callable(val) else ""` suffix rule, the
  second inside a `try` that wraps the whole `dir()` loop though only `eval`
  can fail, and `text.rfind(".")` plus two slices is `text.rpartition(".")`.
  `_meta` rebuilds its dispatch dict, with a `lambda`, on every meta-command;
  a `_meta_help` method and `getattr(self, f"_meta_{cmd}", None)` guarded by
  `cmd.isidentifier()` is name-based dispatch.
- `execute(..., interactive: bool)` in `poop/executor.py` is a boolean switch
  for what `compile` already names: `mode: Literal["exec", "single"]`, with the
  `ast.Interactive` wrap and the `SyntaxError → ExecutionError` conversion in
  one `_compile` helper.
- `_alias.py` writes the slot-copy loop twice (`_fill` and inline in
  `builtin_alias.__init__`), recomputes `_payload_slots(wrapped)` on every
  construction though `wrapped` is fixed when the alias is built, and tells the
  `__new__`-step story in `_endow`'s docstring and again in `__call__`.

**Fix.** One commit per bullet; none changes wording or behaviour.

### 16. The suite asserts AST shape by hand and copies the call-name contract thirty-eight times

- `tests/test_transformers/` has forty-one `isinstance(call.func, ast.Name)` …
  `call.func.id == "_poop_int"` chains, each four to six asserts that check
  part of the tree, and only four files use `ast.unparse`. `ast.unparse` of the
  transformed module says it exactly in one line: `x = _poop_int(42)`,
  `_poop_int_from('42')`. A `rewritten(transformer, source) -> str` next to
  the `transform` helper in `tests/_support.py` makes each test one assert,
  and the three-case tests `parametrize` cleanly; the "is not rewritten" tests
  become `rewritten(...) == source`. The `isinstance` narrowing was only there
  for `ty`, which `unparse` removes the need for. The four `BINDINGS[...] is`
  identity tests stay.
- Thirty-eight validators are `CallNameValidator` subclasses with two class
  attributes, and their seventy test modules repeat the same contract: sixty
  `test_valid_code_passes` over `x = 1 + 2`, sixty-two `*_carries_line_number`,
  the `method named X is not blocked` and `bare name is reserved` cases.
  `test_no_hash.py`, `test_no_len.py` and `test_no_abs.py` are byte-identical
  modulo the name. One `tests/test_validators/test_call_name.py` parametrised
  over `[(v, name) for v in DEFAULT_VALIDATORS if isinstance(v,
  CallNameValidator) for name in v.forbidden]` states the contract once and
  cannot forget a new validator; a suite-wide `test_plain_code_passes` over
  `DEFAULT_VALIDATORS` replaces the sixty copies. Each per-validator file keeps
  only what is specific — the substitute wording. CONTRIBUTING's "tests live
  next to their target" gets a line saying the mechanical contract lives in
  the shared module.
- Hygiene in the same sweep: unused `capsys` / `monkeypatch` parameters in
  `tests/test_repl.py` (ruff `ARG` is off); `tmp_path: object` then
  `Path(str(tmp_path))` twice there; both `import pathlib` and `from pathlib
  import Path` in one file; `_repl()` returning `(repl, repl._ns)` thirty-three
  times, mostly unpacked as `repl, _` — a `repl` fixture; one test in
  `tests/test_cli.py` writing `syntax.py` by hand beside the `source_file`
  fixture that does it, and two identical `subprocess.run([sys.executable,
  "main.py", ...])` blocks.

**Fix.** The `rewritten` helper and a file-by-file conversion; the parametrised
call-name module; the hygiene bullets as one commit. No behaviour is touched.

---

Considered and not proposed, so the next review does not re-open them:
subclassing `code.InteractiveConsole` wholesale (the REPL writes banner and
prompts to stderr and names each input `<repl-N>`, which it does not offer);
moving the per-class `max`/`min` and set messages into their mixins (the
mixins are cloaked `object`, and the rule that a wrong-arity error names the
receiver is stated in `_set_algebra.py` and `_sequence.py`); deriving the
three `BINDINGS` entries of the sixteen constructor transformers from
`rewriter.builtin` (the keys are not uniform — `_poop_range` is a converter,
`Boolean` binds as `_poop_boolean`, `complex` adds a literal binding — and
twenty test files name them, so it is a rename with scope to confirm first);
`isinstance(raw, SupportsIndex)` for `hasattr(raw, "__index__")` (slower, and
the current test is CPython's exact rule); `zip(strict=True)` under `Zip` (a
`ValueError` from a user block would be indistinguishable from the mismatch).
