# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 1–11 come from a typing audit of `poop/` (October 2026). `ty check`
passes today, but it passes largely because `Any` is spelt 297 times across
the package: 121 parameters, 101 return types and 65 type arguments. Every one
of them is a place the checker was asked to look away, and the places are not
random — they cluster in a dozen helpers whose callers then inherit the hole.
Each item below names a cluster, shows what the code already knows at that
point, and says how to write it down. The techniques each item leans on
(enum-literal narrowing on `is`, a generic `tuple[type[T], ...]`, a payload
`Protocol`, PEP 696 type-parameter defaults, a generic mixin) were checked
against ty 0.0.70 before being proposed.

Dependency order: 1 is mechanical and independent; 2–4 are the foundations
the rest build on; 5 and 6 depend on 2; 7, 8, 9 and 10 are independent of each
other; 11 is the lock that goes on last.

Items 12–20 come from a second pass over the same code, this time for shape
rather than types: what repeats, what a stdlib module already does, what a
library function changes about the process it runs in. Each was measured or
checked before being written down — the import-cycle idiom in 12 on Python
3.15, the overhead in 14 with `timeit`, the redundancy in 15 by walking every
class's MRO. Order: 12 first, since it touches the import block of most
modules and 18 rides on it; 13, 14, 15 are independent and small; 16 and 17
are the two front-end items; 19 is the maintainer's call; 20 is the lock.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 21. Once every
item has been implemented and deleted, numbering starts over at 1.

### 1. A parameter the body only forwards or tests is `object`, not `Any`

`Any` in a *parameter* position buys exactly one thing: attribute access on
the value inside the body. Most of the 121 `: Any` parameters never use it —
the body hands the value to `isinstance`, to `callable`, to `type(value)`, or
straight through to something else:

    def is_identical(cls, other: Any) -> Boolean        # meta.py:796 — `cls is other`
    def __setattr__(self, name: str, value: Any)        # object.py:107 — forwarded
    def __call__(self, *args: Any, **kwargs: Any)       # block.py:75, 269 — forwarded
    def encoded(text: str, encoding: Any, errors: Any)  # _codec.py:114 — guarded
    def _protocol(cm: Any)                              # with_.py:14 — `type(cm)`
    def __init__(self, *sources: Any, ...)              # zip.py:42 — `a_collection`

Written `object`, the same bodies type-check unchanged and the checker starts
refusing a body that *does* reach into the value without a guard — which is
the whole point of `_argument.py`. Where the body needs more than `object`,
it needs a *specific* type, never `Any`: `Zip`'s sources are
`Iterable[Object]`, `Enumerate`'s source too, `make_bytes_from`'s `build` is
`Callable[[bytes | bytearray | Iterable[int] | int], T]`, `_alias.py`'s
`cls: Any` / `alias: Any` are `type`.

**Fix.** One sweep, file by file, replacing `: Any` with `: object` wherever
the body compiles against it, and with the specific type where it does not.
`**kwargs: Any` on `__init_subclass__` and a metaclass `__new__` may stay as
`object` too — `type.__new__` accepts it. No behaviour changes; this is the
item that makes the later ones' errors visible instead of swallowed.

### 2. A guard in `_argument.py` answers the type it just checked

Every guard takes `Any` and answers `Any` — `text_like`, `a_needle`,
`a_fill`, `bytes_like`, `a_block`, `a_key`, `an_int`, `a_collection`,
`a_pair`, `byte_source`, `a_class`, `a_bound` — so the roughly 150 call sites that
route through them get nothing back from the check they just made, and two
of them re-state the answer with a `cast` (`_set_algebra.py:25`,
`dict.py:111`). Yet each body ends on the line that *knows* the type:

    if isinstance(raw, kinds): return raw            # kinds: tuple[type, ...]
    if callable(value): return value
    if hasattr(raw, "__index__"): return raw
    if isinstance(value, Iterable): return value

`tuple[type, ...]` is the one that loses the information: a generic
`kinds: tuple[type[T], ...]` answers `T`, and ty infers `str | bytes` from
`(str, bytes)` and `str` from `(str,)`. ty refuses a *default* for such a
parameter, and eleven callers (`string.py:284`, `bytes.py:46`,
`object.py:289`, …) rely on `text_like`'s default — an `@overload` without
`kinds` answering `str | bytes | bytearray` keeps them as they are.

**Fix.** Parameters become `object` (item 1); returns become what the guard
established: `text_like[T] -> T` (overloaded for the default), `a_fill -> T |
None`, `a_needle -> T | int` on byte receivers, `bytes_like -> bytes |
bytearray | memoryview` (`| None` under `optional`), `a_block ->
Callable[..., object]`, `a_key -> Callable[[object], object]`, `an_int -> int`
— through `operator.index(raw)`, which is the Pythonic spelling of "anything
with an `__index__`" and answers an `int` instead of the duck test's `Any` —
`a_collection` / `a_pair -> Iterable[Object]`, `a_class -> type | tuple[type,
...]`, `_opt_text` (`string.py:133`) `-> str | None`. The two casts go, and
`_at.py` follows the same rule: `at_index[T](items: Sequence[T], index:
SupportsIndex) -> T`, `at_key[K, V](data: Mapping[K, V], key: K) -> V`,
`no_element_at(…, items: Sized, …)`.

### 3. `_faithful` and `_unwrap` through a payload `Protocol`

`_faithful(value: object) -> Any` (`_raw.py:11`) is the one deliberate hole:
its docstring says it "returns `Any` so the raw fallback slots into a `str` /
`bytes` / `int` parameter without a per-call-site ignore". `_unwrap`
(`_unwrap.py:58`) then launders through it — `result: Any = _faithful(value);
return result` — to claim `T` for a value that is `T` only if the caller passed
the right wrapper. `_searched` and `_repeat_count` inherit the same `Any`, and
`_NumericCompareMixin` declares `_value: Any` (`_numeric_compare.py:56`) for a
slot `Boolean`, one of its three users, does not have.

Every wrapper that *has* a payload declares it in a slot with a known type —
`Int._value: int`, `Str._value: str`, `Bytes._value: bytes`, `Float._value:
float` — and a `Protocol` can read that:

    class _Wrapped[T](Protocol):
        @property
        def _value(self) -> T: ...

    @overload
    def _faithful[T](value: _Wrapped[T]) -> T: ...
    @overload
    def _faithful(value: object) -> object: ...

ty infers `int` for `_faithful(Int(1))` and `str` for `_faithful(Str("a"))`.
A call site holding `Str | NoneClass | None` — which is how the optional
arguments are already annotated — gets `str` back from `_unwrap` honestly; a
call site holding `object` gets `object`, and has to go through an
`_argument.py` guard (item 2), which is where it should have been anyway. The
`object` overload keeps the documented fallback for a payload-less `List`
reaching a `str` parameter, now visible as `object` rather than hidden as
`Any`.

**Fix.** The protocol and the overloads in `_raw.py`; `_unwrap[T, D](value:
_Wrapped[T] | NoneClass | None, default: D) -> T | D` with the laundering
line gone; `_opt_str` reduced to the `_unwrap` call it already is. On
`_NumericCompareMixin`, drop the phantom `_value: Any` and make
`_order_value(self) -> int | float` the abstract hook `Int` and `Float`
implement with `return self._value` — the mixin then states the one thing it
needs and nothing it does not have.

### 4. A sentinel-returning helper says so in its type

`_sentinel.py`'s docstring makes the case for the `Enum`: "a type checker
narrows on it". Nothing lets it. The three helpers that answer a sentinel all
answer `Any`:

    def _repeat_count(other: object) -> Any    # int | NOT_A_COUNT  (_repeat.py:8)
    def _num_value(other: object) -> Any       # int | float | NOT_NUMERIC  (_numeric_compare.py:25)
    def _integral_value(other: object) -> Any  # int | NOT_INTEGRAL  (int.py:34)

so `if count is NOT_A_COUNT: return NotImplemented` narrows nothing, and the
`self._items * count` after it is checked against `Any`. ty narrows an enum
literal on `is`: with `-> int | Literal[Sentinel.NOT_A_COUNT]`, the
fall-through sees `int`.

**Fix.** Three aliases beside the existing `Missing` — `NotACount`,
`NotNumeric`, `NotIntegral` — and the three return types written as the union
they are. The same spelling fixes `_PeekMixin._peeked: Any`, which is `T |
Literal[Sentinel.UNPEEKED]` (item 7).

### 5. `default: Any = MISSING` is `default: D | Missing = MISSING`

Nine messages take an optional default and annotate it `Any`: `_minmax`,
`_PeekMixin.next`, `an_int`, `_IterableMixin.min` / `max`,
`_MappingMixin.min` / `max`, `Str.min` / `max`. `Dict.pop` writes it `Object |
NoneClass | Any` (`dict.py:64`), and a union with `Any` *is* `Any` — the two
real members are decoration. All of them then answer `Any`, which is why
`Int.max`, `Float.max` and `Boolean.max` each wrap `_minmax` in a `cast`
(six casts across `int.py:80,87`, `float.py:54,63`, `boolean.py:291,301`).

The honest shape is a second type parameter: `def next[D](self, default: D |
Missing = MISSING) -> T | D`. ty answers `T | D` when a default is passed; when
none is, `D` is unsolved and ty answers `T | Unknown`, so the pair is written
as two `@overload`s — one without `default` answering `T`, one with it
answering `T | D`.

**Fix.** The overload pair on each of the nine, `Dict.pop(key, default: D |
Missing = MISSING) -> Object | D`, and `_minmax[T, D](func, name, iterable:
Iterable[T], key: Key[T], default: D | Missing) -> T | D` (the `Key` alias is
item 6's). The six casts go. Two of them were also hiding a wrong answer:
`Int.max` declares `-> Int` for operands typed `Int | Boolean`, and
`Int(0).max(true)` answers `true` — `Boolean.max` already says `Int |
Boolean`; `Int.max` and `Float.max` should say the same.

### 6. `_IterableMixin` is generic over its element

`Callable[[Any], Any]` is spelt 26 times in the package, 11 of them in
`_IterableMixin` alone, and `key: Callable[[Any], Any] | NoneClass | None` 18
times. The mixin's own `__iter__` is `Iterator[Any]`, so `find` answers `Any`,
`reduce` answers `Any`, `sum` answers `Any`, and every block parameter is a
function from nothing to nothing. But each concrete receiver knows its
element: `Str` yields `Str`, `Bytes` yields `Int`, `Range` yields `Int`,
`List` / `Tuple` / `Set` / the mappings yield `Object`.

    class _IterableMixin[T]:
        def __iter__(self) -> Iterator[T]: ...
        def do(self, block: Callable[[T], object] | Missing = MISSING) -> NoneClass
        def find(self, block: Callable[[T], object] | Missing = MISSING) -> T | NoneClass
        def reduce[R](self, init: R | Missing = MISSING,
                      block: Callable[[R, T], R] | Missing = MISSING) -> R
        def map[R](self, block: Callable[[T], R] | Missing = MISSING) -> Map[T, R]
        def filter(self, block: Callable[[T], object] | Missing = MISSING) -> Filter[T]

with `class Str(…, _IterableMixin[Str], Object)` and so on. ty answers `Str |
None` for a `find` on such a receiver. `Map` and `Filter` follow: `_BlockView`
is `_LazyView[Any]` today (`_block_view.py:11`) and becomes `_BlockView[S,
T](_LazyView[T])` over `source: Iterable[S]` and `block: Callable[[S],
object]`; `Map[S, T]` yields the block's answer, `Filter[T](_BlockView[T, T])`
yields its source's element. `_generate` sets `self._source = self._block =
None` to release them, which is what forced `self._block: Any`; with
`__slots__`, `del self._source, self._block` releases them without widening
the type.

**Fix.** The generic mixin and views as above, with two aliases where the
spelling repeats — `type Key[T] = Callable[[T], object] | NoneClass | None`
for the 18 `key` parameters, and the block parameter written out, since each
message's block has its own shape. Depends on item 2 for `a_block`'s answer.

### 7. `_Cursor[T, R = T]` names the raw element it wraps

`_PeekMixin` (`_peek.py`) is the whole cursor protocol and is typed `Any`
throughout: `_materialize -> Iterator[Any]`, `_wrap(value: Any) -> Any`,
`_pull -> Any`, `_buffered -> Any`, `next -> Any`, `__next__ -> Any`,
`_peeked: Any`. `_Cursor[T]` is already generic over the element and sits
right above it, so the mixin is generic in all but spelling. The one thing
that stops `_wrap` from being `(T) -> T` is `_DictItemIteratorBase`: its raw
iterator yields `tuple[Object, Object]` and `_wrap` answers a `Tuple`.

PEP 696 gives the parameter a default, and ty honours it:

    class _Cursor[T, R = T](_PeekMixin[T, R], _IterableMixin[T], Object):
        _peeked: R | Unpeeked
        def _materialize(self) -> Iterator[R]
        def _wrap(self, raw: R) -> T
        def _pull(self) -> R
        def next[D](self, default: D | Missing = MISSING) -> T | D   # item 5's pair
        def __next__(self) -> T

Every iterator but one spells a single parameter as it does today;
`_DictItemIteratorBase(_IteratorBase[Tuple, tuple[Object, Object]])` spells
both, and `Enumerate` / `Zip` keep `_LazyView[Tuple]`.

**Fix.** Make `_PeekMixin` generic and give `_Cursor` the defaulted second
parameter; `_IteratorBase.__init__(self, iterable: Iterable[R])` and
`self._iter: Iterator[R]`. `Unpeeked` is item 4's alias.

### 8. A mixin's payload slot is typed by what the mixin does with it

`_SequenceMixin._items: Any` (`_sequence.py:43`) and
`_SetAlgebraMixin._data: Any` (`_set_algebra.py:95`) are declared `Any` so that
`List`'s `list` and `Tuple`'s `tuple`, or `Set`'s `set` and `FrozenSet`'s
`frozenset`, both satisfy the declaration. But a mixin only needs the
*operations it performs*: `_SequenceMixin` reads `len`, `iter`, `in`, `*` and
`index` — `Sequence[Object]` — and `_SetAlgebraMixin` reads `len` and the set
operators — `collections.abc.Set[Object]`, imported as `AbstractSet` to keep
POOP's own `Set` unshadowed. Each concrete class narrows its own slot, as
`_MappingMixin` already does with `_data: dict[Object, Object]`.

The same module carries a second workaround for the same gap. `_other_set`
(`_set_algebra.py:55`) recognises an operand by a duck-typed `_set_like`
`ClassVar` and reads `other._data  # ty: ignore[unresolved-attribute]`; its
docstring says the marker avoids "the Set <-> FrozenSet import cycle". The
class that would be tested — `_SetAlgebraMixin` — is defined forty lines below
in the *same file*, so `isinstance(other, _SetAlgebraMixin)` creates no cycle,
narrows `other` to a type that declares `_data`, and retires the marker, the
ignore and the `-> Any`.

**Fix.** The two slot annotations; `_other_set -> AbstractSet[Object] | None`
over `isinstance`; `_SetLikeView._own -> AbstractSet[Object]` (`DictItems`
already says `set[Object]`; `DictKeys` and the base say `Any`); and the
operator callbacks typed by their operands —
`op: Callable[[AbstractSet[Object], AbstractSet[Object]], AbstractSet[Object]]`
in `_algebra` / `_inplace` / `_dict_view._algebra`, `Callable[[int, int |
float], int | float]` in `Int._arith`, `Callable[[int | float, int | float],
bool]` in `_order` and `_compare`. `operator.add` and friends are assignable
to all of them.

### 9. `to_poop` is overloaded; `to_python` answers `object`

`_bridge.py`'s two dispatchers answer `Any`, and the registered halves spell
`list[Any]`, `tuple[Any, ...]`, `dict[Any, Any]`, `set[Any]`,
`frozenset[Any]`. `to_python` crosses *out* of the language, so `object` is
the honest answer and the containers are `list[object]`, `dict[object,
object]` and so on — nothing in `poop/` reads a member back. `to_poop` crosses
*in*, and its four callers (`int.py:175,208`, `float.py:136,200`) depend on
the answer: `Int._arith` is declared `-> Int | Float` on the strength of an
`Any`. `singledispatch` cannot express "an `int` answers an `Int`", but a
public function can be declared over a private dispatcher:

    @overload
    def to_poop(value: int) -> Int: ...
    @overload
    def to_poop(value: float) -> Float: ...
    …
    def to_poop(value: object) -> object:
        return _to_poop(value)

ty expands a union argument across overloads, so `to_poop(op(int, int |
float))` answers `Int | Float` — the type `_arith` already claims. Should it
not, `_arith` can branch on `isinstance(raw, int)` itself, which is one line
and says the same thing.

**Fix.** As above, one overload per registered native. `to_python -> object`
with `object`-typed containers.

### 10. A return the code already knows is not `Any`

Independent of the clusters above, about forty `-> Any` are on functions
whose body ends in one known type:

- `Object.class_` (`object.py:51`) answers `type(self)`: `type[Self]`.
- `Error.kind` and `poop_class_of` answer an exception class:
  `type[BaseException]`. `Error.class_` (`error.py:53`) *raises* — `Never`,
  which also documents the surprise its docstring spends a paragraph on.
- `PoopMeta.superclass` answers a class or `none`: `PoopMeta | NoneClass`.
  `mro` answers `list[type]` or refuses. `class_` and `class_name` on the
  class side only refuse: `Never`, as `_refuse` already declares.
- `PoopMeta.__new__` and `_AliasMeta.__new__` answer `Self`, which is how
  typeshed types `type.__new__`; `_AliasMeta.__call__` answers `object`.
- `_adapted(slot, method: Callable[..., object]) -> Callable[..., object]`;
  `_class_operator -> Callable[..., Never]`; `_length_message(self: object) ->
  Int`; `class_side.__get__ -> Self | Block | MethodType`.
- `does_not_understand -> object` on all three definitions: the base raises,
  but the docstring invites an override that answers, so `object` is the
  contract and `Never` is not.
- `Boolean._rev` and the twelve `__r*__` built on it (`boolean.py:309–403`)
  call whatever `other` answers: `object`, as typeshed types a reflected
  operator on an unknown operand.
- `_exception_kind -> type[BaseException] | tuple[type[BaseException], ...]`;
  `_protocol -> tuple[Callable[..., object], Callable[..., object]]`;
  `reflected_pow -> object`; `_refuse_leftovers(iterators:
  list[Iterator[object]])`; `_endow` / `_fill` / `wrapped_instance[T](cls:
  type[T], *args: object) -> T` in `_alias.py`.

**Fix.** Each as listed; none changes behaviour. `Try._execute`'s `cast` on
`self._block` (`try_.py:115`) goes the way item 6's views do: `del
self._block` after the run instead of `= None`, and the slot's type stays
`Callable[[], object]`.

### 11. Turn `ANN401` back on

`pyproject.toml` ignores `ANN401` — ruff's "no `Any` in a signature" — which
is the rule that would have reported every item above as it was written. With
items 1–10 in, the survivors are few and each has a sentence to justify it:
the `object` overload of `_faithful` is honest and no longer `Any`; the two
`__getattr__` / `__getattribute__` hooks are hidden under `if not
TYPE_CHECKING` and may carry `# noqa: ANN401` with the comment they already
have; a metaclass `__new__`'s `**kwargs` is `object` (item 1).

**Fix.** Remove `ANN401` from `ignore`; keep `tests/` exempt in
`per-file-ignores`, where the 62 remaining `Any`s belong to mock helpers the
file already exempts from `ANN001`–`ANN003`. `RUF100` is already on, so a
`noqa` that stops being needed is reported, which is what keeps the count from
growing back. While there, one spelling for the suppressions the checker
itself needs: `_dict_view.py:137` and `mapping_proxy.py:30` write `# type:
ignore[assignment]` and `_set_algebra.py:63` writes `# ty: ignore[…]` — after
item 8 only the first two remain, and they are the `__hash__ = None` idiom
typeshed itself writes with that exact directive, so `type: ignore` is the
one to keep.

### 12. One idiom for the import cycles: import the module, not the name

`poop/types/` is one flat package whose modules need each other at call time
— `Int` answers a `Str` from `hex`, a `Float` from `/`, a `Tuple` from
`divmod`; everything answers `none` and a `Boolean`. Today that is spelt as a
function-local import at the line that needs it: 60 carry `# noqa: PLC0415`,
and `meta.py` and `object.py` are exempted from the rule wholesale and hold
about 90 more. `int.py` alone imports `Str` inside four different methods. The
hubs are `boolean` (`to_boolean`, `true`, `false`), `none`, `string` and
`exceptions` (`MIRRORS`) — 49 of the local imports are `none` or `to_boolean`.

A function-local import is Python's workaround of last resort, and the
language has a first-resort one: bind the *module* at the top and read the
name when it is used. Since Python 3.7 `import poop.types.boolean as _boolean`
succeeds inside a cycle — the submodule is already in `sys.modules`, partially
initialised, and `_boolean.to_boolean(...)` resolves at call time, after both
modules have finished loading. Checked on 3.15 with a two-module cycle. The
same trick is why `from poop.types.boolean import to_boolean` *cannot* go at
the top: it reads the attribute at import time.

**Fix.** For every edge that is a cycle, `import poop.types.<mod> as _<mod>`
at the top and `_<mod>.Name` at the use; the `TYPE_CHECKING` block keeps the
names for annotations as it does now. Then drop the two per-file `PLC0415`
exemptions in `pyproject.toml`, so the rule is on everywhere and a new cycle
is reported as one instead of being written as a local import. The edges that
are *not* cycles (a leaf like `_sentinel`, `_cloak`, `_message`) stay as
ordinary `from … import`. Where a module reaches for one hub in a dozen
methods — `int.py` and `boolean.py` — the file gets shorter.

### 13. `cloak` is a class keyword, and the mixins share one base

Every wrapper module ends with `cloak(Int, "int")`: 43 trailing calls, 13 of
them `cloak(_SomeMixin, "object")` under nine copies of the same four-line
comment ("Cloaked as `object`, the root's own spelling: these methods are
inherited by many wrappers…"). The cloak is part of the class's declaration —
the name it answers to — and the package already says so for one family:
`class BytesIterator(_IteratorBase[Int], name="bytes_iterator")` cloaks
through `_Cursor.__init_subclass__`, and `_DictView` does the same. The rest
of the tree spells it as a statement after the fact, which also means a new
wrapper can be defined and the line forgotten; `tests/test_cloak.py` exists to
catch exactly that.

The mixins carry a second repeated declaration: `__slots__ = ()` with the
same paragraph explaining that a slot-less class anywhere in an MRO restores
`__dict__` (`_value_eq.py`, `_iterable_mixin.py`, `_sequence.py`,
`_set_algebra.py`, `_bytes_like.py`, …).

**Fix.** `PoopMeta.__new__` takes `name: str | None = None` as a class
keyword and applies `cloak` when it is given; `Object`'s subclasses then read
`class Int(_NumericCompareMixin, Object, name="int")` and the trailing call
goes. `_Cursor` and `_DictView` stop redefining `__init_subclass__` for it. The
mixins — plain classes outside the `Object` tree — descend from one `_Mixin`
whose `__slots__ = ()` and `__init_subclass__` cloak as `object`, and whose
docstring holds the `__dict__` paragraph once. `cloak` itself stays a
function, since `builtin_alias` and the exception mirrors call it on classes
they build by hand.

### 14. The protocol-slot adapter wraps only a program's classes

`PoopMeta.__new__` wraps `__str__`, `__repr__`, `__bool__`, `__hash__` and
`__len__` in `_adapted` so a *program's* class can answer a `Str` or an `Int`
from them and CPython still receives a native. Its docstring says the library's
own wrappers "pass through untouched" — true of the value, not of the call:
every one of the 49 wrappers' five slots is wrapped too, and each `hash(x)`,
`str(x)`, `len(x)` or `bool(x)` on a POOP value pays a Python-level frame, an
`isinstance`, and a `functools.wraps` indirection to learn it was native all
along. Measured on `Int(1)`, 500k calls each:

| call | through `_adapted` | the slot itself |
|---|---|---|
| `hash(x)` | 0.29 s | 0.15 s |
| `str(x)` | 0.35 s | 0.19 s |

`hash` is on the path of every `Dict` and `Set` operation, `bool` of every
`if_true`, `len` of every `len()`. The two populations are already
distinguishable at class-creation time: the executor binds `__name__` to
`"__poop__"`, so a class a program defines arrives with
`namespace["__module__"] == "__poop__"`, and a library class with
`"poop.types.…"`.

**Fix.** Adapt the slots only when the namespace's `__module__` is
`"__poop__"`. The library's wrappers already answer natives, which is what the
short-circuit was checking at run time, class by class, call by call. One
test per slot that a library wrapper's slot is the function written in its
module, not a wrapper around it.

### 15. `__repr__ = __str__` is already `Object`'s answer

Twenty-two classes end their body with `__repr__ = __str__` — `Int`, `Float`,
`List`, `Dict`, `Set`, `Range`, `Slice`, `Try`, `With`, `NoneClass`, the
iterator base, … — and `Object.__repr__` is `return str(self)`. Walking every
class in `poop/types/` and asking what `__repr__` would resolve to without
the alias answers `Object.__repr__` for all twenty-two; the four classes whose
`__repr__` differs from `__str__` — `Object` itself, `Str`, `Boolean` and
`ByteArray` — define a real one and are unaffected. The alias is also what forces `_adapted` to wrap
each class's `__repr__` separately from its `__str__`, since both land in the
namespace.

**Fix.** Delete the twenty-two lines. Behaviour is identical: `repr(x)`
reaches `Object.__repr__`, which calls the class's own `__str__`.

### 16. The REPL is a `code.InteractiveConsole`

`Repl.run` (`repl.py`) re-implements the loop `code.InteractiveConsole`
ships: accumulate lines in a buffer, hand them to `codeop.compile_command`,
loop on `None` for an incomplete statement, reset on `SyntaxError`, switch the
prompt between `>>>` and `...`, swallow `KeyboardInterrupt` and end on
`EOFError`. Sixty lines of `run` plus `_indent_for`, `_readline_input` and the
`_leading_mark` flag are that loop; what is POOP's is the pipeline in
`run_source_repl`, the per-input filename, the `:meta` commands, the coloured
prompt, the auto-indent and the display hook. `InteractiveConsole` has an
override point for each: `raw_input` (prompt, indent hook, meta dispatch,
byte-order mark), `runsource` (the pipeline, the filename, the error report),
`write` (stderr through `_ERR`), and `sys.ps1` / `sys.ps2` for the prompts.

The module also keeps `_OUT = OUT` and `_ERR = ERR` as module globals "so a
test can swap the REPL's own", and `tests/test_repl.py` does so with
`monkeypatch.setattr("poop.repl._OUT", …)` five times. A seam that is a module
global is a seam every test shares; the Pythonic one is a constructor
parameter.

**Fix.** `class Repl(code.InteractiveConsole)` with the four overrides;
`Repl(interpreter, *, out: Console = OUT, err: Console = ERR)` and the
module-level `_print_value` / `_error` / `_say` become methods writing to
`self._out` / `self._err`. The tests pass consoles in instead of patching the
module. `_PoopCompleter` and the readline setup are untouched.

### 17. `execute` does not leave the recursion limit raised

`executor.execute` calls `sys.setrecursionlimit(6000)` when the current limit
is lower, and never restores it — "raised, not set", the comment says, so a
caller that asked for more keeps it. A library function that changes
process-wide interpreter state as a side effect of running a program is the
kind of thing Python spells as a context manager; the test suite imports
`execute` and so runs the rest of its own tests, and pytest itself, at the
raised limit after the first POOP program.

**Fix.** A `_recursion_budget()` context manager in `executor.py` that raises
the limit for the duration of `exec` and puts the previous value back, used
around the one `exec` call. The REPL already goes through `execute` per input,
so each input runs under the budget and the prompt returns to the process's
own. The "keeps a higher limit" rule holds within the block: the manager only
raises, never lowers.

### 18. The mirrors under their own names

`raise MIRRORS["TypeError"](…)` appears 120 times — 71 `TypeError`, 22
`ValueError`, six each of `RuntimeError` and `AttributeError`, and a handful of
others. A string key into a module-level dict is how a registry is read, not
how an exception is raised, and the spelling costs something at every site: the
key is a `Literal` the checker verifies but the reader cannot complete, and
`exceptions.py` itself needs `cast("MirrorName", native.__name__)` to write
into the same table. The mirrors are classes with fixed names, built once at
import; nothing about them is dynamic after that.

**Fix.** A `poop/types/mirrors.py` that binds each mirror under its own name
after `exceptions` has built the table — `TypeError = MIRRORS["TypeError"]`
and so on, sixteen lines under one `# noqa: A001` comment saying that the
mirror *is* POOP's `TypeError` — and call sites read `raise
mirrors.TypeError(…)`. `MIRRORS` stays for the two readers that are
table-shaped: `poop_class_of` and the `_at.py` helpers that take a
`MirrorName`. Depends on item 12 for the import style, since `exceptions` sits
in the cycle.

### 19. The call-name validators are one table

Of the 71 validators, 38 are a `CallNameValidator`: a module of five lines
holding a class, a `forbidden = frozenset({"len"})` and a `message` (seven of
them ban a small family — `iter` and `next`, `exec` and `eval`, …). They
differ in two strings and share one visitor, one base, one parametrised test
(`tests/test_validators/test_call_name.py` already walks them as data), and one
consumer — the REPL's `:explain`, which reads `forbidden` back off each
instance through `getattr(validator, "forbidden", ())`.

**Fix.** A mapping in `_call_name.py`, a frozenset of names to its message,
and `DEFAULT_VALIDATORS` extended with one `CallNameValidator(names, message)`
per row — so `len(DEFAULT_VALIDATORS)`, which `tests/test_doc_counts.py` reads
against `README.md`, counts as it does now. The 33 validators with a visitor
of their own keep their modules. `:explain` asks
`isinstance(validator, CallNameValidator)` instead of duck-typing the
attribute. `CONTRIBUTING.md`'s "a new validator" recipe gains a first step: a
banned builtin is a row, not a module. This one is a judgment call about
discoverability — `no_len.py` is a filename a reader can `ls` for — which is
why it is written down rather than done.

### 20. Turn on the rules the code already passes

Run with ruff's full rule set, `poop/` trips almost nothing outside the
families already on: `PERF`, `PIE`, `RET`, `PTH`, `C4` and `SIM` pass clean,
`FURB` and `PLR` in preview find five lines (three generator expressions that
are `itertools.starmap` — `errors.py:252`, `dict_items.py:24,56` — and two
`in (…)` tuples that are set literals — `errors.py:140`, `_argument.py:269`),
and `ARG`, `TRY`, `A`, `N` and `PLR` find two dozen sites that are each
intentional: a
`reversed` / `abs` / `round` *message* shadowing the builtin it replaces, an
unused `start` on `Str.sum` whose job is to refuse, an unused `other` on the
Boolean singletons' operators, `MessageNotUnderstood` without an `Error`
suffix.

**Fix.** Fix the five preview findings. Add `PERF`, `PIE`, `RET`, `PTH`,
`C4`, `FURB`, `ARG`, `TRY` and `PL` to `select`, ignore `A003` for the
message names that mirror builtins by design and `N818` for the one class, and
mark the remaining intentional sites with a `noqa` and the reason, as the
`PLW1641` sites do today. `RUF100` keeps each one honest.
