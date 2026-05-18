# Proposals

Findings from a code-audit pass over `poop/types/`. Each entry has a
location, the underlying problem, and a proposed fix. Grouped by category.

## Raw Python objects leaking through POOP surface

Public POOP surface should never hand a raw CPython object back to user code —
arithmetic, properties, and library wrappers must wrap their results in the
matching `_poop_*` type.

### 1. `sys` info structs returned raw — `poop/types/sys.py:137-166`

`Sys.implementation`, `Sys.flags`, `Sys.float_info`, `Sys.int_info`,
`Sys.hash_info`, and `Sys.thread_info` all `return _sys.<attr>` directly, so
`sys flags` hands back CPython's `sys.flags` namedtuple with raw `int` fields.

**Fix:** wrap each as a small POOP shim (mirroring the `StructTime` pattern
already in `poop/types/time.py`) exposing every field as `Int`/`Boolean`/`Str`.

### 2. `sys.modules` exposes raw module objects — `poop/types/sys.py:28-32`

`_modules_dict` stores `Str(k) → v` where `v` is the raw Python module object
(note the existing `# type: ignore`). `sys modules at: 'os'` returns
`<module 'os'>` whose `class` is the bare Python `module` type.

**Fix:** either drop module values (replace with a `ModuleStub` carrying `name`
and `file` as POOP strings) or restrict the view to keys only.

### 3. Default `decimal` contexts are raw — `poop/types/decimal.py:236-238`

`Decimal_.BasicContext`, `ExtendedContext`, and `DefaultContext` are bound as
`ClassVar[Any] = _decimal.<Context>`, so the user touches a raw
`_decimal.Context` (and any attribute access leaks plain Python `int`s).

**Fix:** wrap at class-definition time, e.g.
`BasicContext: ClassVar[Context] = Context(_decimal.BasicContext)`.

### 4. `subprocess.CompletedProcess.args` raw — `poop/types/subprocess.py:53-55`

The `args` property returns `self._impl.args` unwrapped, so callers see a raw
`list[str]` (or `str`) after `subprocess.run(...)`.

**Fix:** wrap by branch, mirroring the existing `stdout`/`stderr` logic:
`List(*[Str(a) for a in ...])` when sequence, `Str(...)` when scalar.

### 5. `logging.LogRecord.msg/args` raw — `poop/types/logging.py:38-43`

Both properties return whatever the user originally passed to the logger,
unwrapped. Inside a POOP `Formatter`/`Filter` block, `record msg class` shows
`str` instead of `Str`.

**Fix:** route through `to_poop(...)` from `poop/types/_bridge.py`.

### 6. `asyncio.Future` and `concurrent.CFFuture` leak coroutine results — `poop/types/asyncio.py:39-43`, `poop/types/concurrent.py:25-30`

`Future.result()` / `Future.exception()` (and the `concurrent` equivalents)
return `self._impl.result()` / `self._impl.exception()` raw, so any awaited
value comes back as a plain Python object.

**Fix:** wrap with `to_poop(self._impl.result())` (and the exception path).

### 7. `asyncio.new_event_loop()` returns raw loop — `poop/types/asyncio.py:122-128`

`AsyncIO.new_event_loop()` hands back `_asyncio.new_event_loop()` directly.

**Fix:** introduce an `EventLoop(Object)` shim, or drop the entry point (the
module's docstring already notes that event-loop construction is out of scope
for v1).

### 8. `codecs.CodecInfo` exposes raw encoder/decoder classes — `poop/types/codecs.py:56-62`

`CodecInfo.incrementalencoder` and `incrementaldecoder` return the raw Python
encoder/decoder classes, so instantiating them yields raw `bytes`/`str`.

**Fix:** wrap into POOP `IncrementalEncoder`/`IncrementalDecoder` shims, or
remove these properties (the docstring already labels incremental codec
construction as out of scope).

### 9. `signal.signal()` / `signal.getsignal()` leak previous handler — `poop/types/signal.py:100-105`

Both return the previous handler unwrapped — could be a Python function, a
`signal.Handlers` enum value, or an `int`.

**Fix:** pipe through `to_poop(...)` (covers the integer case and passes
callables through).

### 10. `csv.Sniffer.sniff()` returns raw `_csv.Dialect` — `poop/types/csv.py:240-242`

Reading `delimiter`/`quotechar` on the result yields raw `str`.

**Fix:** introduce a POOP `Dialect` shim exposing `delimiter`, `quotechar`,
`lineterminator`, `doublequote`, `skipinitialspace`, `quoting` as POOP types,
or return a POOP `Dict` of those fields.

### 11. `dict_items._own_set()` is callable from POOP — `poop/types/dict_items.py:80-81`

Returns a raw Python `set`. Intended as an internal helper for `__or__` /
`__and__` / etc., but lacks the `_poop_` mangle and is reachable from user
code.

**Fix:** rename to `_poop_own_set` (or inline into each binop and drop the
helper).

## Method-signature inconsistencies

POOP public surface annotates POOP types — never Python primitives. Findings
below diverge from that contract.

### 12. `List.sort(reverse: bool = False)` uses primitive — `poop/types/list.py:131-133`

Only place in a central type where `reverse` is `bool` instead of `Boolean`.
`subprocess.run`, `socket.create_server`, `json.dumps` already use
`Boolean = false`.

**Fix:** `reverse: Boolean = false` (import `false` from `boolean`).

### 13. `Set` set-ops accept `object → Any`; `FrozenSet` accepts `FrozenSet → FrozenSet` — `poop/types/set.py:104-122` vs `poop/types/frozen_set.py:66-76`

```python
# set.py
def __and__(self, other: object) -> Any: ...
# frozen_set.py
def __and__(self, other: FrozenSet) -> FrozenSet: ...
```

Same operation, two contracts.

**Fix:** align both signatures. Preferred:
`def __and__(self, other: Set) -> Set:` (consistent with `List.__add__` /
`Tuple.__mul__`, which do not return `NotImplemented`).

### 14. `Decimal` comparison ops return `Any` — `poop/types/decimal.py:80-90`

`__lt__`, `__le__`, `__gt__`, `__ge__` all return `Any` despite the body
always producing `true`/`false`.

**Fix:** annotate as `-> Boolean` (mirrors `Int.__lt__`).

### 15. `NormalDist.__eq__/__ne__` return `Any` — `poop/types/statistics.py:146-154`

Every other `__eq__`/`__ne__` in the project returns `Boolean`.

**Fix:** annotate as `-> Boolean`.

### 16. `tarfile`/`zipfile` predicates return `bool` — `poop/types/tarfile.py:71-84,113`, `poop/types/zipfile.py:207`

`TarInfo.is_file/is_dir/is_symlink/is_link`, `TarFile.is_tarfile`,
`ZipFile.is_zipfile` all return `bool` primitives. `Path.is_file` etc. already
return `Boolean`.

**Fix:** return `Boolean` (`return true if ... else false`).

### 17. `SMTP.has_extn` returns `bool` — `poop/types/smtplib.py:50`

Predicate; analogous to `Object.has_attr -> Boolean`.

**Fix:** `def has_extn(self, name: Str) -> Boolean:`.

### 18. `lzma`/`bz2`/`zlib` decompressor properties return `bool` — `poop/types/lzma.py:66-70`, `poop/types/bz2.py:59-63`, `poop/types/zlib.py:73`

`eof` and `needs_input` annotated `-> bool`.

**Fix:** return `Boolean`.

### 19. `Shlex` properties return raw primitives — `poop/types/shlex.py:51,55,136`

`lineno -> int`, `whitespace_split -> bool`, `debug -> int`. Siblings `UUID`,
`ZipInfo`, `TarInfo` already expose POOP types via properties.

**Fix:** `lineno -> Int`, `whitespace_split -> Boolean`, `debug -> Int`, with
matching wraps in the body.

### 20. `Dict.fromkeys(value: Object | None = None)` misses `NoneClass` — `poop/types/dict.py:51`

Project convention for "optional POOP" is `X | NoneClass | None = None`
(see `Path.mkdir`, `Object.format`, `Object.print`, `Str.split`).

**Fix:** `value: Object | NoneClass | None = None`.

### 21. `Dict.zip(*others: object, strict: Boolean | None)` leaks `object` — `poop/types/dict.py:138`

Varargs typed as `object` (raw Python). `strict` also lacks `NoneClass`.

**Fix:** `def zip(self, *others: Object, strict: Boolean | NoneClass | None = None) -> Zip:`
(align `_IterableMixin.zip` accordingly — currently `Any`).

### 22. `_IteratorBase.next() -> Any` propagates to every iterator — `poop/types/_iterator_base.py:45`

Affects 20+ iterators (`StrIterator` should declare `Str`, `RangeIterator`
`Int`, `BytesIterator`/`ByteArrayIterator`/`MemoryViewIterator` `Int`,
`ListIterator`/`TupleIterator`/`SetIterator`/`FrozenSetIterator`/
`DictKeyIterator`/`DictValueIterator` `Object`, `DictItemIterator` `Tuple`).

**Fix:** either parametrize `_IteratorBase` with `Generic[T]` or override
`next()` in each concrete subclass with the correct return type.

### 23. `DictKeys`/`DictItems` set-ops annotated `Any` — `poop/types/dict_keys.py:64-117`, `poop/types/dict_items.py:73-133`

`isdisjoint`, `__or__`, `__and__`, `__sub__`, `__xor__`, `__le__`, etc. all
take `other: Any`. The legitimate input set is
`DictKeys | DictItems | Set | FrozenSet`.

**Fix:** replace `Any` with that explicit union, and drop the
`isinstance(other, set)` branch in `_other_items` that dilutes the boundary
further.

### 24. `Array.slice` and `Array.do` diverge from the analogues — `poop/types/array.py:111,169`

- `Array.slice(start: Int, stop: Int, step: Int | None = None)` requires
  `stop` and does not accept a `Slice`. Other sequence types use
  `slice(start_or_slice: Int | Slice, stop: Int | None = None, ...)`.
- `Array.do(block: Any)` — other types use `Callable[[Object], Any]`.

**Fix:** align with `List.slice`/`Tuple.slice`; type `do` as
`block: Callable[[Object], Any] -> NoneClass`.

### 25. `Bytes`/`ByteArray` base64/hashlib optionals miss `NoneClass` — `poop/types/bytes.py:267,282-303,310-343` (and `byte_array.py` peers)

`b64encode(altchars: Bytes | None = None)`,
`a85encode(*, foldspaces: Boolean | None = None, ..., pad: Boolean | None = None)`,
`b16decode(casefold: Boolean | None = None)` etc. — none accept `NoneClass`,
so passing POOP `none` fails the type checker.

**Fix:** widen each optional to `X | NoneClass | None = None`.

## Bugs

Bugs 26–30 were fixed in v1.0.1. Only bug 31 remains, as a design
question rather than a defect.

### 31. `no_unary_minus` admits inconsistent constant forms — `poop/validators/no_unary_minus.py:12-19` *(lower confidence)*

The validator allows `USub` only when `node.operand` is a plain `Constant`,
which excludes `-(-5)` while admitting `-5` and `-1.5j`. The error message
("unary minus on expressions is forbidden — use `.negated()`") does not
define "expression" cleanly, so the gate behaves inconsistently for
parenthesised constant expressions vs flat literals. Flagged for reviewer
judgment.

**Python behavior:** Python accepts every unary-minus form uniformly —
`-(-5)`, `--5`, `-(-1.5)` all evaluate without complaint. POOP is
intentionally stricter; the inconsistency is in *which* expressions slip
through, not in being strict at all.

**Fix:** decide on the precise rule (e.g. "only `Constant` of type
`int`/`float`/`complex`/`bool`") and reject everything else uniformly.

---

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks):
file an issue with a concrete use case to surface a deferred name.
