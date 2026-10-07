# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 3–12 come from a Pythonic-code review of the whole package and the test
suite, after the wording sweeps closed. Item 3 changes behaviour a
program can observe; the rest remove duplication or hand-rolled spellings of
things the stdlib or the codebase already has. Each was verified against the
code at the commit that opened it; counts are from `grep`.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 13. Once every
item has been implemented and deleted, numbering starts over at 1.

### 3. `List.at` takes a slice; `Tuple.at`, `Range.at` and `Str.at` refuse one

`[1, 2, 3].at(slice(0, 2))` answers `[1, 2]`; `(1, 2, 3).at(slice(0, 2))`
answers `tuple.at expects an int index, got a slice`, and `range` and `str`
refuse the same way. `List.at` in `poop/types/list.py` special-cases
`isinstance(index, Slice)` before `at_index`; its siblings go straight to
`at_index`. Every one of the four already has a `slice` message, so the
special case is not the only spelling of the operation on any receiver.

**Fix.** Pick one answer for the family. Dropping the `List` special case is
the smaller change and leaves `slice` as the one message that slices; lifting
it into the sequence mixin of item 4 is the other. Either way the four
receivers agree, and a test pins them together. While there: `at_index`'s
refusal in `poop/types/_at.py` says `got a {type}` and so prints `got a int`,
where `List.at_put` one screen up uses `article(...)`.

### 4. `List` and `Tuple` spell thirteen methods twice

`len`, `__len__`, `slice`, `__add__`, `__mul__`, `__rmul__`, `__iter__`,
`includes`, `__contains__`, `sorted`, `reversed`, `count`, `index` and `print`
in `poop/types/list.py` and `poop/types/tuple.py` differ only in whether the
result is built with `List(...)` or `Tuple(...)`; `print` is byte-identical,
and `index` carries the same five-line comment in both files.

**Fix.** A `_SequenceMixin` holding `_items` and the `_rewrap(raw)` hook of
item 1, with the thirteen bodies written once. `List` keeps its mutators;
`Tuple` keeps `__hash__`. About ninety lines go, and the next `index`-style
fix lands in one place.

### 5. The `NotImplemented` tail is hand-written thirty-five times

```python
raw = _other_set(other)
if raw is None:
    return NotImplemented
return <op>(self._data, raw)
```

Sites: twelve each in `poop/types/dict_keys.py` and `poop/types/dict_items.py`
(eight set operators and four orderings per view), four in-place operators in
`poop/types/set.py`, five in `poop/types/_set_algebra.py`, two in
`poop/types/mapping_proxy.py`. The codebase already has the template twice —
`_SetAlgebraMixin._algebra(other, op)` and `_OrderedMixin._compare(other, op)`
in `poop/types/_ordered.py` — and only the four binary set operators use it.

**Fix.** `_compare` on `_SetAlgebraMixin` with `operator.le/lt/ge/gt`;
`_inplace` on `Set` with `operator.ior/iand/isub/ixor`; a `_SetLikeView` base
under the two dict views with one hook, `_own() -> set`, and generic
`_algebra`, `_reflected`, `_compare`, `isdisjoint` and `__eq__`. The
twenty-four view methods become one-liners, and the two spellings of `__eq__`
(`true if ... else false` in `DictKeys`, `to_boolean(...)` in `DictItems`)
become one.

### 6. The substring-search family is one body written fourteen times

`find`, `index`, `count`, `rfind` and `rindex` in `poop/types/string.py` and
again in `poop/types/_bytes_like.py` are each
`Int(self._value.<m>(a_needle(...), a_bound(start, ...), a_bound(end, ...)))`
with the selector repeated three times as a string; `startswith` and
`endswith` on both classes are the same shape over `affix_needle`.

**Fix.** A `_search(method, selector, sub, start, end)` helper per class,
taking the *bound* method (`self._value.find`) rather than a name to
`getattr`, so each public method is one line and stays an explicit `def` —
`ty`, `dir()` and `:methods` need the defs, as `boolean.py` records. The
bytes side also spells `true if ... else false` where `Str` spells
`to_boolean(...)`; `to_boolean` is already imported there.

### 7. Five `visit_Constant` and two `visit_UnaryOp` are the same literal fold

`poop/transformers/int.py`, `float.py`, `string.py`, `bytes.py` and
`complex.py` each define `visit_Constant` as "if the value is a `T`, wrap it
in a call to `_poop_t`"; `int.py` and `float.py` each define `visit_UnaryOp`
to fold `-5` into one literal, with identical comments. `int.py` spells
`isinstance(v, int) and not isinstance(v, bool)` twice.

**Fix.** Two ClassVars on `BuiltinRewriter` in `poop/transformers/base.py`,
`literal_type` and `literal_target`, and the two visitors written once.
`type(v) is self.literal_type` excludes `bool` for free. `complex.py` keeps
its `visit_BinOp` fold; `boolean.py`, `none.py` and `ellipsis.py` rewrite to
a *name*, not a call, and stay as they are.

### 8. `no_builtin_shadow` tabulates by hand the set the rewriters already know

`_BUILTIN_NAMES` in `poop/validators/no_builtin_shadow.py` lists twenty names.
They are exactly the `builtin` of the eighteen `BuiltinRewriter` subclasses,
plus the two spellings `ObjectTransformer` rewrites, plus `Ellipsis`. The
module's own comment argues that the *mirror* half must be "derived rather
than tabulated" so a new mirror cannot be added without the reservation
following it; the builtin half is tabulated, so a new rewriter is exactly
that hazard.

**Fix.** `names: ClassVar[frozenset[str]]` on `BuiltinRewriter`, defaulting to
`{builtin}`; `_ObjectRewriter` sets `{"object", "Object"}` and loses its
`is_builtin` override; `_EllipsisRewriter` gains `{"Ellipsis"}`. The validator
unions `cls.rewriter.names` over `_TRANSFORMER_CLASSES`.
`no_namespace_shadow.py` already imports from `poop.transformers`, so no new
cycle. A test asserting the derived set equals today's literal fails first and
is then deleted with the literal.

### 9. The `bytes` and `bytearray` converters are the same function

`_poop_bytes_from` in `poop/transformers/bytes.py` and `_poop_bytearray_from`
in `poop/transformers/byte_array.py` share the arity guard, the `codec =
args[1:]` split, the four-way `Str` / `Bytes` / `Int` / `Iterable` dispatch
and the final refusal; they differ in the wrapper, the hint literal and one
`._value` hop. `poop/transformers/_collection.py` already solves this shape
for the four collections with `make_iterable_from`.

Three converters — `enumerate.py`, `range.py`, `slice.py` — also call
`refuse_extra_arguments` and then, on `if not args`, raise a sentence that
retypes the same `built_from` and `hint` by hand.

**Fix.** A `make_bytes_from(wrapper, *, hint)` factory beside
`make_iterable_from`; the registry already cloaks factory-built functions, so
error messages keep their names. Give `refuse_extra_arguments` in
`poop/transformers/_arity.py` a `least=` bound that words the "got nothing"
case from the same `built_from` and `hint`, and drop the three hand copies.

### 10. `format_error` and `render_error` are hand-kept twins

Both functions in `poop/errors.py` compute the location, emit `poop:` plus the
message, the numbered gutter with the quoted line, and the optional caret
line. The docstring calls `render_error` the "twin"; a change to the layout is
made twice, and `tests/test_errors.py` and `tests/test_repl.py` test the two
layouts separately.

**Fix.** One `_error_segments(exc, source) -> list[tuple[str, str]]` yielding
`(text, style)` pairs. `format_error` joins the texts; `render_error`
assembles them, swapping the quoted-line segment for the syntax-highlighted
`Text`. The layout is stated once.

### 11. The test suite re-rolls what `conftest.py` and pytest already give

- `tests/conftest.py` defines `parse` and `assert_rejects` "to keep the ~60
  validator tests focused". Neither has a single user. Meanwhile
  `tests/test_validators/` holds 436 `ast.parse(` calls and 332 raw
  `pytest.raises(ValidationError)` blocks, and five files each define their
  own `_validate(src)`.
- Thirteen files in `tests/test_transformers/` define the same two-line
  `_transform(source)` helper, differing only in the transformer class.
- `tests/test_repl.py` installs a fake `builtins.input` in twelve tests and
  swaps `poop.repl._OUT` / `_ERR` eight times by hand; `tests/test_cli.py`
  builds the same `rich.Console` under another name and writes a file under
  `tmp_path` sixteen times.
- Seven test files each compute the repository root from `__file__`, and two
  duplicate the `("poop/types", "poop/transformers")` tuple the sweeps walk.
- Suite-wide, `assert "..." in str(exc_info.value)` appears 77 times against
  454 uses of `match=`. The reason is likely that `match` is `re.search` and
  needs `re.escape` around `()`; `tests/test_no_in.py` escapes by hand.

**Fix.** Either adopt `assert_rejects` across the validator tests or delete
both fixtures. Add `transform(transformer, source)`, `feed_input`,
`terminal_console`, `source_file`, `REPO_ROOT` and `SWEPT_PACKAGES` to
`conftest.py` and point the copies at them. Convert the `in str(...)` asserts
to `match=re.escape(...)`. Each bullet is its own commit.

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
