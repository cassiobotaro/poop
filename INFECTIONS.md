# Smalltalk Infections

Infections come in two kinds:
- **Validators** (`poop/validators/`) — reject code incompatible with POOP; follow the `Validator` + `ast.NodeVisitor` pattern.
- **Transformers** (`poop/transformers/`) — rewrite the AST before execution to replace Python constructs with POOP equivalents; follow the `Transformer` + `ast.NodeTransformer` pattern.

Pipeline: `parse → validate → transform → execute(namespace)`

## Principles

- **Everything is an object** and every operation is **message passing**.
- There are no control flow structures — conditionals and iterations are messages sent to objects.
- There are no free functions — all behavior lives in class methods.
- **Message aesthetics**: the central criterion of an infection is not "does it exist in Smalltalk?" but rather "does it look like an object receiving a message?". Operators (`-x`, `not x`, `~x`) and free functions (`len(x)`, `abs(x)`) have a procedural look even when they call methods internally — they must be replaced by `x.negated()`, `x.not_()`, `x.bit_invert()`, `x.len()`, `x.abs()`. POOP code must look like a conversation between objects, not a sequence of operations.
- **Method names in Python, not Smalltalk**: all methods follow the corresponding Python name — builtins, dunders and collection API. `for_each` not `do`, `map` not `collect`, `filter` not `select`, `filter_false` not `reject`, `find` not `detect`, `reduce` not `inject_into`. Smalltalk names are not implemented.
- **Activate validator only when the substitute exists**: blocking without offering an alternative only breaks code without teaching anything. Validators without an implemented substitute live in the backlog until the alternative is ready.
- **Representation**: all POOP types implement `__str__` (and `__repr__` delegates to it). `Transcript.show` calls `str(obj)` internally.
- **`__slots__` on all POOP types**: instance variables are declared in the class definition and fixed — never added dynamically to instances. Runtime *method* extension continues to work normally. Subclasses that need new instance variables can declare their own `__slots__` or omit them.
- **Every literal is transformed**: every literal in Python source (`1`, `3.14`, `"hello"`, `True`, `False`, `None`, `[1, 2]`, `(1, 2)`, `{1, 2}`, `{k: v}`, `b"..."`, `1+2j`) is rewritten by a Transformer into its POOP equivalent before execution — no naked Python primitive ever reaches runtime.
- **Every basic type has a POOP equivalent**: `int` → `Int`, `float` → `Float`, `str` → `Str`, `bool` → `Boolean`, `NoneType` → `NoneClass`, `list` → `List`, `tuple` → `Tuple`, `set` → `Set`, `frozenset` → `FrozenSet`, `dict` → `Dict`, `bytes` → `Bytes`, `bytearray` → `ByteArray`, `complex` → `Complex`. Python native types must not leak into POOP code.
- **All POOP methods return POOP types**: every method on every POOP type must return a POOP object — never a raw Python `int`, `bool`, `str`, `list`, etc. Returning a native type is a bug. *Exception*: Python protocol dunders (`__bool__`, `__hash__`, `__len__`, `__str__`, `__int__`, `__float__`, `__contains__`, `__repr__`) must return native types because Python itself requires it for `if`, `dict`, `len()`, `str()`, etc. to work. The rule applies to all explicitly named POOP methods (`len()`, `hash()`, `not_()`, `includes()`, `tobytes()`, etc.).
- **`True`, `False`, and `None` are singletons**: `true`, `false`, and `none` are unique objects — there is exactly one instance of each. All comparisons and identity checks rely on this guarantee.

## Active infections

### No `if` — `poop/validators/no_if.py`

| AST node | Reason |
|---|---|
| `ast.If` | `if/elif/else` looks like control flow; use `x.if_true(block)` / `x.if_false(block)` |
| `ast.IfExp` | Ternary expression `x if cond else y` — same reason |

### No loops — `poop/validators/no_loops.py`

| AST node | Reason |
|---|---|
| `ast.For` | Loop looks procedural; use `col.for_each(block)`, `col.map(block)`, recursion |
| `ast.While` | Same; use `cond.while_true(block)` |
| `ast.AsyncFor` | Async variant of `for` |

### No free functions — `poop/validators/no_free_functions.py`

| AST node | Context | Reason |
|---|---|---|
| `ast.FunctionDef` | outside class | Free function is not a message to any object |
| `ast.AsyncFunctionDef` | outside class | Async variant |

Functions inside classes (`class_depth > 0`) are allowed as methods.

### No `print` — `poop/validators/no_print.py`

| Call | Reason | Substitute |
|---|---|---|
| `print(...)` | Free function with procedural look | `obj.print()` |

### No `try` — `poop/validators/no_try.py`

| AST node | Reason |
|---|---|
| `ast.Try` | Control structure — procedural look; future substitute: `block.on_error(handler)` |
| `ast.TryStar` | `try/except*` variant (exception groups) |

### No `not` — `poop/validators/no_not.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.UnaryOp` with `ast.Not` | `not x` looks like an operator; it is not a message to `x` | `x.not_()` |

### No unary minus — `poop/validators/no_unary_minus.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.UnaryOp` with `ast.USub` | operand is not `ast.Constant` | `-x` looks like an operator | `x.negated()` |

Negative literals (`-1`, `-3.14`) are allowed — only `-variable` and `-expression` are blocked.

### No bitwise invert — `poop/validators/no_invert.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.UnaryOp` with `ast.Invert` | `~x` looks like an operator | `x.bit_invert()` |

### No `is` / `is not` — `poop/validators/no_is.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Compare` with `ast.Is` | `is` looks like an operator | `x.is_none()` or `x.is_identical(other)` |
| `ast.Compare` with `ast.IsNot` | `is not` looks like an operator | `x.not_none()` or `x.not_identical(other)` |

### No `global`/`nonlocal` — `poop/validators/no_global.py`

| AST node | Reason |
|---|---|
| `ast.Global` | `global` breaks encapsulation — state lives in instances, not in global scope |
| `ast.Nonlocal` | `nonlocal` manipulates outer scope — use instance variables |

### No `yield` — `poop/validators/no_yield.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Yield` | generator has a procedural look for iteration | `col.for_each(block)`, `col.map(block)` |
| `ast.YieldFrom` | same | same |

### No walrus (`:=`) — `poop/validators/no_walrus.py`

| AST node | Reason |
|---|---|
| `ast.NamedExpr` | `:=` combines assignment and expression — use separate assignment |

### No `match/case` — `poop/validators/no_match.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Match` | control structure with procedural look | polymorphism + `if_true(block)`/`if_false(block)` |

### No `len` — `poop/validators/no_len.py`

| Call | Reason | Substitute |
|---|---|---|
| `len(x)` | free function with procedural look | `x.len()` |

### No `abs` — `poop/validators/no_abs.py`

| Call | Reason | Substitute |
|---|---|---|
| `abs(x)` | free function with procedural look | `x.abs()` |

### No `hash` — `poop/validators/no_hash.py`

| Call | Reason | Substitute |
|---|---|---|
| `hash(x)` | free function with procedural look | `x.hash()` |

### No `isinstance` — `poop/validators/no_isinstance.py`

| Call | Reason | Substitute |
|---|---|---|
| `isinstance(x, T)` | free function with procedural look | `x.is_instance(T)` |

### No `callable` — `poop/validators/no_callable.py`

| Call | Reason | Substitute |
|---|---|---|
| `callable(x)` | free function with procedural look | `x.callable()` |

### No `id` — `poop/validators/no_id.py`

| Call | Reason | Substitute |
|---|---|---|
| `id(x)` | free function with procedural look | `x.id()` |

### No `all` — `poop/validators/no_all.py`

| Call | Reason | Substitute |
|---|---|---|
| `all(col)` | free function with procedural look | `col.all(block)` |

### No `any` — `poop/validators/no_any.py`

| Call | Reason | Substitute |
|---|---|---|
| `any(col)` | free function with procedural look | `col.any(block)` |

### No `min`/`max` — `poop/validators/no_min.py`, `poop/validators/no_max.py`

| Call | Reason | Substitute |
|---|---|---|
| `min(a, b)` | free function with procedural look | `a.min(b)` |
| `max(a, b)` | free function with procedural look | `a.max(b)` |

### No `bin`/`hex`/`oct` — `poop/validators/no_bin.py`

| Call | Reason | Substitute |
|---|---|---|
| `bin(n)` | free function with procedural look | `n.bin()` |
| `hex(n)` | free function with procedural look | `n.hex()` |
| `oct(n)` | free function with procedural look | `n.oct()` |

### No `chr`/`ord` — `poop/validators/no_chr.py`

| Call | Reason | Substitute |
|---|---|---|
| `chr(n)` | free function with procedural look | `n.chr()` |
| `ord(c)` | free function with procedural look | `c.ord()` |

### No `divmod` — `poop/validators/no_divmod.py`

| Call | Reason | Substitute |
|---|---|---|
| `divmod(a, b)` | free function with procedural look | `a.divmod(b)` |

### No `pow` — `poop/validators/no_pow.py`

| Call | Reason | Substitute |
|---|---|---|
| `pow(a, b)` | free function with procedural look | `a.pow(b)` |

### No `hasattr` — `poop/validators/no_hasattr.py`

| Call | Reason | Substitute |
|---|---|---|
| `hasattr(x, s)` | free function with procedural look | `x.has_attr(s)` |

### No `format` — `poop/validators/no_format.py`

| Call | Reason | Substitute |
|---|---|---|
| `format(x, spec)` | free function with procedural look | `x.format(spec)` |

### No `slice` — `poop/validators/no_slice.py`

| Call | Reason | Substitute |
|---|---|---|
| `slice(...)` | Python-specific construct | `obj.at(index)` |

### No `enumerate`/`zip` — `poop/validators/no_enumerate.py`

| Call | Reason | Substitute |
|---|---|---|
| `enumerate(col)` | free function with procedural look | `col.map(block)`, `col.reduce(init, block)` |
| `zip(a, b)` | free function with procedural look | same |

### No `iter`/`next` — `poop/validators/no_iter.py`

| Call | Reason | Substitute |
|---|---|---|
| `iter(col)` | iterator protocol with procedural look | `col.for_each(block)` |
| `next(it)` | same | same |
| `aiter(col)` | async variant | same |
| `anext(it)` | async variant | same |

### No `setattr`/`delattr` — `poop/validators/no_setattr.py`

| Call | Reason | Substitute |
|---|---|---|
| `setattr(obj, name, val)` | explicit attribute manipulation | use class methods |
| `delattr(obj, name)` | same | same |

### No introspection — `poop/validators/no_introspection.py`

| Call | Reason |
|---|---|
| `globals()` | scope introspection — state lives in instances |
| `locals()` | same |
| `vars(obj)` | same |
| `dir(obj)` | same |

### No `exec`/`eval`/`compile` — `poop/validators/no_exec.py`

| Call | Reason |
|---|---|
| `exec(code)` | metaprogramming — not allowed in POOP |
| `eval(expr)` | same |
| `compile(src, ...)` | same |

### No `exit`/`quit` — `poop/validators/no_exit.py`

| Call | Reason |
|---|---|
| `exit()` | process control — no POOP equivalent |
| `quit()` | same |

### No `breakpoint` — `poop/validators/no_breakpoint.py`

| Call | Reason |
|---|---|
| `breakpoint()` | Python-specific debugging — no POOP equivalent |

### No `input` — `poop/validators/no_input.py`

| Call | Reason |
|---|---|
| `input(prompt)` | interactive I/O — no POOP equivalent |

### No `open` — `poop/validators/no_open.py`

| Call | Reason |
|---|---|
| `open(path, ...)` | file I/O — no POOP equivalent |

## Active types

### Object — `poop/types/object.py`

Concrete root of all POOP types. Provides default implementations for universal methods:

| Smalltalk message | Method | Behavior |
|---|---|---|
| `isNil` | `is_none()` | always `false` for Object |
| `notNil` | `not_none()` | always `true` for Object |
| `not` | `not_()` | `false if bool(self) else true` |
| `class` | `class_name()` | `type(self).__name__` as `Str` |
| `respondsTo:` | `responds_to(symbol)` | `hasattr` as base |

`__str__` returns `"<ClassName>"` as fallback; `__repr__` delegates to `__str__`.

### NoneClass — `poop/types/none.py`

`NoneClass(Object)` with singleton `none`. Transformer rewrites `ast.Constant(value=None)` → `_poop_none`.

| Method | `Object` | `NoneClass` |
|---|---|---|
| `is_none()` | `false` | `true` |
| `not_none()` | `true` | `false` |
| `if_none(block)` | does not execute | executes block |
| `if_not_none(block)` | executes passing `self` | does not execute |

`__bool__` returns `False`. `__str__` returns `"None"`.

### Boolean — `poop/types/boolean.py`

`Boolean(Object, ABC)` with private subclasses `_TrueClass` and `_FalseClass`. Singletons `true`/`false` replace `True`/`False` via transformer.

| Smalltalk message | Method |
|---|---|
| `ifTrue:` / `ifFalse:` | `if_true(block)` / `if_false(block)` |
| `ifTrue:ifFalse:` / `ifFalse:ifTrue:` | `if_true_if_false(t, f)` / `if_false_if_true(f, t)` |
| `and:` / `or:` (lazy) | `and_(block)` / `or_(block)` |
| `not` / `xor:` / `eqv:` | `not_()` / `xor(other)` / `eqv(other)` |
| `&` / `\|` (eager) | `__and__(other)` / `__or__(other)` |

### Interval — `poop/types/interval.py`

`Interval(Object)` represents a closed integer interval [start, stop]. Created via `Int.to_(limit)`.

| Smalltalk message | POOP method | Behavior |
|---|---|---|
| `do:` | `for_each(block)` | iterates without allocating a list |
| `collect:` | `map(block)` | transforms → `List` |
| `select:` | `filter(block)` | filters → `List` |
| `reject:` | `filter_false(block)` | filters inverse → `List` |
| `detect:` | `find(block)` | first satisfying, or POOP `none` |
| `inject:into:` | `reduce(init, block)` | reduce |
| `len` | `len()` | returns `Int` |

### Object.print — `poop/types/object.py`

All POOP objects inherit `print()` from `Object`. `List` and `Tuple` override to support `sep`.

| Message | Behavior |
|---|---|
| `obj.print()` | prints `str(obj)` followed by `\n` and returns `self` |
| `obj.print(end="")` | controls the terminator |
| `list.print(sep=", ")` | `List`/`Tuple`: joins elements with `sep` (default `" "`) |

`"".print()` prints a blank line. Returning `self` enables cascades: `x.print().print()`.

## Active transformers

### Int — `poop/transformers/int.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=int)` (except `bool`) | `_poop_int(n)` |
| `ast.UnaryOp(USub, Constant(int))` | `_poop_int(-n)` — collapsed negative literal |
| `ast.Call` with `int(x)` or `int(s, base)` | `_poop_int_from(x)` / `_poop_int_from(s, base)` |

### Float — `poop/transformers/float.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=float)` | `_poop_float(n)` |
| `ast.UnaryOp(USub, Constant(float))` | `_poop_float(-n)` — collapsed negative literal |
| `ast.Call` with `float(x)` | `_poop_float_from(x)` |

### Boolean — `poop/transformers/boolean.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=True)` | `_poop_true` |
| `ast.Constant(value=False)` | `_poop_false` |
| `ast.Call` with `bool(x)` | `_poop_bool_from(x)` |

### None — `poop/transformers/none.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=None)` | `_poop_none` |

### Str — `poop/transformers/string.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=str)` | `_poop_str(s)` |
| `ast.Call` with `str(x)` | `_poop_str_from(x)` |

### Bytes — `poop/transformers/bytes.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=bytes)` | `_poop_bytes(b)` |
| `ast.Call` with `bytes(x)` or `bytes(s, enc)` | `_poop_bytes_from(x)` / `_poop_bytes_from(s, enc)` |

### List — `poop/transformers/list.py`

| AST node | Replacement |
|---|---|
| `ast.List` (Load context) | `_poop_list(*elts)` |
| `ast.Call` with `list(x)` | `_poop_list_from(x)` |

### Tuple — `poop/transformers/tuple.py`

| AST node | Replacement |
|---|---|
| `ast.Tuple` (Load context) | `_poop_tuple(*elts)` |
| `ast.Call` with `tuple(x)` | `_poop_tuple_from(x)` |

### Set — `poop/transformers/set.py`

| AST node | Replacement |
|---|---|
| `ast.Set` | `_poop_set(*elts)` |
| `ast.Call` with `set(x)` | `_poop_set_from(x)` |

### Dict — `poop/transformers/dict.py`

| AST node | Replacement |
|---|---|
| `ast.Dict` (no unpacking) | `_poop_dict_from_pairs(k1, v1, k2, v2, …)` |
| `ast.Call` with `dict(x)` | `_poop_dict_from(x)` — `x` must be `Dict` or iterable of 2-element `Tuple`/`List` pairs |

### No `del` — `poop/validators/no_del.py`

| AST node | Reason |
|---|---|
| `ast.Delete` | objects have no explicit destruction — simply do not delete |

### No subscript — `poop/validators/no_subscript.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Subscript` | slice is not `ast.Slice` | `obj[key]` looks like an operator | `obj.at(key)` |

Slicing `obj[1:3]` (`ast.Slice`) is allowed for now — see backlog (`no_slice`).

### Str — `poop/transformers/str.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=str)` | `_poop_str(s)` |

### ~~TODO — operations that return native boolean~~

- ~~Comparisons (`==`, `!=`, `<`, `>`, `<=`, `>=`) — still returning native Python `bool` instead of POOP `Boolean`~~
- Resolved: `Object.__eq__`/`__ne__` return `Boolean` by identity; subclasses (`Int`, `Float`, `Str`, `Interval`) override with value logic.

## Backlog

### Validators — awaiting implementation

None pending.

### Validators — awaiting substitute

| Construct | Validator | Pending substitute |
|---|---|---|
| `raise` | `no_raise.py` | `Error` with `.signal()` |
| `with` / `async with` | `no_with.py` | `on_do` mechanism |
| `assert` | `no_assert.py` | `assert_:` in test framework |

### Next types

- ~~**`List`**: replaces `list`; messages `for_each(block)`, `map(block)`, `filter(block)`, `filter_false(block)`, `find(block)`, `reduce(init, block)`, `add(obj)`, `len()`, `includes(obj)`. When implemented, `Interval.map`/`filter`/`filter_false` start returning `List`.~~ — implemented (Smalltalk names — rename, see Pending renames).
- ~~**`Tuple`**: replaces `tuple`; immutable; messages `len()`, `at(index)`, `for_each(block)`, `map(block)`, `filter(block)`, `filter_false(block)`, `find(block)`, `reduce(init, block)`, `includes(obj)`. Transformer rewrites `(a, b, c)` literals → `Tuple`.~~ — implemented (Smalltalk names — rename, see Pending renames).
- **[HIGH PRIORITY] `Error`**: base class for POOP exceptions. **Critical dependency**: unblocks `no_raise`, `no_with` and `no_assert` — while `Error` does not exist, POOP code can freely use `raise` and `with`, without protection from the principles. Design decisions still open — see Open decisions section (exception hierarchy strategy, `raise_` naming, interaction with existing Python exceptions).
- ~~**`Dict`**~~: implemented — `at(key)`, `at_put(key, val)`, `includes_key(key)`, `keys()`, `values()`, `for_each(block)` (receives `Tuple(key, value)`), `len()`. Transformer rewrites `{k: v}` literals → `Dict`.
- ~~**`Set`**~~: implemented — `includes(obj)`, `add(obj)`, `remove(obj)` (discard semantics, no error if absent), `len()`, `for_each(block)`, `map(block)`, `filter(block)`, `filter_false(block)`, `find(block)`, `reduce(init, block)`, `all(block)`, `any(block)`. Transformer rewrites `{a, b}` literals → `Set`. Empty `{}` literal is dict — use `_poop_set()` for empty set.
- ~~**`FrozenSet`**~~: implemented — immutable version of `Set`. `includes(obj)`, `len()`, `for_each(block)`, `map(block)`, `filter(block)`, `filter_false(block)`, `find(block)`, `reduce(init, block)`, `all(block)`, `any(block)`. Hashable (can be used as `Dict` key). Transformer rewrites `frozenset(iterable)` → `FrozenSet(*iterable)` and `frozenset()` → `FrozenSet()`.
- ~~**`Complex`**: replaces `complex`; messages `real()`, `imag()`, `conjugate()`, `abs()`. Literals `complex(r, i)` → `Complex`. Transformer rewrites `j`-literals (`1+2j`) → `Complex`. Low priority — scientific/niche use.~~
- ~~**`Bytes`**~~: implemented — immutable, hashable (can be used as `Dict` key). Messages `len()`, `at(index)` → `Int`, `includes(byte: Int)` → `Boolean`, `decode(encoding: Str)` → `Str`, `hex()` → `Str`, `for_each(block)`, `map(block)` → `List`. Transformer rewrites `b"..."` literals → `Bytes`.
- ~~**`ByteArray`**: replaces `bytearray`; mutable version of `Bytes` — analogous relationship to `List`/`Tuple`. Messages `len()`, `at(index)`, `at_put(index, byte)`, `includes(byte)`, `decode(encoding)`, `hex()`, `for_each(block)`. Implement after `Bytes`.~~
- ~~**`MemoryView`**: replaces `memoryview`; wrapper over bytes buffer. Messages `len()`, `at(index)`, `for_each(block)`. Low priority — scientific/niche use. Implement after `Bytes`/`ByteArray`.~~
- **`Str` — missing methods**: none. All dunders and string methods are implemented.
- **`Interval` — missing methods**: none. All methods are implemented.

### Next transformers

- ~~List literals (`ast.List`) → `List`.~~ — implemented via ListTransformer.
- ~~Tuple literals (`ast.Tuple`) → `Tuple`.~~ — implemented via TupleTransformer.
- ~~Dict literals (`ast.Dict`) → `Dict`.~~
- ~~Set literals (`ast.Set`) → `Set`.~~
- ~~`range(...)` → `Interval`.~~ — implemented via RangeTransformer.
- ~~`len(x)` → `x.len()`~~ — ban via validator with suggestion; see Builtins section.
- ~~`abs(x)` → `x.abs()`~~ — ban via validator with suggestion; see Builtins section.
- ~~`isinstance(x, T)` → `x.is_instance(T)`~~ — ban via validator; use `x.is_instance(T)`.
- ~~`hasattr(x, s)` → `x.has_attr(s)`~~ — ban via validator; use `x.has_attr(s)`.
- ~~`callable(x)` → `x.callable()`~~ — ban via validator; use `x.callable()`.
- ~~Comparisons (`==`, `!=`, `<`, `>`, `<=`, `>=`) → return `TrueClass`/`FalseClass`.~~ — implemented via `Object.__eq__`/`__ne__` and overrides in subclasses.

### Python builtins — complete map

#### Transform (rewrite to message to object)

| Builtin | POOP equivalent | Status |
|---|---|---|
| `round(x)` | `x.round()` | ✓ in Int/Float |
| `str(x)` | calls `__str__` | ✓ works |
| `int(x)` | `x.int()` | ✓ in Int, Float, Str |
| `float(x)` | `x.float()` | ✓ in Int, Float, Str |
| `type(x)` | `x.class_name()` | ✓ in Object |
| `reversed(x)` | `x.reversed()` | ✓ in Interval, Str |
| `sorted(x)` | `x.sorted()` | pending in List, Tuple |
| `map(f, col)` | `col.map(f)` | ✓ (rename — see Pending renames) |
| `filter(f, col)` | `col.filter(f)` | ✓ (rename — see Pending renames) |

#### Ban (validator)

| Builtin | Reason |
|---|---|
| `print` | ✓ blocked — use `obj.print()` |
| `len(x)` | ✓ blocked — use `x.len()` |
| `abs(x)` | ✓ blocked — use `x.abs()` |
| `range(n)` | ✓ rewritten → `Interval` via RangeTransformer |
| `hash(x)` | ✓ blocked — use `x.hash()` |
| `id(x)` | ✓ blocked — use `x.id()` |
| `all(col)` | ✓ blocked — use `col.all(block)` |
| `any(col)` | ✓ blocked — use `col.any(block)` |
| `min(a, b)` / `max(a, b)` | ✓ blocked — use `a.min(b)` / `a.max(b)` |
| `isinstance(x, T)` | ✓ blocked — use `x.is_instance(T)` |
| `hasattr(x, s)` | ✓ blocked — use `x.has_attr(s)` |
| `callable(x)` | ✓ blocked — use `x.callable()` |
| `divmod(a, b)` | ✓ blocked — use `a.divmod(b)` |
| `pow(a, b)` | ✓ blocked — use `a.pow(b)` |
| `bin(n)` / `hex(n)` / `oct(n)` | ✓ blocked — use `n.bin()` / `n.hex()` / `n.oct()` |
| `chr(n)` / `ord(c)` | ✓ blocked — use `n.chr()` / `c.ord()` |
| `input` | ✓ blocked — I/O with no POOP substitute |
| `open` | ✓ blocked — I/O with no POOP substitute |
| `exec` / `eval` / `compile` | ✓ blocked — metaprogramming |
| `breakpoint` | ✓ blocked — Python-specific debugging |
| `exit` / `quit` | ✓ blocked — process control |
| `globals` / `locals` / `vars` / `dir` | ✓ blocked — use instances |
| `setattr` / `delattr` | ✓ blocked — use class methods |
| `iter` / `next` / `aiter` / `anext` | ✓ blocked — use `col.for_each(block)` |
| `enumerate` / `zip` | ✓ blocked — use `col.map(block)` / `col.reduce(init, block)` |
| `slice` | ✓ blocked — use `obj.at(index)` |
| `format` | ✓ blocked — use `obj.format(spec)` |
| `ascii` | Python-specific |

#### Constructor builtins (intercepted by transformers)

Constructors (`int`, `float`, `bool`, `str`, `bytes`, `list`, …) are **not banned** — they are OO (class instantiation). Instead, each transformer intercepts the call and returns the POOP equivalent. See each transformer section in "Active transformers" for details.

| Builtin | Status |
|---|---|
| `int(x)` / `int(s, base)` | ✓ rewritten → `_poop_int_from(x)` (IntTransformer) |
| `float(x)` | ✓ rewritten → `_poop_float_from(x)` (FloatTransformer) |
| `bool(x)` | ✓ rewritten → `_poop_bool_from(x)` (BooleanTransformer) |
| `str(x)` | ✓ rewritten → `_poop_str_from(x)` (StrTransformer) |
| `bytes(x)` / `bytes(s, enc)` | ✓ rewritten → `_poop_bytes_from(x)` (BytesTransformer) |
| `list(x)` | ✓ rewritten → `_poop_list_from(x)` (ListTransformer) |
| `tuple(x)` | ✓ rewritten → `_poop_tuple_from(x)` (TupleTransformer) |
| `set(x)` | ✓ rewritten → `_poop_set_from(x)` (SetTransformer) |
| `dict(x)` | ✓ rewritten → `_poop_dict_from(x)` (DictTransformer) |
| `frozenset(x)` | ✓ rewritten by FrozenSetTransformer |
| `complex(r, i)` | ✓ rewritten by ComplexTransformer |
| `bytearray(x)` | ✓ rewritten by ByteArrayTransformer |
| `memoryview(x)` | ✓ rewritten by MemoryViewTransformer |

#### Allow / Decide later

| Builtin | Note |
|---|---|
| `super` | needed for inheritance |
| `property` / `classmethod` / `staticmethod` | class definition |
| `getattr` | used internally by `responds_to` |
| `issubclass` | evaluate alongside `isinstance` |
| `repr` | delegates to `__repr__` → `__str__` |
| `sum` | use `reduce(0, block)` — ban when transformer exists |

### Bugs / inconsistencies

- ~~**`Interval.detect` returns native `None`**~~ ✓ fixed.
- ~~**`Object.class_name()` returns native `str`**~~ ✓ fixed.
- **Built-in functions** (`len`, `isinstance`, `hasattr`, `callable`) leak native Python types into the POOP model.
- ~~**`Str.split()` returns Python `list`**~~ ✓ fixed — returns POOP `List`.
- ~~**`Str.join()` accepts Python `list[Str]`**~~ ✓ fixed — accepts POOP `List`.
- ~~**`__repr__` missing in Int, Float, Str, Interval, List, Tuple, NoneClass**~~ — fixed: `__repr__ = __str__` present in all types.

### Missing validators

- ~~**[HIGH PRIORITY] `no_subscript`**~~: implemented — blocks `obj[key]`, slicing `obj[1:3]` allowed for now (see item below).
- **`no_slice`**: slicing `obj[1:3]` looks like an operator but has no defined substitute yet — candidate: `obj.from_to(start, stop)`. Activate after deciding the name and implementing the method.
- **`slice` as a Python class**: `slice` is a built-in class (`slice(1, 3, 2)` creates an object with `.start`, `.stop`, `.step`). Worth considering whether POOP should have its own `Slice` type, or if slicing should simply be banned without an object substitute. The current `no_slice` only blocks the `slice(...)` call, not the use of the type in annotations or `isinstance`.
- **[MEDIUM PRIORITY] ~~`no_comprehension`~~**: implemented — blocks `ast.ListComp`, `ast.SetComp`, `ast.DictComp`, `ast.GeneratorExp`. Substitutes: `col.map(block)`, `col.filter(block)` (after renaming).
- **[MEDIUM PRIORITY] `no_augmented_assign`**: `x += 1`, `x -= 1` etc. are not blocked — `ast.AugAssign`. Very frequent construct; the absence of blocking creates an implicit exception to the message model.
- **`no_import`**: `import os` inside POOP code is not blocked — decide whether to ban or restrict.
- **`no_raise`** and **`no_assert`**: blocked by `Error` — validators cannot be activated before the `Error` type exists (see Next types section).

### Missing methods in existing types

- **[MEDIUM PRIORITY] Python API parity audit**: review every POOP type against its Python counterpart and add any missing methods. Each POOP type should expose all meaningful methods of the Python class it wraps, following the naming rule (Python names, not Smalltalk). Types to audit: `Int` (`int`), `Float` (`float`), `Str` (`str`), `List` (`list`), `Tuple` (`tuple`), `Dict` (`dict`), `Set` (`set`), `FrozenSet` (`frozenset`), `Bytes` (`bytes`), `ByteArray` (`bytearray`), `Complex` (`complex`), `Interval` (`range`).
  - **`Int`**: `as_integer_ratio()` → `Tuple(Int, Int)`, `conjugate()` → self, `denominator()` → `Int(1)`, `imag()` → `Int(0)`, `numerator()` → self, `real()` → self, `to_bytes(length, byteorder)` → `Bytes`.
  - **`Float`**: `conjugate()` → self, `hex()` → `Str`, `imag()` → `Float(0.0)`, `real()` → self.
  - **`Str`**: `casefold()`, `center(width)`, `encode(encoding)` → `Bytes`, `expandtabs()`, `isascii()`, `isdecimal()`, `isidentifier()`, `isnumeric()`, `isprintable()`, `istitle()`, `ljust(width)`, `partition(sep)` → `Tuple`, `removeprefix(prefix)`, `removesuffix(suffix)`, `rfind(sub)`, `rindex(sub)`, `rjust(width)`, `rpartition(sep)` → `Tuple`, `rsplit(sep)`, `splitlines()`, `zfill(width)`.
  - **`List`**: `clear()`, `copy()` → `List`, `count(obj)` → `Int`, `extend(other)`, `index(obj)` → `Int`, `insert(i, obj)`, `remove(obj)`, `reverse()`, `sort(key, reverse)`.
  - **`Tuple`**: `count(obj)` → `Int`, `index(obj)` → `Int`.
  - **`Dict`**: `clear()`, `copy()` → `Dict`, `items()` → `List` of `Tuple(key, val)`, `pop(key)`, `popitem()` → `Tuple`, `setdefault(key, default)`, `update(other)`.
  - **`Set`**: `clear()`, `copy()` → `Set`, `difference(*others)`, `difference_update(*others)`, `discard(obj)`, `intersection(*others)`, `intersection_update(*others)`, `isdisjoint(other)` → `Boolean`, `issubset(other)` → `Boolean`, `issuperset(other)` → `Boolean`, `pop()`, `symmetric_difference(other)`, `symmetric_difference_update(other)`, `union(*others)`, `update(*others)`.
  - **`FrozenSet`**: `copy()` → `FrozenSet`, `difference(*others)`, `intersection(*others)`, `isdisjoint(other)` → `Boolean`, `issubset(other)` → `Boolean`, `issuperset(other)` → `Boolean`, `symmetric_difference(other)`, `union(*others)`.
  - **`Bytes`**: `capitalize()`, `center(width)`, `count(sub)`, `endswith(suffix)`, `expandtabs()`, `find(sub)`, `index(sub)`, `isalnum()`, `isalpha()`, `isascii()`, `isdigit()`, `islower()`, `isspace()`, `istitle()`, `isupper()`, `join(iterable)`, `ljust(width)`, `lower()`, `lstrip()`, `partition(sep)`, `removeprefix(prefix)`, `removesuffix(suffix)`, `replace(old, new)`, `rfind(sub)`, `rindex(sub)`, `rjust(width)`, `rpartition(sep)`, `rsplit(sep)`, `rstrip()`, `split(sep)`, `splitlines()`, `startswith(prefix)`, `strip()`, `swapcase()`, `title()`, `upper()`, `zfill(width)`.
  - **`ByteArray`**: tudo acima de `Bytes`, mais: `append(byte)`, `clear()`, `copy()` → `ByteArray`, `extend(iterable)`, `insert(i, byte)`, `pop(index)`, `remove(byte)`, `resize(size)`, `reverse()`.
  - **`Interval`**: `count(value)` → `Int`, `index(value)` → `Int`, `start()` → `Int`, `stop()` → `Int`, `step()` → `Int`.
- **`List.sorted()` / `List.reversed()`**: return a new sorted/reversed copy. `Interval` has `reversed()`; `List` and `Tuple` do not.
- **`Tuple.sorted()` / `Tuple.reversed()`**: same.
- ~~**`Int.times(block)`**~~: removed — `times` and `timesRepeat:` are Smalltalk names with no Python `int` equivalent.
- ~~**`Int.divmod(other)` / `Float.divmod(other)` → `Tuple`**~~: implemented.

### Pending renames (Smalltalk names → Python names)

None pending.

### Architecture / DX

- **REPL**: interactive loop — `poop` with no arguments opens the REPL.
- **Richer error messages**: `ValidationError` could suggest the POOP equivalent (e.g., `"use x.not_() instead of 'not x'"`).

### Code examples

- Expand `examples/` with collections: `List`, `Tuple`, `Interval` with `map`/`filter`/`filter_false`.

### ~~CLI as installable entry point~~ ✓ (done)


## Open decisions

- **Exception system design**: POOP blocks `raise`/`try` but the `Error` type and its interaction with Python's existing exception hierarchy is unresolved. Three strategies were considered:
  - **A — Generic wrapper**: `on_error` wraps any caught exception in a single `Error(e)` POOP object. Simple, but loses hierarchy — cannot distinguish `ValueError` from `KeyError` in the handler.
  - **B — Mirrored POOP hierarchy**: POOP defines its own `ValueError`, `KeyError`, `TypeError` etc., each inheriting from both `Error` (POOP) and the corresponding Python exception. Preserves hierarchy and `isinstance` checks, but requires wrapping every Python exception class — impractical given the size of the hierarchy.
  - **C — Python types as selector, POOP wrapper in handler** *(recommended)*: `on_error(exc_type, handler)` accepts a native Python exception class as the type selector (used directly in `except`), but wraps the caught exception in a POOP `Error` object before passing to the handler. Pragmatic and compatible with the full Python exception ecosystem; the only leak is the exception class reference used as argument.
  - For raising: `Error("msg", ValueError).raise_()` — `Error` wraps a Python exception instance and `raise_()` re-raises it. Avoids transforming every exception constructor; the `Error` constructor accepts an optional Python exception class as kind. The keyword `raise` is banned by `no_raise`; `raise_` follows PEP 8 keyword escape (same problem as `for_each`/`while_true` — see naming strategy decision).
  - For resumable exceptions (Smalltalk-style `e resume: value`): not planned — Python's exception model does not support resumption natively.

- **Naming strategy for Python keyword → method**: `for`, `while`, `in` are Python keywords that cannot be used as method names. POOP currently handles them inconsistently: `for` → `for_each` (Java/JS compound), `while` → `while_true` (descriptive compound), `in` → `includes` (semantic equivalent from `__contains__`). Three approaches exist: (1) PEP 8 trailing underscore — `for_`, `while_`, `in_` — mechanical but ugly; (2) descriptive compound — `for_each`, `while_true` — readable but not Python names; (3) semantic equivalent — `includes`, `contains` — most Pythonic but requires case-by-case judgment. A consistent rule should be decided before adding new keyword-derived methods.

- **`while_true` not yet implemented**: `no_loops` blocks `ast.While` and documents `cond.while_true(block)` as the substitute, but `Boolean` does not implement `while_true`. The validator is active without a working substitute — violates the principle "activate validator only when the substitute exists". Implement `while_true(block)` on `Boolean` (and decide what it returns) before this is considered complete.

- **`in` operator not blocked**: `x in col` uses `__contains__` internally and is not rejected by any validator. POOP has `col.includes(x)` as the message-passing equivalent, but the operator form still works — a silent inconsistency. Decide: add a `no_in` validator (blocked until `includes` is confirmed as the canonical substitute on all collection types), or explicitly allow `in` as syntactic sugar for `__contains__`.

- **`for_each` vs `for_`**: iteration method is named `for_each` because `for` is a Python keyword and `def for(...)` is a syntax error. `for_` (PEP 8 trailing-underscore convention) was rejected because it reads awkwardly (`col.for_(block)`). `for_each` is semantically clear but not a Python builtin name — it comes from Java/JavaScript tradition, which is a mild violation of the "Python names, not Smalltalk" principle. Worth revisiting when the broader keyword naming strategy (see above) is decided.

- **Classmethods as POOP messages**: some Python built-in types expose useful classmethods — `int.from_bytes(b, byteorder)`, `float.fromhex(s)`, `bytes.fromhex(s)`, `dict.fromkeys(keys)`. These cannot be expressed as messages to an instance; the receiver would be the class itself. Two questions to resolve: (1) should POOP support sending messages to class objects at all, and (2) if so, should the transformer pipeline intercept `Int.from_bytes(...)` as a special call form (attribute access on a class name) and rewrite it to a factory function? Until decided, these methods are excluded from the Python API parity audit.

- **Constructor builtins are intercepted, not banned**: `int()`, `float()`, `bool()`, `str()`, `bytes()`, `list()`, `tuple()`, `set()`, `dict()` etc. are class constructors — they ARE object instantiation and fit the OO model. The rule is: each transformer intercepts the bare call (no method receiver) and rewrites it to return the POOP type. The factory function (`_poop_X_from`) handles type dispatch and raises `TypeError` for unsupported input types.

- **Dunders exposed as regular methods**: every relevant dunder on a POOP type gets an alias with the Python name without underscores — `__len__` → `len()`, `__abs__` → `abs()`, `__contains__` → `contains()`, `__iter__` → `iter()`, `__hash__` → `hash()`, etc. The rule is: remove the underscores, keep the Python name — do not translate to Smalltalk. Smalltalk names (`size()`, `identity_hash()`, etc.) are not implemented.
- **`isEmpty` will not be implemented in `Str`**: use `obj == ''` — calls `Str.__eq__` and returns POOP `Boolean`.
- **`List.join` / `Tuple.join` will not be implemented**: Python `list` has no `join` — the correct idiom is `Str(sep).join(list)`, which already exists.
- **`Transcript` removed**: was a Smalltalk remnant with no Python equivalent. The correct POOP idiom is the object receiving the message: `obj.print()`. `Object.print()` returns `self` for cascades; `List`/`Tuple` override with `sep` parameter. `"".print()` replaces `Transcript.nl()`.
- **`as_string()` / `printString` will not be implemented**: use `str(obj)` — calls `__str__` on each POOP type.
- **Lambdas** (`ast.Lambda`): analogous to Smalltalk blocks — **allowed**.
- **Comprehensions** (`ast.ListComp`, `ast.SetComp`, `ast.DictComp`, `ast.GeneratorExp`): contain implicit iteration — evaluate whether they should be banned along with loops.
- **Augmented / multiple assignment**: evaluate consistency with the object model.
- **`import`** (`ast.Import`, `ast.ImportFrom`): evaluate whether to ban or restrict to POOP module imports.
