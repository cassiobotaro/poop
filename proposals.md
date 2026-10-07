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

### 4. The CLI writes each stream through two unrelated paths

`poop/console.py` exists so colour is decided per destination, and the REPL's
`_say` was added because it had "two paths to one stream". `main` in
`poop/cli.py` still has the split: `PoopError`s and the coloured AST dump go
through `report(..., ERR)` and `OUT.print`, while the two read failures,
`No validation errors.` and the plain dump go through `typer.echo`. A
`NO_COLOR`/pipe decision is made by rich for one line and by click for the next.

The two `except` branches around `read_text` differ only in
`exc.strerror`/`exc.reason`, and `main` does four jobs: read, validate-only,
transform-only, run.

**Fix.** Route everything through the two consoles — `ERR.print(..., markup=False,
highlight=False)` for the read failures, `OUT.print` for the rest — and the
`in_colour(OUT)` branch becomes one `OUT.print(Syntax(...) if in_colour(OUT)
else code)`. A `_read_source(file) -> str` owns the two `except`s. `Console()`
resolves `sys.stdout` lazily, so `CliRunner` captures it exactly as it already
captures `report(..., ERR)` in `tests/test_cli.py`. While there,
`--validators-only --transformers-only` together silently runs the first;
one `typer.BadParameter` says so.

### 5. Two validators re-implement `NodeVisitor` dispatch by hand

`_Visitor` in `poop/validators/no_namespace_shadow.py` (shared by
`no_builtin_shadow`) carries a recursive `_visit_target` over `Name` / `Tuple`
/ `List` / `Starred`, three `visit_*Assign` methods that call it, a
`_check_args` over `iter_params(args)` and a `visit_Lambda` — all to find
`Name` nodes in `Store` context and `arg` nodes. `no_poop_prefix.py` repeats
the parameter half. The class *is* an `ast.NodeVisitor`: `generic_visit`
already recurses into the unpacking forms and into `arguments`, and the two
hooks that name those nodes are

```python
def visit_Name(self, node: ast.Name) -> None:
    if isinstance(node.ctx, ast.Store):
        self._check(node.id, node)

def visit_arg(self, node: ast.arg) -> None:
    self._check(node.arg, node)
```

Verified: `visit_arg` sees every parameter of `def f(a, /, b, *c, d, **e)` and
of `lambda p, *q, **r`. Error positions are unchanged (both report at the
`Name` / `arg`). The one widening: `for Try in xs` and `with ... as Try`
targets are `Store` names, so the shadow validators now also report them, on
top of `no_loops` / `no_with` — consistent with every validator collecting.

Two more walkers in the same family: `_collect_starred` in
`poop/transformers/unpack.py` is an accumulator-by-mutation recursion that
`ast.walk` with a `Starred`-in-`Store` filter writes as one comprehension, and
`_ClassNames` in `poop/validators/no_private_attribute.py` is a whole visitor
class whose job is `{n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}`.

**Fix.** The two hooks above; `_visit_target`, the three `visit_*Assign`,
`_check_args`, `visit_Lambda` and `iter_params` (then without callers) go.
`ast.walk` for the other two. No existing test flips.

### 6. `Int` and `Float` re-dispatch a raw result that `to_poop` already dispatches

`to_poop` in `poop/types/_bridge.py` is a `singledispatch` from `int` / `float`
/ `complex` to `Int` / `Float` / `Complex`. Five sites re-implement it by hand:
`Int.__pow__` (`isinstance(result, complex)` → `Complex`, `float` → `Float`,
else `Int`), `Float.__pow__` (the same minus the `Int` arm), `Float.__round__`
(`Int(result) if isinstance(result, int) else Float(result)`), `Int._arith`
(`Float(...)` if the other is a `Float`, else `Int(...)`), and
`Int.__truediv__`, a copy of `_arith` that hard-codes `Float` and so is the one
arithmetic operator that does not go through it.

**Fix.** `_arith` returns `to_poop(op(self._value, other._value))`, with
`to_poop` imported locally the way `string.py` imports `to_python`;
`__truediv__` becomes `self._arith(other, operator.truediv)`; the two `__pow__`
and `__round__` return `to_poop(...)`. Arithmetic never yields a raw `bool`,
so the `bool` registration cannot be hit. The modulus branch of `Int.__pow__`
is untouched.

### 7. `Map` and `Filter` are one class written twice

`poop/types/map.py` and `poop/types/filter.py` differ in two lines out of
forty: the class name and `yield value` versus `if bool(value): yield item`.
The `__slots__`, `__init__`, `_generate`, the fifteen-line PEP 479 comment and
the `try/except StopIteration` around the block call are byte-identical.

One level up, `_IteratorBase` and `_LazyView` in `poop/types/_iterator_base.py`
restate `__init_subclass__`, `__iter__`, `iter`, `__str__` and `__repr__`; the
`_LazyView` docstring itself says "the same `__iter__`, `iter`, `<name>` repr
and cloak".

**Fix.** A `_BlockView(_LazyView)` holding the slots, the constructor, the
guarded `_call(block, item)` with the PEP 479 comment once, and a `_generate`
that hands `(source, block)` to a per-class `_gen`; `Map._gen` is one
generator expression and `Filter._gen` the other. A `_Cursor` base under
`_IteratorBase` and `_LazyView` holds the five shared members, leaving
`_IteratorBase` with `__init__`, `_materialize` and the `_iterating` slot the
lazy views must not have (`_peek.py` says why). Both bases cloaked `object`
like the other mixins; `class_name()` answers are unchanged.

### 8. `_PeekMixin` spells the pull-and-reword `try` three times

`has_next`, `next` and `__next__` in `poop/types/_peek.py` each wrap
`next(self._materialize())` in the same `except RuntimeError as exc: raise
reword_if_native(exc, self._iterating) from None`, with the `dictionary
changed size during iteration` story told three times in comments, and `next`
and `__next__` open with the same buffered-value prologue.

**Fix.** One `_pull(self) -> Any` with the `try` and the comment; the three
messages call it. `StopIteration` is not a `RuntimeError`, so the catch order
is preserved and `next`'s `default` / `_exhausted` branch sits on top of
`_pull` unchanged.

### 9. `a_bound` and `max_split` are `an_int` with a default

`a_bound(value, selector, role)` in `poop/types/_argument.py` unwraps,
accepts `None` or an `__index__`, and raises `#{selector}'s {role} must be an
int, got ...`; `an_int(value, selector, role, default)` does the same with the
absent case named. `max_split` is `a_bound` with `"maxsplit"` and `-1` for
`None`. Verified by script that `a_bound(v, s, r) == an_int(v, s, r,
default=None)` and `max_split(v, s) == an_int(v, s, "maxsplit", default=-1)`
on `None`, `none`, `Int(3)`, `Int(0)`, and that the refusal text is identical
for `Str("x")` and `1.5`. Fourteen `a_bound` and twenty-five `an_int` call
sites.

Same family, lower value: `a_collection` and `a_pair` are the identical
`isinstance(value, Iterable)` guard with a different sentence, and
`bytes_like(..., optional=True)` is a boolean flag whose only job is an
`_is_absent` short-circuit the strip family could spell as `a_fill` does.

**Fix.** `a_bound` and `max_split` become one-line calls to `an_int` (their
docstrings stay). The messages are byte-identical, so `test_str.py`,
`test_bytes.py` and `test_byte_array.py` keep passing.

### 10. The metaclass MRO is scanned for a `class_side` four times, once redundantly

`_read_refusal` and `PoopMeta.__dir__` in `poop/types/meta.py`,
`PoopMeta.__setattr__`'s `owned = any(...)`, and `_answered_by_the_class_side`
in `poop/types/error.py` each walk `type(cls).__mro__` reading
`vars(klass).get(name)` for a `class_side`. In `__setattr__` the
`_read_refusal(...) is None` precheck is dead: `class_side_read_refusal`
subclasses `class_side`, so whenever it is non-`None` `owned` is already true
and `_reject_builtin` is skipped either way.

**Fix.** One `_class_side_named(metacls, name) -> class_side | None` in
`meta.py` — `next((attr for m in metacls.__mro__ if isinstance(attr :=
vars(m).get(name), class_side)), None)` — that `_read_refusal`, `__setattr__`
and `error.py` call; the precheck goes. `test_meta.py`'s read-refusal tests
stay green.

### 11. The scalars wire their operators the long way round

- `__rand__`, `__ror__`, `__rxor__` on `Int` and `__radd__`, `__rmul__` on
  `Complex` go through `_bitwise(..., reflected=True)` / `_arith(...,
  reflected=True)`, though `&`, `|`, `^`, `+`, `*` commute. The codebase's own
  idiom is `__rmul__ = __mul__` (`_sequence.py`, `string.py`,
  `_bytes_like.py`). Only the two shifts and `-`, `/`, `**` on `Complex` need
  the swapped form.
- `abs`, `ceil`, `floor`, `trunc`, `round` on `Int` and `Float` are written
  as `def abs(self): return self.__abs__()` — the message calling the dunder,
  the opposite of `Complex.__neg__ = ... self.negated()` and of CONTRIBUTING's
  "wire dunders to public methods". Ten two-line pairs become `__abs__ = abs`
  one-liners, the way `__repr__ = __str__` already reads; the qualname a
  wrong-arity call reports stays `int.abs`. `Int.__ceil__`, `__floor__` and
  `__trunc__` are three copies of `return self`.
- `Complex._coerce` is the `Int | Float | Boolean` chain of
  `_numeric_compare._num_value` with a `None` sentinel where the rest of the
  tower uses `NOT_NUMERIC`; `_numeric_compare` has no top-level POOP imports,
  so `complex.py` can call it.

**Fix.** Aliases for the commutative reflections; message once, dunder
aliased, for the five unary pairs; `_coerce` through `_num_value`. No wording
changes.

### 12. `_IterableMixin` hand-rolls `find`, `sum`, `all` and `any`

`find` is a `for`/`if`/`return` with a `none` tail — `next((item for item in
... if block(item)), none)`. `sum` spells the empty case as a `try/except
StopIteration` around `next(items)` — `next(items, Int(0))` — and folds with
`lambda a, b: a + b` — `operator.add`. `all` and `any` wrap each answer in
`bool(...)` inside `builtins.all` / `builtins.any`, which truth-test their
elements themselves; `Boolean.__bool__` is what makes that work, and `find`'s
`if bool(block(item))` is the same redundancy. `builtins.sum` stays avoided for
the `__radd__` reason CLAUDE.md records.

**Fix.** The four spellings above; `all`/`any` become
`to_boolean(builtins.all(map(block, self._iter_items())))`. Semantics are
identical and the existing tests cover all four.

### 13. Wrappers are rebuilt from a raw payload the long way round

- `Dict.fromkeys` in `poop/types/dict.py` is a `for` loop over `d._data[k] =
  fill`; `dict.fromkeys` is the builtin it mirrors. `Dict.copy` builds an
  empty `Dict` and assigns `_data`; `Dict.__or__` does `merged =
  self.copy(); merged._data.update(other._data)` — the pre-3.9 spelling of
  `self._data | other._data`; `_merged` in `poop/types/mapping_proxy.py` does
  the same with a `reflected: bool` whose only job is to swap two names. A
  `Dict._wrapping(data)` classmethod makes all four one-liners and dissolves
  `_merged`.
- `Range.slice` and `Range.reversed` in `poop/types/range.py` both re-encode a
  native `range` with the same three lines (`sign = 1 if r.step > 0 else -1;
  Range(Int(r.start), Int(r.stop - sign), Int(r.step))`) — the inverse of
  `_range()`. A `Range._from_native(r)` is the missing half of that pair.
- `__reversed__` and `reversed` are identical bodies on `DictKeys`,
  `DictValues`, `DictItems` and `MappingProxy`; `__reversed__` written once on
  `_DictView` as `return self.reversed()` wires the dunder to the message.
  `includes` re-spells `__contains__` on seven receivers (`DictKeys`,
  `DictValues`, `Dict`, `List`, `Tuple`, `Set`, `FrozenSet`) as
  `to_boolean(x in self._payload)` beside `x in self._payload`;
  `DictItems.includes` already reads `to_boolean(pair in self)` with a comment
  saying why. `Str`, `Bytes` and `MemoryView` are not candidates: their
  `includes` guards the argument and their `__contains__` does not.

**Fix.** As listed. Purely structural; no test changes.

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
