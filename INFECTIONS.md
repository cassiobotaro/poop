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
- **Constructor builtins are intercepted, not banned**: `int()`, `float()`, `bool()`, `str()`, `bytes()`, `list()`, `tuple()`, `set()`, `dict()` etc. are class constructors — they ARE object instantiation and fit the OO model. Each transformer intercepts the bare call and rewrites it to return the POOP type via a `_poop_X_from(...)` factory.
- **Dunders exposed as regular methods**: every relevant dunder on a POOP type gets an alias with the Python name without underscores — `__len__` → `len()`, `__abs__` → `abs()`, `__hash__` → `hash()`, etc. Do not translate to Smalltalk names.

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

### No `del` — `poop/validators/no_del.py`

| AST node | Reason |
|---|---|
| `ast.Delete` | objects have no explicit destruction — simply do not delete |

### No subscript — `poop/validators/no_subscript.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Subscript` | slice is not `ast.Slice` | `obj[key]` looks like an operator | `obj.at(key)` |

Slicing `obj[1:3]` (`ast.Slice`) is allowed for now — see backlog (`no_slice`).

### No comprehension — `poop/validators/no_comprehension.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.ListComp` / `ast.SetComp` / `ast.DictComp` / `ast.GeneratorExp` | implicit iteration with procedural look | `col.map(block)`, `col.filter(block)` |

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

### Complex — `poop/transformers/complex.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=complex)` | `_poop_complex_literal(v)` |
| `ast.BinOp` combining real + imaginary literal | collapsed into `_poop_complex_literal(r+ij)` |
| `ast.Call` with `complex(r, i)` | `_poop_complex_from(r, i)` |

### ByteArray — `poop/transformers/byte_array.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `bytearray(x)` | `_poop_bytearray_from(x)` |

### MemoryView — `poop/transformers/memory_view.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `memoryview(x)` | `_poop_memoryview_from(x)` |

### FrozenSet — `poop/transformers/frozen_set.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `frozenset(x)` | `FrozenSet(*x)` or `FrozenSet()` |

### Range — `poop/transformers/range.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `range(stop)` / `range(start, stop)` / `range(start, stop, step)` | `_poop_range(...)` → `Interval` |
