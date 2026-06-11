# Proposals

### ~~156. `set == frozenset` and `bytes == bytearray` answer `false` — `_ValueEqMixin` demands the exact wrapper type~~ — DONE

**Decision + implemented:** added an optional `_eq_group: ClassVar[str | None]` to `_ValueEqMixin` (`poop/types/_value_eq.py`). Two wrappers are comparable when they share a class *or* a non-`None` `_eq_group`, so the raw values compare directly (`set == frozenset`, `bytes == bytearray` are equal-by-value in CPython). Declared `_eq_group = "set"` on `Set`/`FrozenSet` and `_eq_group = "bytes"` on `Bytes`/`ByteArray`. A string group avoids the import cycle that mutual class references would create. Both directions of `==`/`!=` now answer the CPython result; foreign operands still answer `false`/`true`. Tests in `tests/test_types/test_frozen_set.py` and `test_byte_array.py`.

### 157. Set algebra rejects mixed `set`/`frozenset` operands — `{1, 2} | frozenset({3})` crashes

`Set.__and__/__or__/__sub__/__xor__` (`poop/types/set.py:104-122`) return `NotImplemented` unless the operand `isinstance(other, Set)`, and `FrozenSet`'s counterparts (`poop/types/frozen_set.py:66-80`) likewise demand a `FrozenSet`. Since neither class accepts the other and neither defines reflected variants that bridge the pair, every mixed expression dies with a `TypeError`, while CPython happily evaluates them (result takes the left operand's type):

```python
({1, 2} | frozenset({3})).print()
# poop: unsupported operand type(s) for |: 'set' and 'frozenset' — expected {1, 2, 3}
(frozenset({1}) | {2}).print()
# poop: unsupported operand type(s) for |: 'frozenset' and 'set' — expected frozenset({1, 2})
```

**Proposed fix:** widen the guards in both classes to `isinstance(other, Set | FrozenSet)` (importing lazily or via a shared module to avoid the import cycle) and build the result from `self._data <op> other._data`, keeping the receiver's class as the result type to match CPython's left-operand rule. Apply the same widening to the comparison/subset operators if they share the strict guard.

### 158. `complex(1, 0) == 1` answers `false` — `Complex` equality is sealed off from `Int`/`Float`

`Complex` gets its equality from `_ValueEqMixin` with `_eq_attr = "_value"` (`poop/types/complex.py:13-15`), so comparing a `Complex` against an `Int` or `Float` short-circuits to `false` even when the values are mathematically equal. The asymmetry is jarring because mixed *arithmetic* already works — `(1 + 2j) + 1` correctly answers `(2+2j)` — yet the equality that CPython defines (`complex(1, 0) == 1` is `True`) answers `false`:

```python
(complex(1, 0) == 1).print()    # False — expected True
((1 + 2j) + 1).print()          # (2+2j) — arithmetic bridging already works
```

**Proposed fix:** give `Complex` its own `__eq__`/`__ne__` (in `poop/types/complex.py`) that unwraps `Complex | Int | Float | Boolean` operands and compares the raw values (`self._value == other._value`), answering POOP `false`/`true`, mirroring the cross-numeric equality already granted to `Decimal` in proposal 148.

### 159. printf-style `%` formatting crashes — `Str` lacks `__mod__`

`Str` (`poop/types/string.py`) defines no `__mod__`, so the `%` operator — a core string operator in Python, same tier as the `+`/`*` operators the wrapper already supports — raises a `TypeError` for every form:

```python
("v %s" % 5).print()
# poop: unsupported operand type(s) for %: 'str' and 'int' — expected "v 5"
("v %s" % (5,)).print()
# poop: unsupported operand type(s) for %: 'str' and 'tuple' — expected "v 5"
```

**Proposed fix:** add `Str.__mod__(self, other)` in `poop/types/string.py` that deep-unwraps the right operand (scalar, `Tuple` of wrappers, or `Dict` with `Str` keys for `%(name)s` mappings — reuse the recursive unwrapper used by `Str.format` from proposal 151), applies `self._value % raw`, and answers a `Str`; return `NotImplemented` for operand types CPython rejects so the error message stays faithful.

### 160. `Boolean` cannot do arithmetic — `True + 1` crashes although POOP reports bool as an int subtype

In CPython `bool` is an `int` subclass, so `True + 1 == 2` and `True * 3 == 3` are ordinary expressions (and summing flags is the canonical counting idiom). In POOP `Boolean` (`poop/types/boolean.py:11`) defines no numeric dunders, and the `Int`/`Float` operator guards only accept `Int | Float` (e.g. `Int.__add__`, `poop/types/int.py:93`), so both operand orders die — and the diagnostic itself advertises the operand as `'bool'`, implying the numeric kinship the implementation denies. Proposal 154 already established the Boolean→number bridge for `int(True)`/`float(True)`; the operators were left behind:

```python
(True + 1).print()
# poop: unsupported operand type(s) for +: 'bool' and 'int' — expected 2
(True * 3).print()
# poop: unsupported operand type(s) for *: 'bool' and 'int' — expected 3
```

**Proposed fix:** either widen the `isinstance(other, Int | Float)` guards in `Int`/`Float` arithmetic and ordering dunders (`poop/types/int.py`, `poop/types/float.py`) to also unwrap `Boolean` as `1`/`0`, or add the numeric dunders (`__add__`, `__radd__`, `__mul__`, ...) to `Boolean` answering `Int` results. If the team instead rules Boolean arithmetic un-Smalltalk-ish by design, the fix is a dedicated validator/error message that says so explicitly rather than the misleading `'bool' and 'int'` TypeError.

### 161. `html.parser` handler overrides never fire — the working SAX surface lives only on the raw inner parser, and `_impl_ref()` hands that raw object out

POOP's `HTMLParser` (poop/types/html.py:45) composes a raw `html.parser.HTMLParser` in `__init__` (html.py:50-53) and `feed` (html.py:54-56) drives that inner instance. CPython's parser delivers events by calling `self.handle_starttag/handle_data/...` on **itself** — so when a POOP user subclasses the wrapper and overrides `handle_data`, the override sits on the POOP object while events fire on the raw `_impl`, whose handlers are the no-op defaults. The entire subclass-and-override surface (the only way CPython's SAX parser is ever used) is silently dead. The one way to get any events is to reach the raw parser — and `_impl_ref()` (html.py:74-75) is a public method that answers exactly that raw `html.parser.HTMLParser` object, a direct raw-stdlib-object leak callable from user code. Repro (`uv run python main.py /tmp/poop_leak_1.py`):

```python
class MyParser(html.parser):
    def handle_data(self, data):
        data.print()

p = MyParser()
p.feed("<b>hi</b>")
"done".print()
```

Actual output: `done` (the override never runs). Expected: `hi` then `done`, with `data` arriving as a POOP `Str`.

**Proposed fix:** in `poop/types/html.py`, make the inner impl a private `_html_parser.HTMLParser` subclass holding a back-reference to the POOP wrapper, whose `handle_starttag`/`handle_endtag`/`handle_startendtag`/`handle_data`/`handle_comment`/`handle_entityref`/`handle_charref`/`handle_decl`/`handle_pi` delegate to the wrapper's method of the same name with POOP-wrapped args (`Str(tag)`, attrs as `List` of `Tuple(Str, Str|none)`, `Str(data)`), following the `__init_subclass__` bridging precedent already used by `logging.Formatter.format` (poop/types/logging.py). Define the POOP-side defaults as no-ops so non-overriding subclasses keep working, and remove (or underscore-mangle away) `_impl_ref()` so the raw parser can no longer be handed to user code.

### 162. `Enum` members created with `auto()` answer a raw Python `int` from `.value`

`auto()` (poop/types/enum.py:204-209) returns a bare `_enum.auto()`, so CPython's `_generate_next_value_` fabricates raw `int` member values and `.value` (the raw descriptor inherited from `enum.Enum`) hands them straight to user code. This is inconsistent with every other way of building a member: literals are rewritten by the transformer pipeline, so `RED = 1` stores a POOP `Int` and `Color.RED.value.print()` prints `1` — but the `auto()` spelling of the *same program* crashes. Repro (`uv run python main.py /tmp/poop_leak_2.py`):

```python
class Color(Enum):
    RED = auto()

Color.RED.value.print()
```

Actual: `poop: 'int' object has no attribute 'print' (line 4)`. Expected: `1`, identical to the `RED = 1` spelling (verified working). The docstring escape hatch "`.value` returns whatever the user assigned" (enum.py:160-171) does not cover this case — the user assigned `auto()`, never a raw `int`; the raw value is fabricated by the wrapper's own machinery.

**Proposed fix:** add a `_generate_next_value_` classmethod to `_PoopEnumMixin` in `poop/types/enum.py` that mirrors CPython's logic but answers a POOP `Int` (unwrap any POOP values in `last_values` via `to_python`, compute `last + 1`, return `Int(...)`). `Int` is hashable and equality-stable, so alias resolution and `_value2member_map_` keep working; `StrEnum`'s own `_generate_next_value_` (lower-cased name) needs the same treatment returning `Str`. Keep `value_object()` as a no-op-compatible alias.

### 163. `logging.getLogRecordFactory()` / `getLoggerClass()` answer raw CPython classes

`Logging.getLogRecordFactory` (poop/types/logging.py:599-601) and `Logging.getLoggerClass` (poop/types/logging.py:607-609) return `_logging.getLogRecordFactory()` / `_logging.getLoggerClass()` unwrapped — raw `logging.LogRecord` and raw `logging.Logger` classes. Every message sent to the result crashes, and calling the factory builds a raw `logging.LogRecord` whose attributes (`name`, `levelno`, `msg`, ...) are all raw `str`/`int` — even though POOP ships its own `LogRecord` wrapper (logging.py:23) and `Logger` wrapper (logging.py:380). `getLoggerClass()` is the same trap proposal 132 fixed for `Logger("app")`: instantiating the answered class builds a corrupt raw logger outside POOP's wrapper discipline. Repro (`uv run python main.py /tmp/poop_leak_3.py`):

```python
factory = logging.getLogRecordFactory()
factory.print()
```

Actual: `poop: type object 'LogRecord' has no attribute 'print' (line 2)`. Expected: a POOP-side factory object that answers messages and, when called, builds a POOP `LogRecord`.

**Proposed fix:** in `poop/types/logging.py`, make `getLoggerClass()` answer the POOP `Logger` class (and `setLoggerClass` accept it, unwrapping to the impl class it manages), mirroring how proposal 133's namespace exposes POOP-side classes. Make `getLogRecordFactory()` answer a POOP callable wrapper around the current raw factory whose `__call__` unwraps POOP args via `to_python` and wraps the produced record in POOP `LogRecord`; `setLogRecordFactory` should accept a POOP block and route it through `poop.types._bridge.bridge` so stdlib-side calls still receive a raw record while POOP-side reads stay wrapped.
