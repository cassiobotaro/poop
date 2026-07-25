# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

---

### 1. Every unowned CPython builtin is reachable by name

**Severity: high (integrity / Python leak).**

`no_dunder_name` closed the dunder globals, but the *ordinary* builtins are
still there: `exec` gives user code CPython's full `__builtins__`, and POOP only
covers the names it bans (68 validators) or rewrites (`int`, `list`, the 16
mirrored exceptions). Everything else resolves to a naked native:

```
OSError.print()      -> AttributeError: type object 'OSError' has no attribute 'print'
BaseException        -> the raw class
KeyboardInterrupt    -> the raw class
copyright.print()    -> AttributeError: '_Printer' object has no attribute 'print'
NotImplemented       -> NotImplementedType
classmethod / staticmethod / property -> raw Python types
```

55 of Python's 71 builtin exceptions land here. That contradicts
`poop/types/exceptions.py`, which mirrors 16 *on purpose* — "a language with no
I/O and no codecs cannot reach the `OSError` subtree" — while `OSError` itself
stays one identifier away. The error a user gets is CPython's
(`type object 'OSError' has no attribute 'print'`), not POOP's
`does not understand #print`.

Repro:

```bash
printf 'OSError.print()\n'   | poop /dev/stdin   # raw AttributeError, validators clean
printf 'copyright.print()\n' | poop /dev/stdin   # a live _Printer object
```

**Solution.** Stop enumerating and hand `exec` a builtins allow-list. Contrary
to what the dunder-globals proposal assumed, `exec` only *injects*
`__builtins__` when the globals dict lacks it — a supplied one is honoured, so
this is a small change in `poop/executor.py`:

```python
# The only builtins user code may reach. Everything else — OSError, copyright,
# NotImplemented — is a naked native; POOP is the language, not the library.
_ALLOWED_BUILTINS: dict[str, object] = {
    "__build_class__": builtins.__build_class__,  # the `class` statement
    "__name__": "__poop__",                       # read by class creation
    "super": builtins.super,                      # allowed by INFECTIONS.md
    "classmethod": builtins.classmethod,          # class-side declaration
    "staticmethod": builtins.staticmethod,
    "property": builtins.property,
}
...
ns.setdefault("__builtins__", dict(_ALLOWED_BUILTINS))
```

An unknown name then answers `NameError: name 'OSError' is not defined`, which
is exactly what "if Python needs an import to reach it, POOP does not offer it"
means. Verified against the whole `examples/` tree: with this dict every example
still runs (`greet.py` only fails on EOF from stdin). The three decorator
entries are load-bearing — `patterns/execute_around.py`, `patterns/singleton.py`
and `patterns/flyweight.py` use `@staticmethod` / `@classmethod`, which are
class-definition machinery with no message-passing substitute, the same argument
that already carves out `super`.

Defence in depth, not a replacement: `no_dunder_name` still gives the *teaching*
error at validation time, and the allow-list catches every name no validator
enumerates. Add `tests/test_executor.py` cases for a rejected native and for an
allowed `super` / `class` program, and an `INFECTIONS.md` row under the
namespace section.

---

### 2. The `getattr` substitutes leak `#_value` for a non-`Str` name

**Severity: medium (Python leak, on every object).**

`get_attr` / `has_attr` / `set_attr` / `del_attr` read `name._value` before
anything else, so a non-`Str` name trips `does_not_understand` and the error
names a POOP internal. They are the substitute `no_getattr` points at, and they
live on `Object` — every value in the language has them, and `PoopMeta` repeats
the same four sites class-side:

```
(5).get_attr([1])       -> list does not understand #_value
(5).has_attr(1)         -> int  does not understand #_value
(5).set_attr(none, 1)   -> NoneType does not understand #_value
Foo.get_attr([1])       -> same, class-side
```

`Object.assert_` has the same shape one method over: `none.assert_([1])` reads
`message._value` and leaks, though CPython's `assert x, msg` accepts *any*
object as the message.

**Solution.** One helper next to the faithful-unwrap idiom in
`poop/types/_unwrap.py`, used by all eight attribute sites:

```python
def _attr_name(name: object) -> str:
    """The raw attribute name behind a `Str`, else CPython's own TypeError.

    `getattr(obj, 5)` answers `attribute name must be string, not 'int'`;
    reading `name._value` answered `int does not understand #_value`.
    """
    raw = _faithful(name)
    if not isinstance(raw, str):
        raise TypeError(f"attribute name must be string, not {type(name).__name__!r}")
    return raw
```

The guards then read the unwrapped name once
(`raw = _attr_name(name); self._reject_dunder(raw); ...`), which also removes
the repeated `._value` reads inside each method. `assert_` needs no helper — it
is the plain faithful unwrap, `raise AssertionError(_faithful(message))`, which
additionally makes a non-`Str` message work as it does in Python.

Regression tests under `tests/test_types/test_object.py` and `test_meta.py`
asserting the faithful message (not `#_value`), one per accessor per side.

---

### 3. Indexing messages leak `#_value` and reject a Boolean index

**Severity: medium (Python leak **and** correctness gap).**

`at`, `slice`, `insert`, `pop` and `Slice.indices` unwrap the index as
`index._value`, so a foreign index leaks — and a `Boolean` index, which CPython
accepts because `bool` is an `int` subclass, fails everywhere:

```
[1, 2].at([0])              -> list does not understand #_value
"ab".at(True)               -> bool does not understand #_value   (CPython: "b")
[1, 2].at(True)             -> bool does not understand #_value   (CPython: 2)
bytearray(b"ab").at(True)   -> bytearray indices must be integers or slices, not bool
range(True, 5)              -> int() argument must be ... not 'bool'  (CPython: range(1, 5))
```

Note the split: `Range.at` and `ByteArray.at` already route through `_faithful`,
so they no longer leak the slot name — but they still refuse `True`, because a
POOP `Int` is only usable as an index after something unwraps it by hand. The
faithful-unwrap idiom cannot fix that half.

**Solution.** Make the numeric tower answer Python's index protocol, then stop
unwrapping at the call sites:

```python
class Int(...):
    def __index__(self) -> _int:
        return self._value

class Boolean(...):
    def __index__(self) -> int:
        return 1 if self else 0      # bool is an int subclass in CPython
```

`self._items[index]`, `self._value[index]`, `self._items.insert(i, obj)` and
`slice(self._start, self._stop, self._step)` then work with the POOP object
directly; CPython calls `__index__` for an `Int`/`Boolean` and raises its own
`list indices must be integers or slices, not list` for anything else. Verified
on a patched build: `[10, 20][Int(1)]`, `[10, 20][true]`, `"abc"[true]`,
`slice(Int(1), None).indices(5)` and `[1, 2, 3][slice(Int(1), Int(3))]` all
answer what CPython answers, and every foreign operand raises the faithful
`TypeError`.

Sites to clean up afterwards: `List.at` / `slice` / `insert` / `pop`,
`Tuple.at`, `Str.at`, `Bytes.at`, `MemoryView.at`, `Slice._py_slice` /
`indices`, and `Range.__init__` (`start._value <= stop._value`, which is why
`range(True, 5)` fails today). Each ships as its own commit, with a
boolean-index test and a faithful-message test per type, plus an
`INFECTIONS.md` note that `Int` / `Boolean` answer `__index__` — the one
protocol dunder POOP adds so that *no* call site has to unwrap an index by hand.

---

### 4. `Str.format` template fields reach attributes and items

**Severity: medium (Python leak — bypasses `no_dunder_attribute` entirely).**

`str.format`'s field syntax performs attribute access and subscripting at
runtime, from inside a string literal no validator can read:

```bash
printf '"{0.__class__}".format(5).print()\n'            | poop /dev/stdin
# -> <class 'int'>            a raw CPython class, printed
printf '"{0.__class__.__name__}".format("x").print()\n' | poop /dev/stdin
# -> str
printf '"{0[0]}".format([1, 2]).print()\n'              | poop /dev/stdin
# -> 1                        obj[key], which no_subscript bans in source
```

This is precisely the case `Object._reject_dunder` exists for — "a computed name
puts that spelling beyond any static validator's reach" — except `format` has no
such guard. It is worse than the `get_attr` hole it mirrors, because
`Str.format` deep-unwraps its arguments through `to_python`, so `{0.__class__}`
runs against the *raw Python value*, not the wrapper.

**Solution.** Validate the template before formatting, in `Str.format`:

```python
def _reject_field_access(template: str) -> None:
    """Refuse `{0.attr}` / `{0[key]}` — a format field is not an escape hatch.

    `str.format` reads attributes and items at runtime, so `{0.__class__}`
    reopens exactly what `no_dunder_attribute` closes and `{0[0]}` what
    `no_subscript` closes. Only the field *name* is inspected: a format spec
    may legitimately contain a dot (`{:.2f}`), and `Formatter.parse` already
    splits the two.
    """
    for _, field, spec, _ in _Formatter().parse(template):
        if field and ("." in field or "[" in field):
            raise ValueError(
                f"{{{field}}} is forbidden — a format field reaching an "
                "attribute or an item bypasses obj.get_attr(...) / obj.at(...); "
                "send the message and format the answer"
            )
        if spec:
            _reject_field_access(spec)  # nested specs: "{:{0.__class__}}"
```

The recursion matters — `"{0:{1.__class__}}".format(1, 2)` leaks the same class
repr through the `ValueError` CPython raises about the resolved spec. Tests
under `tests/test_types/test_str.py` for both spellings, the nested-spec case,
and the untouched positives (`{}`, `{0}`, `{name}`, `{:.2f}`, `{!r}`,
`{:{width}}`); an `INFECTIONS.md` note beside the runtime dunder guard, which
this joins as its third half.

---

### 5. `MappingProxy` merge leaks `#_data`

**Severity: low (Python leak).**

`MappingProxy.__or__` / `__ror__` (`poop/types/mapping_proxy.py:90`, `:100`)
pick the operand's payload with a conditional whose else-branch is unguarded:

```python
other_data = other._dict._data if isinstance(other, MappingProxy) else other._data
```

Anything that is neither a `MappingProxy` nor a `Dict` reaches `other._data`:

```
{"a": 1}.keys().mapping() | 5   -> int does not understand #_data
```

CPython answers `unsupported operand type(s) for |: 'mappingproxy' and 'int'`.
`Dict.__or__` already guards this way; the proxy was written before that fix and
never got it.

**Solution.** The established shape — guard, then `NotImplemented`:

```python
def __or__(self, other: object) -> Dict:
    from poop.types.dict import Dict

    if not isinstance(other, MappingProxy | Dict):
        return NotImplemented  # foreign operand -> faithful TypeError
    ...
```

Both directions, with a regression test in
`tests/test_types/test_mapping_proxy.py` asserting the message does not name
`#_data`.

---

### 6. A chained comparison is a hidden `and`

**Severity: low (consistency).**

`no_and_or` rejects `x and y` because a conjunction is a message
(`x.and_(lambda: y)`), not an operator. A chained comparison is the same
conjunction with the operator spelled invisibly, and it runs clean:

```bash
printf 'x = 1 < 2 < 3\nx.print()\n' | poop /dev/stdin   # -> True
```

CPython compiles `a < b < c` to `a < b and b < c`, short-circuit included, so
the construct POOP bans is reachable by writing it without the keyword.

**Solution.** Extend `no_and_or` — its message and substitute already fit — with
an `ast.Compare` branch rejecting more than one comparator:

```python
def visit_Compare(self, node: ast.Compare) -> None:
    if len(node.comparators) > 1:
        self.report(
            "a chained comparison is `and` by another spelling — use "
            "(a < b).and_(lambda: b < c) instead",
            node,
        )
    self.generic_visit(node)
```

A single-comparator `Compare` stays untouched, so ordinary `a < b` is
unaffected. Tests in `tests/test_validators/test_no_and_or.py`, plus the
`INFECTIONS.md` row for `no_and_or`. No example relies on a chain.
