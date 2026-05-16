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
- **Method names in Python, not Smalltalk**: all methods follow the corresponding Python name — builtins, dunders and collection API. `map` not `collect`, `filter` not `select`, `filter_false` not `reject`, `find` not `detect`. Smalltalk names are not implemented. **Exception**: iteration uses `do` (from Smalltalk `do:`) instead of `for_each` — `for` is a Python keyword and `for_each` is a Java/JS idiom with no Python equivalent; `do` is the canonical Smalltalk message for iteration and reads naturally as a message to an object. It returns `none`, like a `for` loop. Folds use `reduce(init, block)` (Smalltalk's `inject:into:`); it is named `reduce` after `functools.reduce`, which is the Python name for the same operation.
- **Activate validator only when the substitute exists**: blocking without offering an alternative only breaks code without teaching anything. Validators without an implemented substitute live in `proposals.md` until the alternative is ready. *Exception*: **definitive bans** — constructs with no possible substitute inside POOP's model (`exec`/`eval`/`compile`, `exit`/`quit`, `breakpoint`, `globals`/`locals`/`vars`, `open`) are activated without a substitute and tracked under `proposals.md` § "Stay banned (no proposal)".
- **Representation**: all POOP types implement `__str__` (and `__repr__` delegates to it). `Object.print` calls `str(obj)` internally — every printed message goes through the type's own representation.
- **`__slots__` on all POOP types**: instance variables are declared in the class definition and fixed — never added dynamically to instances. Runtime *method* extension continues to work normally. Subclasses that need new instance variables can declare their own `__slots__` or omit them.
- **Every literal is transformed**: every literal in Python source (`1`, `3.14`, `"hello"`, `True`, `False`, `None`, `[1, 2]`, `(1, 2)`, `{1, 2}`, `{k: v}`, `b"..."`, `1+2j`) is rewritten by a Transformer into its POOP equivalent before execution — no naked Python primitive ever reaches runtime.
- **Every basic type has a POOP equivalent**: `int` → `Int`, `float` → `Float`, `str` → `Str`, `bool` → `Boolean`, `NoneType` → `NoneClass`, `list` → `List`, `tuple` → `Tuple`, `set` → `Set`, `frozenset` → `FrozenSet`, `dict` → `Dict`, `bytes` → `Bytes`, `bytearray` → `ByteArray`, `memoryview` → `MemoryView`, `complex` → `Complex`. Python native types must not leak into POOP code.
- **All POOP methods return POOP types**: every method on every POOP type must return a POOP object — never a raw Python `int`, `bool`, `str`, `list`, etc. Returning a native type is a bug. *Exception*: Python protocol dunders (`__bool__`, `__hash__`, `__len__`, `__str__`, `__int__`, `__float__`, `__contains__`, `__repr__`) must return native types because Python itself requires it for `if`, `dict`, `len()`, `str()`, etc. to work. The rule applies to all explicitly named POOP methods (`len()`, `hash()`, `not_()`, `includes()`, `tobytes()`, etc.).
- **Mutators named after Python void-returning methods return `none`**: methods that mirror Python counterparts returning `None` (e.g., `list.append`, `set.add`, `dict.update`, `bytearray.reverse`) must return POOP `none`, not `self`. This preserves the Python mirror contract — `result = lst.append(x)` leaves `result` as `none`, matching what a Python programmer expects. POOP-specific methods with no Python equivalent (e.g., `List.add`, `Dict.at_put`, `ByteArray.at_put`) may still return `self` for chaining.
- **`True`, `False`, and `None` are singletons**: `true`, `false`, and `none` are unique objects — there is exactly one instance of each. All comparisons and identity checks rely on this guarantee.
- **Constructor builtins are intercepted, not banned**: `int()`, `float()`, `bool()`, `str()`, `bytes()`, `list()`, `tuple()`, `set()`, `dict()` etc. are class constructors — they ARE object instantiation and fit the OO model. Each transformer intercepts the bare call and rewrites it to return the POOP type via a `_poop_X_from(...)` factory.
- **Dunders exposed as regular methods**: every relevant dunder on a POOP type gets an alias with the Python name without underscores — `__len__` → `len()`, `__abs__` → `abs()`, `__hash__` → `hash()`, etc. Do not translate to Smalltalk names.
- **Namespace hygiene — POOP types pass as Python builtins**: every wrapper class (`Int`, `List`, `Object`, …) is bound under a mangled `_poop_*` name and unreachable from user code (enforced by `no_poop_prefix`). The bare Python builtin (`int`, `list`, `object`, …) is rewritten at parse time to the corresponding mangled name. Each wrapper additionally patches `__module__ = "builtins"` and `__name__ = "<lowercase>"`, so `repr(Int)` reads `<class 'int'>` and `Int(5).class_name()` returns `Str("int")` — POOP builtins answer to the same names Python builtins do. True entry points without an AST rewrite or method equivalent fall in two camps: **POOP-specific constructs** (`Try`, `With`, `Path`) keep PascalCase, and **Python stdlib module mirrors** (`math`, `random`, …) keep lowercase to match the source module names. A module that also exposes a class (e.g., `random` ⊃ `Random`) binds both — the lowercase name for module-level entry, the PascalCase name for the class constructor.

## Active infections

### No `if` — `poop/validators/no_if.py`

| AST node | Reason |
|---|---|
| `ast.If` | `if/elif/else` looks like control flow; use `x.if_true(block)` / `x.if_false(block)` |
| `ast.IfExp` | Ternary expression `x if cond else y` — same reason |

### No loops — `poop/validators/no_loops.py`

| AST node | Reason |
|---|---|
| `ast.For` | Loop looks procedural; use `col.do(block)`, `col.map(block)`, recursion |
| `ast.While` | Same; use `(lambda: cond).while_true(lambda: body)` |
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

### No `assert` — `poop/validators/no_assert.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Assert` | Statement — not a message to any object | `obj.assert_('message')` (any truthy receiver) |

### No `raise` — `poop/validators/no_raise.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Raise` | `raise` is a statement — not a message to any object | `ExcType.raise_('msg')` |

### No `try` — `poop/validators/no_try.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Try` | Control structure — procedural look | `Try(block).except_(ExcType, handler).run()` |
| `ast.TryStar` | `try/except*` variant (exception groups) | same |

### No `with` — `poop/validators/no_with.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.With` | Control structure — procedural look | `With(lambda: cm()).do(lambda resource: body)` |
| `ast.AsyncWith` | `async with` variant | same |

### No `and`/`or` — `poop/validators/no_and_or.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.BoolOp` with `ast.And` | `x and y` looks like an operator | `x.and_(lambda: y)` |
| `ast.BoolOp` with `ast.Or` | `x or y` looks like an operator | `x.or_(lambda: y)` |

`and_` and `or_` receive a block so evaluation is lazy — the right-hand side is only evaluated if needed, preserving the short-circuit semantics of Python's `and`/`or`.

### No `async`/`await` — `poop/validators/no_async.py`

| AST node | Reason |
|---|---|
| `ast.AsyncFunctionDef` | async functions imply an event loop — POOP has no event loop |
| `ast.Await` | same |

`ast.AsyncFor` is also banned by the loops validator. `ast.AsyncFunctionDef` *outside* a class is additionally covered by the free-functions validator; `no_async` handles the case where an `async def` appears *inside* a class method.

### No `not` — `poop/validators/no_not.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.UnaryOp` with `ast.Not` | `not x` looks like an operator; it is not a message to `x` | `x.not_()` |

### No unary minus — `poop/validators/no_unary_minus.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.UnaryOp` with `ast.USub` | operand is not `ast.Constant` | `-x` looks like an operator | `x.negated()` |

Negative literals (`-1`, `-3.14`) are allowed — only `-variable` and `-expression` are blocked.

### No unary plus — `poop/validators/no_unary_plus.py`

| AST node | Reason |
|---|---|
| `ast.UnaryOp` with `ast.UAdd` | `+x` is semantically a no-op and has no message-send equivalent — write the value directly |

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
| `ast.Yield` | generator has a procedural look for iteration | `col.do(block)`, `col.map(block)` |
| `ast.YieldFrom` | same | same |

### No walrus (`:=`) — `poop/validators/no_walrus.py`

| AST node | Reason |
|---|---|
| `ast.NamedExpr` | `:=` combines assignment and expression — use separate assignment |

### No `type` alias — `poop/validators/no_type_alias.py`

| Construct | Reason |
|---|---|
| `type X = int` | Creates an alias for a Python builtin type — incompatible with POOP runtime types |

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

### No `repr` — `poop/validators/no_repr.py`

| Call | Reason | Substitute |
|---|---|---|
| `repr(x)` | free function with procedural look | `x.repr()` |

### No `ascii` — `poop/validators/no_ascii.py`

| Call | Reason | Substitute |
|---|---|---|
| `ascii(x)` | free function with procedural look | `x.ascii()` |

### No `issubclass` — `poop/validators/no_issubclass.py`

| Call | Reason | Substitute |
|---|---|---|
| `issubclass(A, B)` | free function with procedural look | `A.is_subclass(B)` |

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
| `min(a, b)` | free function with procedural look | `a.min(b)` (binary, on `Int`/`Float`) |
| `min(iterable)` | free function with procedural look | `iterable.min()` |
| `min(iterable, key=fn)` | free function with procedural look | `iterable.min(key=fn)` |
| `min(iterable, default=x)` | free function with procedural look | `iterable.min(default=x)` |
| `min(a, b, c, ...)` | free function with procedural look | `[a, b, c].min()` or chain `a.min(b).min(c)` |

`max` mirrors `min` exactly. The iterable form lives on
`_IterableMixin` (covers `List`, `Tuple`, `Set`, `FrozenSet`,
`Range`, `Bytes`, `ByteArray`, `MemoryView`, `Enumerate`, `Zip`)
plus direct implementations on `Str` (smallest/largest character)
and `Dict` (smallest/largest key). Empty iterable without `default`
raises `ValueError`, mirroring Python.

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

### No `getattr` — `poop/validators/no_getattr.py`

| Call | Reason | Substitute |
|---|---|---|
| `getattr(x, name)` | free function with procedural look | `x.get_attr(name)` |
| `getattr(x, name, default)` | free function with procedural look | `x.get_attr(name, default)` |

### No `hasattr` — `poop/validators/no_hasattr.py`

| Call | Reason | Substitute |
|---|---|---|
| `hasattr(x, s)` | free function with procedural look | `x.has_attr(s)` |

### No `format` — `poop/validators/no_format.py`

| Call | Reason | Substitute |
|---|---|---|
| `format(x, spec)` | free function with procedural look | `x.format(spec)` |

### `zip` → `Zip` — `poop/transformers/zip.py`

`zip(a, b, ...)` and `zip(a, b, strict=True)` are rewritten by `ZipTransformer` to `_poop_zip(...)`, which returns a `Zip` object.

`Zip` (`poop/types/zip.py`) is a lazy iterable POOP type mirroring Python's `zip` exactly: accepts any number of iterables, stops at the shortest, raises `ValueError` when `strict=true` and lengths differ, and raises `TypeError` eagerly on construction if any source is not iterable (matches Python's `'X' object is not iterable`). It inherits `do`, `map`, `filter`, `filter_false`, `find`, `sum`, `all`, `any` from `_IterableMixin`. Every `_IterableMixin` type and `Dict` expose `.zip(*others, strict=false) -> Zip` as a convenience method.

### `enumerate` → `Enumerate` — `poop/transformers/enumerate.py`

`enumerate(col)` and `enumerate(col, start)` are rewritten by `EnumerateTransformer` to `_poop_enumerate(col)` / `_poop_enumerate(col, start)`, which returns an `Enumerate` object.

`Enumerate` (`poop/types/enumerate.py`) is a lazy iterable POOP type. It wraps any iterable (including `Dict`) and yields `Tuple(Int(index), item)` pairs on demand, raising `TypeError` eagerly on construction if the source is not iterable. It inherits `do`, `map`, `filter`, `filter_false`, `find`, `sum`, `all`, `any` from `_IterableMixin`. Every collection type exposes `.enumerate(start=Int(0)) -> Enumerate` as a convenience method. `Dict.enumerate()` iterates over keys, consistent with Python's `enumerate(dict)`.

### No `iter`/`next` — `poop/validators/no_iter.py`

| Call | Reason | Substitute |
|---|---|---|
| `iter(col)` | iterator protocol with procedural look | `col.iter()` |
| `next(it)` | same | `it.next()` |
| `aiter(col)` | async variant | `col.iter()` |
| `anext(it)` | async variant | `it.next()` |

Every collection exposes `.iter()` returning a specialized one-shot iterator that mirrors Python's iterator types (`list_iterator`, `tuple_iterator`, `set_iterator`, `frozenset_iterator`, `dict_keyiterator`, `str_iterator`, `range_iterator`, `bytes_iterator`, `bytearray_iterator`, `memory_iterator`). All inherit from `_IteratorBase` (`poop/types/_iterator_base.py`), expose `.next()` and `.do(block)`, and raise `StopIteration` on exhaustion — catchable via `Try(lambda: it.next()).except_(StopIteration, handler).run()`.

`Enumerate` and `Zip` are their own iterators (`x.iter() is x`, mirroring Python's `iter(zip(...)) is zip(...)`). They expose `.next()` consuming a lazy internal generator one-shot, while `.do()` keeps the existing restartable behaviour.

`Dict.iter()` returns `DictKeyIterator`, mirroring `iter(dict)` in Python. `Dict.values().iter()` returns `DictValueIterator`; `Dict.items().iter()` returns `DictItemIterator`. Each view also exposes `.reversed()` returning the matching reverse iterator (`DictReverseKeyIterator`, `DictReverseValueIterator`, `DictReverseItemIterator`).

### Dict views — `poop/types/dict_keys.py`, `dict_values.py`, `dict_items.py`

`Dict.keys()`, `Dict.values()`, and `Dict.items()` return **live view** objects mirroring Python's `dict_keys`, `dict_values`, and `dict_items` exactly. They reflect mutations to the underlying dict.

| View | iter | set ops | comparison | mapping |
|---|---|---|---|---|
| `DictKeys` | `DictKeyIterator` | `\|`, `&`, `-`, `^` → `Set`; `isdisjoint` | `__eq__`, `__le__`, `__lt__`, `__ge__`, `__gt__` (set semantics) | `mapping()` → `MappingProxy` |
| `DictValues` | `DictValueIterator` | none (values may be unhashable) | inherits `Object` identity (Python parity) | `mapping()` |
| `DictItems` | `DictItemIterator` (yields `Tuple(k, v)`) | `\|`, `&`, `-`, `^` → `Set` of `Tuple`; `isdisjoint` | full set semantics like `DictKeys` | `mapping()` |

All three views are unhashable (`__hash__ = None`), expose `len()`/`includes()`/`__contains__`, and support `__reversed__`. `DictKeys` and `DictValues` inherit `_IterableMixin`; `DictItems` also inherits the mixin and yields `Tuple(k, v)` from `__iter__`. To materialize a view as a `List`, use `list(view)` — the `ListTransformer` rewrites the call to `_poop_list_from(view)`, which accepts any iterable.

### MappingProxy — `poop/types/mapping_proxy.py`

`MappingProxy` is a read-only wrapper over a `Dict` mirroring `types.MappingProxyType`. Returned by `view.mapping()` on the three dict views. Exposes read methods (`at`, `get`, `keys`, `values`, `items`, `len`, `includes`, `iter`, `copy`, `reversed`, `__or__` returning `Dict`) but no mutation methods. Equality with `Dict` and `MappingProxy`. Unhashable.

### No `setattr`/`delattr` — `poop/validators/no_setattr.py`

| Call | Reason | Substitute |
|---|---|---|
| `setattr(obj, name, val)` | free function with procedural look | `obj.set_attr(name, val)` |
| `delattr(obj, name)` | same | `obj.del_attr(name)` |

### No introspection — `poop/validators/no_introspection.py`

| Call | Reason |
|---|---|
| `globals()` | scope introspection — state lives in instances |
| `locals()` | same |
| `vars(obj)` | exposes raw Python-native slot values (`_value`, `_items`, `_data`) that are not POOP objects — breaks encapsulation and the "all methods return POOP types" rule; no clean substitute |

### No `dir` — `poop/validators/no_dir.py`

| Call | Reason | Substitute |
|---|---|---|
| `dir(obj)` | free function with procedural look | `obj.dir()` |

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

| Call | Reason | Substitute |
|---|---|---|
| `input(prompt)` | free function with procedural look | `prompt.input()` (`poop/types/string.py`) |

Symmetric to `Object.print()` — the receiver is what gets shown. Scoped to `Str` (not `Object`) since non-string receivers as prompts are meaningless. `EOFError` propagates raw, catchable via `Try(lambda: prompt.input()).except_(EOFError, handler).run()`.

### No `open` → `Path` — `poop/validators/no_open.py`, `poop/transformers/path.py`

| Call | Reason | Substitute |
|---|---|---|
| `open(path, ...)` | free function with procedural look | `Path('foo').read_text()` / `write_text(content)` (`poop/types/path.py`) |

`Path` (`poop/types/path.py`) wraps `pathlib.Path` and exposes filesystem I/O as message passing. Exposed as a namespace-only binding via the `NAMESPACE` dict in `poop/transformers/path.py` (no AST rewrite), in the same family as `Try` / `With`. `Path` accepts `Str | Path` in the constructor (idempotent), supports `__truediv__` for joining (`Path('dir') / 'file.txt'`), and orders by the underlying `pathlib.Path`.

| Method | Returns | Notes |
|---|---|---|
| `read_text()` / `write_text(content)` | `Str` / `Int` (bytes written) | UTF-8 only |
| `read_bytes()` / `write_bytes(data)` | `Bytes` / `Int` (bytes written) | |
| `exists()` / `is_file()` / `is_dir()` / `is_symlink()` / `is_absolute()` | `Boolean` | direct delegation |
| `mkdir(mode, parents, exist_ok)` / `rmdir()` / `unlink(missing_ok)` / `touch(mode, exist_ok)` | `NoneClass` | mutate, return `none` |
| `resolve()` / `absolute()` / `rename(target)` / `replace(target)` | `Path` | navigation |
| `joinpath(*others)` / `with_name(n)` / `with_suffix(s)` / `with_stem(s)` / `relative_to(other)` | `Path` | navigation |
| `as_posix()` / `as_uri()` | `Str` | |
| `iterdir()` | `PathIterator` | lazy, one-shot — `pathlib.iterdir` returns a generator |
| `glob(pattern)` / `rglob(pattern)` | `Map` | `pathlib.glob`/`rglob` already return a `map`; POOP `Map` wraps it with `Path._from_pathlib` |
| `Path.cwd()` / `Path.home()` | `Path` | classmethods |
| Properties: `name` / `stem` / `suffix` | `Str` | mirror `pathlib` |
| Properties: `parts` / `parents` | `Tuple[Str]` / `Tuple[Path]` | |
| Property: `parent` | `Path` | |

`PathIterator` (`poop/types/path_iterator.py`) inherits `_IteratorBase` and `_IterableMixin` — it exposes `next()` / `do(block)` and gains `map` / `filter` / `find` / `all` / `any` / `reduce` / `sum` / `min` / `max` / `enumerate` / `zip` from the mixin. It is one-shot (the underlying `pathlib` generator is consumed lazily).

Out of v1 (filed if demand appears): `open(mode)` returning a POOP `File`, `stat()` / `lstat()`, `owner()` / `group()`, datetime-typed `mtime`, full `PurePath` hierarchy, non-UTF-8 encodings.

### No `del` — `poop/validators/no_del.py`

| AST node | Reason |
|---|---|
| `ast.Delete` | objects have no explicit destruction — simply do not delete |

### No `_poop_*` prefix — `poop/validators/no_poop_prefix.py`

| AST node | Reason |
|---|---|
| `ast.Name` with `id` starting in `_poop_` | mangled identifier reserved for the runtime — rewriters target it, user code must not |
| `ast.Attribute` with `attr` starting in `_poop_` | same — keeps the runtime helpers reachable for the rewritten AST but invisible to handwritten code |

Every type wrapper (`Int`, `List`, `Object`, …) lives in `DEFAULT_NAMESPACE` under a `_poop_*` key (`_poop_int`, `_poop_list_cls`, `_poop_object`, …) so the rewritten AST resolves them at runtime. This validator stops user code from referencing the same names directly, preserving the abstraction that POOP types pass as their Python builtin counterparts.

### No namespace shadow — `poop/validators/no_namespace_shadow.py`

| AST node | Reason |
|---|---|
| `ast.Assign` with target `ast.Name` in the protected set | reassigning a namespace name (`math = 42`) breaks every later call to `math.sqrt(…)` |
| `ast.AnnAssign` with target `ast.Name` in the protected set | annotated form (`math: int = 42`) — same problem |
| `ast.AugAssign` with target `ast.Name` in the protected set | augmented form (`math += 1`) — same problem |
| `ast.ClassDef` whose `name` is in the protected set | `class math: …` binds `math` at module level, shadows the namespace |
| Unpacking targets (`ast.Tuple` / `ast.List` / `ast.Starred`) holding a protected name | tuple unpacking (`math, x = 1, 2`) still rebinds the name |

The **protected set** is computed dynamically from `DEFAULT_NAMESPACE` (filtered to non-`_poop_*` entries) at validator instantiation time. Today: `Browser`, `Date`, `DateTime`, `HMAC`, `Hash`, `Match`, `MimeTypes`, `Path`, `Pattern`, `PrettyPrinter`, `Random`, `Shlex`, `Time`, `TimeDelta`, `TimeZone`, `TopologicalSorter`, `Try`, `UUID`, `With`, `binascii`, `bisect`, `copy`, `datetime`, `errno`, `fnmatch`, `getpass`, `glob`, `graphlib`, `hashlib`, `heapq`, `hmac`, `json`, `math`, `mimetypes`, `pprint`, `random`, `re`, `secrets`, `shlex`, `tomllib`, `uuid`, `webbrowser`. As new namespace mirrors land (`uuid`, …), they protect themselves automatically — no changes to this validator.

What the validator **does not** catch: function parameters (`def f(math): …`), lambda arguments (`lambda math: …`), and method names inside classes (`class Calc: def math(self): …`). Those bind in local scope and are typically intentional — the user knows what they're doing. The validator targets the top-level / shared-scope reassignment that surfaces as `AttributeError` much later.

### No `sum` — `poop/validators/no_sum.py`

| Call | Reason | Substitute |
|---|---|---|
| `sum(col)` | free function with procedural look | `col.sum()` |

Available on `List`, `Tuple`, `Set`, `FrozenSet`, and `Range`.

### No `map` / `filter` — `poop/validators/no_map.py`, `poop/validators/no_filter.py`

| Call | Reason | Substitute |
|---|---|---|
| `map(func, col)` | free function with procedural look | `col.map(block)` returning `Map` (lazy) |
| `filter(func, col)` | free function with procedural look | `col.filter(block)` returning `Filter` (lazy) |

`col.map(block)` returns a `Map` and `col.filter(block)` returns a
`Filter` — both lazy iterators in the same family as `Enumerate` and
`Zip`. The block is applied on demand as the result is consumed.
Materialization is via the target type's constructor:

```python
list(items.map(lambda x: x + 1))           # -> List
tuple(items.filter(lambda x: x > 0))       # -> Tuple
set(items.map(lambda x: x.lower()))        # -> Set
bytes(items.map(lambda x: x.code()))       # -> Bytes
```

In Python tests (where the transformer doesn't run), construct via
varargs unpack: `List(*items.map(...))`. Methods that consume the
iterator (`do`, `sum`, `min`, `max`, `find`, `reduce`, `all`, `any`)
work on `Map`/`Filter` directly via `_IterableMixin`.

### No `round` — `poop/validators/no_round.py`

| Call | Reason | Substitute |
|---|---|---|
| `round(x)` | free function with procedural look | `x.round()` |
| `round(x, n)` | free function with procedural look | `x.round(n)` |

Available on `Int` and `Float`.

### No `sorted` / `reversed` — `poop/validators/no_sorted.py`, `poop/validators/no_reversed.py`

| Call | Reason | Substitute |
|---|---|---|
| `sorted(col)` | free function with procedural look | `col.sorted()` |
| `reversed(col)` | free function with procedural look | `col.reversed()` |

### No `in` / `not in` — `poop/validators/no_in.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Compare` | op is `ast.In` | `x in col` has a procedural look | `col.includes(x)` |
| `ast.Compare` | op is `ast.NotIn` | `x not in col` has a procedural look | `col.includes(x).not_()` |

### No subscript — `poop/validators/no_subscript.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Subscript` | slice is not `ast.Slice` | `obj[key]` looks like an operator | `obj.at(key)` |
| `ast.Subscript` | slice is `ast.Slice` | `obj[1:3]` looks like an operator | `obj.slice(start, stop)` |

### No comprehension — `poop/validators/no_comprehension.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.ListComp` / `ast.SetComp` / `ast.DictComp` / `ast.GeneratorExp` | implicit iteration with procedural look | `col.map(block)`, `col.filter(block)` |

## Explicitly allowed

Constructs considered for blocking but decided to allow by design.

### Augmented assignment (`+=`, `-=`, `*=`, …)

`x += 1` is syntactic sugar for `x = x + 1`. Both forms rebind the variable using the same arithmetic operation — there is no message-passing substitute that would be more idiomatic. Blocking `+=` would be a purely cosmetic restriction without a principled rationale. `ast.AugAssign` is intentionally not blocked.

### `super`

`super()` is the standard way to delegate to a parent method in both Python and Smalltalk. Without it, subclasses cannot extend parent behaviour — inheritance breaks entirely. There is no message-passing substitute. Allowed.

### `property` / `classmethod` / `staticmethod`

These are class-definition decorators, not runtime operations on values. They define how a method is bound, not what it does. Blocking them would prevent idiomatic class definitions without a principled POOP substitute. Allowed.

### `help`

`help()` is a development tool — it prints documentation for inspection at the REPL or during exploration. It carries no program logic and has no message-passing equivalent that would be more expressive. Allowed.

### Binary infix operators (`+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`)

`a + b`, `a == b`, `a < b` and their siblings are allowed. These are `ast.BinOp` and `ast.Compare` nodes — the same syntactic family as `+=`, which is already explicitly allowed.

The rationale mirrors Smalltalk: binary messages (`+`, `-`, `*`, …) are the idiomatic way to express arithmetic and comparison. Blocking them would force `a.add(b)`, `a.lt(b)` etc., which is more verbose without being more expressive or principled. The key asymmetry is with *unary* operators: `-a` (USub), `~a` (Invert) have named message equivalents (`a.negated()`, `a.bit_invert()`) and carry no ergonomic benefit in infix form, so they are blocked. Binary forms have no principled substitute.

### Heterogeneous numeric comparisons return `false`

`Int(1) == Float(1.0)` → `false`. `Int(1) == Complex(1+0j)` → `false`. In native Python all three would be `True`.

This is intentional: POOP types are opaque to each other — an `Int` and a `Float` are distinct objects and equality is strict type identity first. The principle "every basic type has a POOP equivalent" means each type is self-contained; implicit cross-type coercion would require treating one type as subordinate to another, which breaks that symmetry.

To compare numeric values across types, convert explicitly first: `i.float() == f`, `f.int() == i`, `i.complex() == c`.

## Active types

### Object — `poop/types/object.py`

Concrete root of all POOP types. The table below highlights the universal methods that map directly onto Smalltalk messages — it is **not exhaustive**. The full API also includes `if_none`, `if_not_none`, `hash`, `id`, `callable`, `is_subclass`, `repr`, `ascii`, `format`, `has_attr`, `set_attr`, `del_attr`, and `print` (see `poop/types/object.py` for signatures).

| Smalltalk message | Method | Behavior |
|---|---|---|
| `isNil` | `is_none()` | always `false` for Object |
| `notNil` | `not_none()` | always `true` for Object |
| `not` | `not_()` | `false if bool(self) else true` |
| `class` | `class_name()` | `type(self).__name__` as `Str` |
| `perform:` | `get_attr(name)` | `getattr` with optional default |
| — | `dir()` | sorted `List` of `Str` attribute names (`builtins.dir(self)`) |

`__str__` returns `"<ClassName>"` as fallback; `__repr__` delegates to `__str__`.

#### `is_instance` and raw Python types

`obj.is_instance(T)` accepts a raw Python `type` (e.g. `Int`, `Str`, `Boolean`) — not a POOP-level "Class" object. This is a deliberate primitive leak: POOP has no first-class metaclass or class-object type, so there is nothing more idiomatic to pass. The same tradeoff applies to exception types in `Try.except_(ValueError, handler)` and context managers in `With`. The message-passing form (`obj.is_instance(...)`) is preserved; only the argument is a native Python type rather than a POOP wrapper.

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
| `assert:` | `assert_(message)` (on `Object`, not just `Boolean`) | raises `AssertionError(message)` if `bool(self)` is falsy; returns `self` otherwise |

### Block — `poop/types/block.py` + `poop/transformers/block.py`

`Block` is a first-class object wrapping a callable. In Smalltalk, `[...]` syntax creates a block; in POOP every `lambda` expression is automatically rewritten to `Block(lambda: ...)` by the transformer. This makes `lambda` the idiomatic block literal — the `Block(...)` wrapper is transparent to the programmer.

`while_true` and `while_false` live on `Block`, not on `Boolean`. The receiver is the condition block — the object whose value determines whether the loop continues. This matches Smalltalk semantics (`[cond] whileTrue: [body]`) and eliminates the philosophical problem of the receiver being irrelevant.

| Smalltalk message | POOP idiom |
|---|---|
| `[cond] whileTrue: [body]` | `(lambda: cond).while_true(lambda: body)` |
| `[cond] whileFalse: [body]` | `(lambda: cond).while_false(lambda: body)` |
| `[block] value` | `(lambda: expr)()` |
| `[block] value: arg` | `(lambda x: expr)(arg)` |

> **Why lambda, not `[...]`?** Python has no block literal syntax. `lambda` is the closest equivalent — a deferred expression. The transformer intercepts every `ast.Lambda` and wraps it in `Block(...)` transparently, so the programmer writes plain lambdas and gets first-class POOP block objects without ever naming `Block` explicitly.

### Collection iterable methods — `poop/types/_iterable_mixin.py`

`List`, `Tuple`, `Set`, `FrozenSet`, `Range`, `Bytes`, `ByteArray`, `MemoryView`, `Enumerate`, `Zip`, `DictKeys`, `DictValues`, and `DictItems` all inherit the following methods from `_IterableMixin`:

| Smalltalk message | POOP method | Behavior |
|---|---|---|
| `do:` | `do(block)` | visits each element; returns `none` (substitute for `for` loop) |
| `collect:` | `map(block)` | returns `Map` (lazy); materialize via `list(...)`/`tuple(...)`/etc. |
| `select:` | `filter(block)` | returns `Filter` (lazy); same materialization |
| `reject:` | `filter_false(block)` | returns `Filter` (lazy) with the predicate inverted |
| `detect:` | `find(block)` | first element satisfying block, or POOP `none` |
| `inject:into:` | `reduce(init, block)` | fold with required initial value; returns accumulated result |
| — | `sum()` | sum of elements; returns `Int(0)` for empty collection |
| — | `min(key=None, default=...)` | smallest element; mirrors Python `min` |
| — | `max(key=None, default=...)` | largest element; mirrors Python `max` |
| — | `all(block)` | `true` if block holds for every element |
| — | `any(block)` | `true` if block holds for at least one element |
| — | `enumerate(start=Int(0))` | returns an `Enumerate` of `Tuple(Int(i), item)` pairs |
| — | `zip(*others, strict=false)` | returns a `Zip` of `Tuple(...)` |

`map`/`filter`/`filter_false` are **lazy** — they return `Map`/`Filter` iterators (same family as `Enumerate`/`Zip`) regardless of the receiver's type, mirroring Python's `map`/`filter` builtins. The block runs only as the result is consumed. To materialize, pass the lazy result to a constructor: `list(col.map(f))`, `tuple(col.filter(g))`, `set(col.map(f))`, `bytes(col.map(g))`. Methods that consume the iterator (`do`, `sum`, `min`, `max`, `find`, `reduce`, `all`, `any`) work on `Map`/`Filter` directly without materialization.

`Dict.do` is not from the mixin — it passes `Tuple(key, value)` pairs to the block instead of plain elements. `Bytes` and `ByteArray` override `find` for substring search (different semantics from the mixin's element-finding `find`).

`Dict.do` is not from the mixin — it passes `Tuple(key, value)` pairs to the block instead of plain elements. `Bytes` and `ByteArray` override `find` for substring search (different semantics from the mixin's element-finding `find`).

### Map / Filter — `poop/types/map.py`, `poop/types/filter.py`

`Map` and `Filter` are lazy iterator types in the same family as `Enumerate` and `Zip`. They wrap a source iterable and a block, and apply the block on demand:

- `Map(source, block)` yields `block(item)` for each item.
- `Filter(source, block)` yields `item` when `block(item)` is truthy.

Both inherit `_IterableMixin` so chains like `col.map(f).filter(g).sum()` keep iterating once through the source. Both expose `.next()` (one-shot, like `Enumerate`/`Zip`) and `__iter__` (returns a fresh generator — restartable when the source is restartable).

`Map` and `Filter` are internal — they have no transformer and are not bound in `DEFAULT_NAMESPACE`. User code reaches them exclusively through the mixin's `.map(block)` / `.filter(block)` / `.filter_false(block)` methods. Python tests that import directly from `poop.types.map` / `poop.types.filter` may construct them as `Map(source, block)` / `Filter(source, block)`.

### Range — `poop/types/range.py`

`Range(Object)` represents a closed integer interval [start, stop]. Created via `range(start, stop)` (rewritten to `_poop_range(...)` by the transformer).

| POOP method | Behavior |
|---|---|
| `do(block)` | see collection iterable methods above |
| `map(block)` | transforms → `Map` (lazy) |
| `filter(block)` | filters → `Filter` (lazy) |
| `filter_false(block)` | filters inverse → `Filter` (lazy) |
| `find(block)` | first satisfying, or POOP `none` |
| `iter()` | returns a one-shot `RangeIterator` |
| `len()` | returns `Int` |
| `at(index)` | returns the value at `index` as `Int` |
| `slice(start, stop, step=None)` | slice → `List` |
| `slice(slice_obj)` | slice via `Slice` value object → `List` |
| `reversed()` | returns reversed `Range` |
| `includes(value)` | `true` if `value` is in the range |
| `count(value)` | number of occurrences (always `0` or `1`) |
| `index(value)` | position of `value`, or raises `ValueError` |
| `start` / `stop` / `step` | properties exposing the underlying `Int` bounds |

### Object.print — `poop/types/object.py`

All POOP objects inherit `print()` from `Object`. `List` and `Tuple` override to support `sep`.

| Message | Behavior |
|---|---|
| `obj.print()` | prints `str(obj)` followed by `\n`; returns `None` |
| `obj.print(end="")` | controls the terminator |
| `obj.print(flush=True)` | forces buffer flush |
| `list.print(sep=", ")` | `List`/`Tuple`: joins elements with `sep` (default `" "`) |

`"".print()` prints a blank line.

### Error — `poop/types/error.py`

`Error(Object)` wraps a caught Python exception. Handlers in `Try.except_` always receive an `Error` object.

| Method | Behavior |
|---|---|
| `message()` | returns exception message as `Str` |
| `kind()` | returns exception class name as `Str` |

`__str__` returns `"Error(<exception>)"`.

### Try — `poop/types/try_.py`

`Try(Object)` implements deferred try/except/finally as a message-passing builder. The block is executed lazily — only when `.run()` or `.finally_()` is called.

| Message | Method | Behavior |
|---|---|---|
| `[block] on: ExcType do: handler` | `Try(block).except_(ExcType, handler)` | registers a handler; chainable |
| `[block] ensure: finallyBlock` | `Try(block).finally_(block)` | sets finally block **and** executes |
| *(terminal)* | `.run()` | executes without finally block |

`exc_type` is a native Python class (`ValueError`, `KeyError`, …) — the only deliberate primitive leak. Unhandled exceptions are always re-raised. Multiple `.except_()` calls are matched in order.

> **Tradeoff**: `exc_type` must be a native Python exception class. Mirroring Python's full hierarchy (~100+ classes) into POOP types is impractical. The handler always receives an `Error` wrapper regardless.

`Try` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/try_.py` — namespace-only, no AST rewrite.

### With — `poop/types/with_.py`

`With(Object)` implements the context manager protocol as a message-passing builder. The context manager block is executed lazily — only when `.do()` is called.

| Message | Method | Behavior |
|---|---|---|
| `[block] value: aResource` | `With(lambda: cm).do(lambda resource: body)` | acquires resource via `__enter__`, runs body, calls `__exit__` |

The context manager object must implement Python's `__enter__`/`__exit__` protocol — a deliberate primitive leak, consistent with `Try` using native exception types. Exceptions propagate via the standard `__exit__` return value: if `__exit__` returns falsy, the exception is re-raised; truthy suppresses it.

> **Tradeoff**: context managers must implement Python's native protocol (`__enter__`/`__exit__`). POOP cannot redefine resource acquisition semantics without reimplementing every standard context manager (files, locks, etc.), which is impractical.

`With` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/with_.py` — namespace-only, no AST rewrite.

### math — `poop/types/math.py` + `poop/transformers/math.py`

`math` is a namespace class wrapping Python's `math` module. Exposed as a namespace-only binding via the `NAMESPACE` dict in `poop/transformers/math.py` (no AST rewrite), in the same family as `Try` / `With` / `Path`. Every public callable in Python 3.14's `math` is reachable as `math.<same-name>(...)`, with parameter order, keyword-only markers, defaults, return types, **and the lowercase module name** mirroring Python exactly. The namespace binding is `math` (lowercase) because `math` is a Python module, not a class.

The five module constants follow the source module's case verbatim — `math.pi`, `math.e`, `math.tau`, `math.inf`, `math.nan` (lowercase). Other POOP namespaces inherit their own case from their source modules: `uuid.NAMESPACE_DNS`, `secrets.DEFAULT_ENTROPY`, and so on stay uppercase because that is how `uuid` and `secrets` ship them.

| Category | Operations | Returns |
|---|---|---|
| Number theory | `factorial`, `gcd(*ints)`, `lcm(*ints)`, `comb`, `perm(n, k=None)`, `isqrt` | `Int` |
| Trigonometric | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2(y, x)` | `Float` |
| Hyperbolic | `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` | `Float` |
| Exp / log / power | `exp`, `expm1`, `exp2`, `log(x, base=math.e)`, `log2`, `log10`, `log1p`, `sqrt`, `cbrt`, `pow` | `Float` |
| Rounding | `floor`, `ceil`, `trunc` | `Int` |
| Float decomposition | `modf` → `(Float, Float)`, `frexp` → `(Float, Int)`, `ldexp` | `Tuple` / `Float` |
| Angular conversion | `degrees`, `radians` | `Float` |
| Float utilities | `fabs`, `copysign`, `fmod`, `remainder`, `fma`, `ulp`, `nextafter(x, y, *, steps=None)` | `Float` |
| Predicates | `isfinite`, `isinf`, `isnan`, `isclose(a, b, *, rel_tol=1e-9, abs_tol=0.0)` | `Boolean` |
| Aggregates | `fsum`, `prod(iter, *, start=1)`, `sumprod`, `dist`, `hypot(*args)` | `Float` / `Int` |
| Special functions | `erf`, `erfc`, `gamma`, `lgamma` | `Float` |
| Constants | `pi`, `e`, `tau`, `inf`, `nan` | `Float` |

POOP `Int` and `Float` keep methods that are native to Python's `int` and `float` (`bit_length`, `bit_count`, `is_integer`, `as_integer_ratio`) and the substitutes for banned builtins (`Int.abs()`, `Int.pow()`, `Int.divmod()` cover the `no_abs` / `no_pow` / `no_divmod` validators). The math-specific public methods that previously lived on those types (`Int.ceil`/`floor`/`trunc`, `Float.ceil`/`floor`/`trunc`) are removed — `math.ceil(x)` and friends are the single source of truth.

`math` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/math.py` — namespace-only, no AST rewrite.

### random + Random — `poop/types/random.py` + `poop/transformers/random.py`

Python's `random` module exposes two distinct names: the lowercase `random` module (with module-level functions like `random.random()` and `random.choice(xs)`) and the PascalCase `Random` class (instantiated for seeded, independent generators: `random.Random(seed)`). POOP mirrors that split with **two namespace entries**:

- **`random`** (lowercase) — a singleton instance (`_DEFAULT = Random()`) acting as the module. Module-level entry points are calls on this singleton: `random.random()`, `random.choice(xs)`, `random.shuffle(xs)`, etc. — matching Python's `random.<func>` exactly.
- **`Random`** (PascalCase) — the class itself, callable in POOP source: `r = Random(seed); r.random()`. Equivalent to Python's `random.Random(seed)`, but shorter (POOP user code already has `Random` in scope, no `random.` prefix needed for the constructor).

This is the first POOP namespace where two names point to related but distinct objects: a module-like singleton AND its underlying class. Other module mirrors (`math`, `secrets`, `tomllib`) have only the lowercase module name because they expose no public class.

| Category | Operations | Returns |
|---|---|---|
| Bookkeeping | `seed(a=None, version=Int(2))` | `none` |
| Core draws | `random()`, `uniform(a, b)`, `randint(a, b)`, `randrange(start, stop=None, step=None)`, `getrandbits(k)`, `randbytes(n)` | `Float`/`Int`/`Bytes` |
| Collection draws | `choice(seq)`, `shuffle(x)` mutates list, returns `none`, `choices(population, weights=None, *, cum_weights=None, k=Int(1))`, `sample(population, k, *, counts=None)` | element / `none` / `List` |
| Distributions | `gauss`, `normalvariate`, `lognormvariate`, `expovariate`, `gammavariate`, `betavariate`, `paretovariate`, `weibullvariate`, `vonmisesvariate`, `triangular`, `binomialvariate` (Python 3.12+) | `Float` (10) / `Int` (binomialvariate) |

The same method set is available on both `random` (module API, uses singleton state) and on `Random(seed)` instances (independent state per instance). Anything cryptographic goes through `secrets`, not `random`. `getstate` / `setstate` are deferred to Future work (see `proposals.md`) because the Mersenne Twister state is opaque (625 ints) and has no clean POOP type-discipline mapping.

`random` and `Random` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/random.py` — namespace-only, no AST rewrite.

### errno — `poop/types/errno.py` + `poop/transformers/errno.py`

`errno` is a constant-only namespace mirroring Python's `errno` module. Every integer error code Python exposes (`EPERM`, `ENOENT`, `EAGAIN`, `EWOULDBLOCK`, …) is bound on the `Errno` class as a POOP `Int` class attribute under the same uppercase name. The reverse map `errno.errorcode` is a POOP `Dict[Int, Str]` keyed by canonical code, mirroring CPython exactly (so aliases like `EAGAIN`/`EWOULDBLOCK` collapse to a single entry).

| Member | Type | Notes |
|---|---|---|
| `errno.EPERM`, `errno.ENOENT`, … (all 134 codes Python exposes) | `Int` | Same name as `errno.<NAME>` in CPython |
| `errno.errorcode` | `Dict[Int, Str]` | 131 entries — canonical names only |

The set of constants is built at import time by enumerating `dir(errno)` rather than maintained by hand, so POOP automatically tracks whichever subset CPython exposes on the host (Linux / macOS / Windows). Lowercase `errno` keeps the lowercase module-name convention; constants are uppercase because that is how CPython ships them.

`errno` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/errno.py` — namespace-only, no AST rewrite.

### getpass — `poop/types/getpass.py` + `poop/transformers/getpass.py`

`getpass` is a tiny namespace mirroring Python's `getpass` module. Both reads return POOP `Str`:

| Operation | Returns | Notes |
|---|---|---|
| `getpass.getpass(prompt=Str("Password: "), stream=none)` | `Str` | Reads without echo |
| `getpass.getuser()` | `Str` | Login name lookup |

`getpass.GetPassWarning` is **not surfaced** in POOP. CPython emits it via `warnings` when echo can't be suppressed, but POOP has no warning concept (`warnings` itself is "out" — see proposals.md). The underlying CPython call still writes the warning to stderr; POOP user code just cannot catch or filter it. See proposals.md § Future work for a possible later exposure path.

`getpass` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/getpass.py` — namespace-only, no AST rewrite.

### base64 — methods on `Bytes` and `Str`

Python's `base64.*` is reachable as **methods on the value**, not a namespace. Both `Bytes` (encode + decode) and `Str` (decode only) carry the full surface:

| Direction | Receivers | Methods |
|---|---|---|
| Encode | `Bytes` | `b16encode`, `b32encode`, `b32hexencode`, `b64encode`, `standard_b64encode`, `urlsafe_b64encode`, `a85encode`, `b85encode`, `z85encode` |
| Decode | `Bytes`, `Str` | `b16decode`, `b32decode`, `b32hexdecode`, `b64decode`, `standard_b64decode`, `urlsafe_b64decode`, `a85decode`, `b85decode`, `z85decode` |

Every method takes no arguments (v0.13.0 ships Python's defaults; optional kwargs like `altchars`/`validate`/`casefold` are deferred to Future work). Encoders return `Bytes` (ASCII-bearing), mirroring `base64.<name>(b)` in Python — callers wanting a textual `Str` must explicitly `.decode(Str("ascii"))` afterward, exactly as in Python. Decoders also return `Bytes`.

No new POOP type, no transformer, no AST rewrite — the methods live directly on the existing `Bytes` and `Str` classes.

### secrets — `poop/types/secrets.py` + `poop/transformers/secrets.py`

`secrets` is a cryptographic-secure-only namespace mirroring Python's `secrets` module. POOP deliberately separates secure (`secrets`) from non-secure (`random`) randomness to match Python's API split exactly.

| Category | Operations | Returns |
|---|---|---|
| Token minting | `token_bytes(nbytes=none)`, `token_hex(nbytes=none)`, `token_urlsafe(nbytes=none)` | `Bytes` / `Str` / `Str` |
| Secure draws | `choice(seq)`, `randbelow(exclusive_upper_bound)`, `randbits(k)` | element / `Int` / `Int` |
| Constant-time comparison | `compare_digest(a, b, /)` (positional-only) | `Boolean` |
| Constant | `DEFAULT_ENTROPY` | `Int` (32 in CPython) |

`secrets.SystemRandom` is **not** surfaced — its instance API duplicates the module-level functions above. `nbytes=none` resolves to `DEFAULT_ENTROPY`, mirroring CPython's default.

`secrets` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/secrets.py` — namespace-only, no AST rewrite.

### binascii — `poop/types/binascii.py` + `poop/transformers/binascii.py`

`binascii` mirrors Python's `binascii` module — lower-level one-shot conversions between binary data and ASCII representations, plus CRC checksums. Pairs with `base64` (the methods on `Bytes`/`Str`).

| Category | Operations | Returns |
|---|---|---|
| Hex | `b2a_hex(data, sep=none, bytes_per_sep=Int(1))`, `hexlify(...)` (alias), `a2b_hex(hexstr)`, `unhexlify(hexstr)` (alias) | `Bytes` |
| Base64 / qp / uu (one-shot) | `b2a_base64(data)`, `a2b_base64(data)`, `b2a_qp(data)`, `a2b_qp(data)`, `b2a_uu(data)`, `a2b_uu(data)` | `Bytes` |
| CRC | `crc_hqx(data, value)`, `crc32(data, value=Int(0))` | `Int` |
| Exception classes | `binascii.Error`, `binascii.Incomplete` | Python exception types |

The two exception classes are exposed as raw Python types so user code can pass them to `Try.except_(...)`. Exception classes are the documented exception to POOP's type-discipline rule — `Try` already accepts a Python exception type for its handler, so exposing these mirrors that existing convention.

`b2a_hqx`/`a2b_hqx` (Mac BinHex 4) are not exposed because Python removed them in 3.13.

`binascii` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/binascii.py` — namespace-only, no AST rewrite.

### mimetypes + MimeTypes — `poop/types/mimetypes.py` + `poop/transformers/mimetypes.py`

`mimetypes` mirrors Python's `mimetypes` module — extension/MIME-type lookups. Like `random`/`Random`, POOP exposes **two namespace entries** because the source module ships both a module-level API and a reusable class:

- **`mimetypes`** (lowercase) — module-level shortcuts plus the standard registry constants. Operates on CPython's process-global registry.
- **`MimeTypes`** (PascalCase) — the reusable registry class. `MimeTypes(filenames=List, strict=Boolean)` builds an isolated instance with its own state.

| Category | Operations | Returns |
|---|---|---|
| Lookups | `guess_type(url, strict=true)`, `guess_extension(type, strict=true)`, `guess_all_extensions(type, strict=true)` | `Tuple[Str/none, Str/none]` / `Str | none` / `List[Str]` |
| Mutation | `add_type(type, ext, strict=true)`, `init(files=none)`, `read_mime_types(filename)` (module-only) | `none` / `none` / `Dict | none` |
| Constants (module-only) | `suffix_map`, `encodings_map`, `types_map`, `common_types` (all `Dict[Str, Str]`), `knownfiles` (`List[Str]`) | snapshot at import time |

The constant dicts are **snapshotted** from CPython's globals at import time. Subsequent `add_type` calls update CPython's mutable globals but not the POOP snapshots — this preserves POOP's "no introspection" stance: constants are immutable values from POOP's perspective. Use `MimeTypes` if you need a registry that reflects later mutations.

`mimetypes` and `MimeTypes` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/mimetypes.py` — namespace-only, no AST rewrite.

### webbrowser + Browser — `poop/types/webbrowser.py` + `poop/transformers/webbrowser.py`

`webbrowser` mirrors Python's `webbrowser` module — open URLs in the user's default (or a chosen) browser. Like `random`/`Random` and `mimetypes`/`MimeTypes`, two namespace entries are bound:

- **`webbrowser`** (lowercase) — module-level shortcuts and the `get(using=none)` factory.
- **`Browser`** (PascalCase) — wraps the underlying `webbrowser.BaseBrowser` controller returned by `get()`, exposing the same `open`/`open_new`/`open_new_tab` methods.

| Operation | Returns | Notes |
|---|---|---|
| `webbrowser.open(url, new=Int(0), autoraise=true)` | `Boolean` | True iff a browser launched successfully |
| `webbrowser.open_new(url)` | `Boolean` | new window |
| `webbrowser.open_new_tab(url)` | `Boolean` | new tab |
| `webbrowser.get(using=none)` | `Browser` | controller; raises `webbrowser.Error` if `using` unknown |
| `webbrowser.Error` | Python type | usable with `Try.except_` |
| `Browser.open` / `.open_new` / `.open_new_tab` | `Boolean` | per-instance dispatch |
| `Browser.name` | `Str` | controller name (e.g. `"chrome"`) |

POOP collapses Python's concrete browser classes (Chrome, Edge, Mozilla, …) into a single `Browser` POOP type because every concrete class carries the same public surface. Class identity is preserved internally for dispatch.

`webbrowser.register(name, constructor, instance, preferred)` is **not** surfaced — its `constructor` argument is a Python callable returning a `BaseBrowser` subclass, with no clean POOP type-discipline mapping in v1. See proposals.md § Future work.

`webbrowser` and `Browser` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/webbrowser.py` — namespace-only, no AST rewrite.

### glob — `poop/types/glob.py` + `poop/transformers/glob.py`

`glob` mirrors Python's `glob` module — shell-style wildcard expansion driven from a string pattern. `Path.glob`/`Path.rglob` cover most use; this namespace surfaces the module-level entry points for callers who want to glob without first constructing a `Path`.

| Operation | Returns | Notes |
|---|---|---|
| `glob.glob(pathname, *, root_dir=none, recursive=false, include_hidden=false)` | `List[Path]` | eager |
| `glob.iglob(pathname, *, root_dir=none, recursive=false, include_hidden=false)` | `GlobIter` | lazy; iterable, with `.to_list()` |
| `glob.escape(pathname)` | `Str` | escapes glob metacharacters |
| `glob.translate(pat, *, recursive=false, include_hidden=false, seps=none)` | `Str` | compiles the pattern to a regex source string (3.13+) |

`GlobIter` wraps Python's `iglob` generator and yields POOP `Path` instances. The `dir_fd` parameter on CPython's `glob.glob` is not surfaced — POOP routes file-descriptor-based I/O nowhere yet.

`glob` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/glob.py` — namespace-only, no AST rewrite.

### fnmatch — `poop/types/fnmatch.py` + `poop/transformers/fnmatch.py`

`fnmatch` mirrors Python's `fnmatch` module — Unix shell-pattern matching against filenames.

| Operation | Returns |
|---|---|
| `fnmatch.fnmatch(filename, pattern)` | `Boolean` (case rules follow the OS) |
| `fnmatch.fnmatchcase(filename, pattern)` | `Boolean` (always case-sensitive) |
| `fnmatch.filter(names, pattern)` | `List[Str]` |
| `fnmatch.translate(pattern)` | `Str` (regex source) |

`fnmatch` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/fnmatch.py` — namespace-only, no AST rewrite.

### copy — `poop/types/copy.py` + `poop/transformers/copy.py`

`copy` mirrors Python's `copy` module — shallow and deep object copying. POOP types implement `__copy__` / `__deepcopy__` via the standard Python protocol; the namespace just routes calls.

| Operation | Returns | Notes |
|---|---|---|
| `copy.copy(obj)` | same type as input | shallow |
| `copy.deepcopy(obj)` | same type as input | recursive |
| `copy.Error` | Python exception type | usable with `Try.except_` |

`deepcopy`'s `memo` parameter (an `id(obj)`-keyed dict CPython uses to track recursive identities during traversal) is **not** surfaced — it has no clean type-discipline mapping because POOP `Dict` is keyed by POOP `Object`, not `int`. Callers wanting custom memoization should implement `__deepcopy__` on their POOP class. `copy.replace` (3.13+) is similarly out of scope for v1 — POOP classes don't use decorators and have no `dataclasses` story.

`copy` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/copy.py` — namespace-only, no AST rewrite.

### pprint + PrettyPrinter — `poop/types/pprint.py` + `poop/transformers/pprint.py`

`pprint` mirrors Python's `pprint` module — multi-line, indented printing of nested data structures. POOP types alias `__repr__` to `__str__`, so pretty-printed output reads naturally for POOP values.

Two namespace entries follow the `random`/`Random` and `mimetypes`/`MimeTypes` convention:

- **`pprint`** (lowercase) — module-level shortcuts.
- **`PrettyPrinter`** (PascalCase) — reusable printer with knobs.

| Operation | Returns | Notes |
|---|---|---|
| `pprint.pprint(obj, *, indent, width, depth, compact, sort_dicts, underscore_numbers)` | `none` | writes to stdout |
| `pprint.pformat(obj, *, …)` | `Str` | returns the formatted string |
| `pprint.pp(obj, *, …)` | `none` | like `pprint`, default `sort_dicts=false` |
| `pprint.isreadable(obj)` | `Boolean` | output is eval-friendly? |
| `pprint.isrecursive(obj)` | `Boolean` | object contains self-references? |
| `pprint.saferepr(obj)` | `Str` | safe repr that doesn't recurse |
| `PrettyPrinter(indent, width, depth, *, compact, sort_dicts, underscore_numbers)` | `PrettyPrinter` | reusable instance with `.pprint`/`.pformat`/`.isreadable`/`.isrecursive` |

`PrettyPrinter` captures `sys.stdout` at construction time, matching CPython exactly — building one inside a stream redirect is the way to capture output.

`pprint` and `PrettyPrinter` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/pprint.py` — namespace-only, no AST rewrite.

### bisect — `poop/types/bisect.py` + `poop/transformers/bisect.py`

`bisect` mirrors Python's `bisect` module — binary search and ordered insertion on sorted POOP `List`s. No new POOP type; the operations all take a `List`.

| Operation | Returns | Notes |
|---|---|---|
| `bisect.bisect_left(a, x, lo=none, hi=none, *, key=none)` | `Int` | leftmost insertion point |
| `bisect.bisect_right(a, x, lo=none, hi=none, *, key=none)` | `Int` | rightmost insertion point |
| `bisect.bisect(a, x, …)` | `Int` | alias for `bisect_right` |
| `bisect.insort_left(a, x, …)` | `none` | mutates `a` in place |
| `bisect.insort_right(a, x, …)` | `none` | mutates `a` in place |
| `bisect.insort(a, x, …)` | `none` | alias for `insort_right` |

`key` is a Python callable applied to elements during comparison; insertion mutators follow POOP's mutator convention (return `none`).

`bisect` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/bisect.py` — namespace-only, no AST rewrite.

### heapq — `poop/types/heapq.py` + `poop/transformers/heapq.py`

`heapq` mirrors Python's `heapq` module — a binary min-heap on a regular POOP `List`. No new POOP type for the heap itself; operations mutate the underlying buffer.

| Operation | Returns | Notes |
|---|---|---|
| `heapq.heappush(heap, item)` | `none` | in-place |
| `heapq.heappop(heap)` | element | raises `IndexError` on empty |
| `heapq.heappushpop(heap, item)` | element | one-step push+pop |
| `heapq.heapreplace(heap, item)` | element | one-step pop+push |
| `heapq.heapify(x)` | `none` | in-place rearrangement |
| `heapq.nlargest(n, iterable, key=none)` | `List` | sorted descending |
| `heapq.nsmallest(n, iterable, key=none)` | `List` | sorted ascending |
| `heapq.merge(*iterables, key=none, reverse=false)` | `HeapMerge` | lazy iterator with `.to_list()` |

Private max-heap variants (`_heapify_max`, etc.) are intentionally out of scope.

`heapq` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/heapq.py` — namespace-only, no AST rewrite.

### shlex + Shlex — `poop/types/shlex.py` + `poop/transformers/shlex.py`

`shlex` mirrors Python's `shlex` module — POSIX-style shell tokenization, joining, and safe quoting. Two namespace entries follow the `random`/`Random` convention:

- **`shlex`** (lowercase) — module-level `split`/`join`/`quote`.
- **`Shlex`** (PascalCase) — the streaming lexer class, mirrors `shlex.shlex`.

| Operation | Returns | Notes |
|---|---|---|
| `shlex.split(s, comments=false, posix=true)` | `List[Str]` | POSIX-style tokenization |
| `shlex.join(split_command)` | `Str` | safely re-joins a list of args |
| `shlex.quote(s)` | `Str` | shell-safe escape for one token |
| `Shlex(instream=none, infile=none, posix=false, punctuation_chars=false)` | `Shlex` | streaming lexer |
| `Shlex.get_token()` | `Str | none` | next token; `none` signals EOF |
| iterating a `Shlex` | yields `Str` | wraps CPython's iter protocol |
| `Shlex.lineno` (property) | `int` | source line counter |
| `Shlex.whitespace_split` (property) | `bool` | configurable splitting mode |

v0.23.0 ships the common iterative surface; the full `Shlex` API (`read_token`, `sourcehook`, the character-class attributes, push/pop sources, etc.) is deferred to Future work. See proposals.md.

`shlex` and `Shlex` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/shlex.py` — namespace-only, no AST rewrite.

### uuid + UUID — `poop/types/uuid.py` + `poop/transformers/uuid.py`

`UUID` is a full POOP value wrapping `uuid.UUID`. Construction mirrors CPython exactly — positional `UUID(Str("12345...-…"))` for a canonical string or keyword `UUID(hex=..., bytes=..., bytes_le=..., int=..., fields=...)` for the parse-from-foo variants. Like `random`/`Random` and `mimetypes`/`MimeTypes`, two namespace entries are bound:

- **`uuid`** (lowercase) — module-level generators, helpers, and constants.
- **`UUID`** (PascalCase) — the class.

| Category | Members | Returns |
|---|---|---|
| Representations | `.hex`, `.urn` (`Str`), `.int` (`Int`), `.bytes`, `.bytes_le` (`Bytes`), `.fields` (`Tuple[Int x 6]`) | per row |
| Field accessors | `.time_low`, `.time_mid`, `.time_hi_version`, `.clock_seq_hi_variant`, `.clock_seq_low`, `.node`, `.time`, `.clock_seq` | `Int` |
| Classification | `.version` (`Int`), `.variant` (`Str`), `.is_safe` (`Str` token: `"safe"`/`"unsafe"`/`"unknown"`) | per row |
| Generators | `uuid.uuid1`/`3`/`4`/`5`/`6`/`7`/`8` | `UUID` |
| Helper | `uuid.getnode()` | `Int` |
| Namespace constants (`UUID`) | `uuid.NAMESPACE_DNS`/`URL`/`OID`/`X500`, `uuid.NIL`, `uuid.MAX` | `UUID` |
| Variant constants (`Str`) | `uuid.RESERVED_NCS`, `uuid.RFC_4122`, `uuid.RESERVED_MICROSOFT`, `uuid.RESERVED_FUTURE` | `Str` |

**`is_safe` divergence.** CPython returns a `SafeUUID` enum. POOP flattens to a lowercase `Str` token (`"safe"` / `"unsafe"` / `"unknown"`) to avoid introducing a one-off enum type — sanctioned divergence, called out in the proposal.

`uuid.SafeUUID` is not exposed as a dedicated POOP enum (see above). `uuid.uuid6`/`7`/`8` are new in Python 3.14 and surfaced unchanged.

`uuid` and `UUID` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/uuid.py` — namespace-only, no AST rewrite.

### json — `poop/types/json.py` + `poop/transformers/json.py`

`json` mirrors Python's `json` module — (de)serialisation between JSON text and POOP value graphs.

| Operation | Returns | Notes |
|---|---|---|
| `json.dumps(obj, *, skipkeys, ensure_ascii, check_circular, allow_nan, indent, sort_keys)` | `Str` | full POOP value tree → JSON |
| `json.loads(s)` | POOP value | JSON → full POOP value tree |
| `json.dump(obj, path, …)` | `none` | path-based serialise (POOP I/O convention) |
| `json.load(path)` | POOP value | path-based deserialise |
| `json.JSONDecodeError` | Python exception type | usable with `Try.except_` |

**Round-trip type discipline.** The native `json` library walks Python types; this namespace wraps every entry/exit with `_unwrap`/`_wrap` so callers never see a raw `dict`/`list`/`str`/`int`/`float`/`bool`/`None`. `Json.loads('{"a":1, "b":true}')` returns a `Dict[Str, Int | Boolean]` — every value is a POOP type. `Json.dumps(d)` accepts a POOP value graph and returns POOP `Str`.

v0.25.0 covers the common 95%; subclassing (`JSONEncoder` / `JSONDecoder`) and callback kwargs (`cls`, `default`, `object_hook`, `parse_int`/`parse_float`/`parse_constant`, `object_pairs_hook`, `separators`) are deferred to Future work pending a POOP `Block` → Python `callable` adaptation story. `json.tool` (CLI) stays out of scope.

`json` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/json.py` — namespace-only, no AST rewrite.

### tomllib — `poop/types/tomllib.py` + `poop/transformers/tomllib.py`

`tomllib` mirrors Python's `tomllib` (3.11+) — read-only TOML parsing for `pyproject.toml`, ruff/ty configs, and other modern Python config formats.

| Operation | Returns | Notes |
|---|---|---|
| `tomllib.loads(s, /)` | `Dict[Str, …]` | from `Str` |
| `tomllib.load(path, /)` | `Dict[Str, …]` | from POOP `Path` — receiver-type divergence: CPython takes a binary file, POOP has no file-object abstraction |
| `tomllib.TOMLDecodeError` | Python exception type | usable with `Try.except_` |

**Type discipline divergence.** TOML date / time / datetime values flatten to ISO-8601 `Str` for now. POOP doesn't yet have a `DateTime` POOP type; when the `datetime` proposal lands, the internal `_wrap` tightens. Documented divergence; tests will need a small update at that point.

`parse_float` (CPython's hook for routing floats to e.g. `Decimal`) is deferred to Future work pending the `decimal` proposal. Write support stays out of scope (`tomllib` is read-only upstream).

`tomllib` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/tomllib.py` — namespace-only, no AST rewrite.

### hmac + HMAC — `poop/types/hmac.py` + `poop/transformers/hmac.py`

`hmac` mirrors Python's `hmac` module — RFC 2104 keyed-hash MAC. Pairs with `hashlib` (still proposed).

| Operation | Returns | Notes |
|---|---|---|
| `hmac.new(key, msg=none, digestmod=Str("sha256"))` | `HMAC` | digestmod accepts CPython's string form |
| `hmac.digest(key, msg, digest)` | `Bytes` | one-shot, constant-time-friendly |
| `hmac.compare_digest(a, b, /)` | `Boolean` | delegates to CPython |
| `HMAC.update(msg)` | `none` | mutates in place |
| `HMAC.digest()` | `Bytes` | |
| `HMAC.hexdigest()` | `Str` | |
| `HMAC.copy()` | `HMAC` | independent clone |
| `HMAC.digest_size` / `.block_size` (property) | `Int` | |
| `HMAC.name` (property) | `Str` | e.g. `"hmac-sha256"` |

Until `hashlib` ships, `digestmod` is typed as `Str` (mirroring CPython's string-name form). When `hashlib` lands, the type widens to also accept hash constructors.

`hmac` and `HMAC` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/hmac.py` — namespace-only, no AST rewrite.

### graphlib + TopologicalSorter — `poop/types/graphlib.py` + `poop/transformers/graphlib.py`

`graphlib` mirrors Python's `graphlib` (3.9+) — topological sorting of node graphs for dependency resolution.

| Operation | Returns | Notes |
|---|---|---|
| `TopologicalSorter(graph=none)` | `TopologicalSorter` | `graph` is `Dict[node, Iterable[predecessors]]` |
| `.add(node, *predecessors)` | `none` | incremental build |
| `.prepare()` | `none` | finalize, lock structure |
| `.is_active()` | `Boolean` | any nodes left to consume? |
| `.get_ready()` | `Tuple[node]` | nodes whose predecessors are done |
| `.done(*nodes)` | `none` | mark nodes consumed |
| `.static_order()` | `Tuple[node]` | one-shot full sort |
| `graphlib.CycleError` | Python exception type | usable with `Try.except_` |

`graphlib` and `TopologicalSorter` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/graphlib.py` — namespace-only, no AST rewrite.

### datetime + Date + Time + DateTime + TimeDelta + TimeZone — `poop/types/datetime.py` + `poop/transformers/datetime.py`

`datetime` mirrors Python's `datetime` module — the canonical date, time, datetime, duration, and fixed-offset timezone types. All five wrapper classes are bound at module scope (`Date`, `Time`, …) and also accessible as `datetime.date`, `datetime.time`, etc. (the latter mirroring CPython's module attributes).

| Operation | Returns | Notes |
|---|---|---|
| `Date(year, month, day)` | `Date` | |
| `Date.today()` / `.fromisoformat(s)` / `.fromtimestamp(t)` / `.fromordinal(n)` | `Date` | constructors |
| `Date.year` / `.month` / `.day` (properties) | `Int` | |
| `Date.weekday()` / `.isoweekday()` / `.toordinal()` | `Int` | |
| `Date.isoformat()` / `.strftime(fmt)` | `Str` | |
| `Date.replace(year=none, month=none, day=none)` | `Date` | |
| `Date + TimeDelta` | `Date` | |
| `Date - TimeDelta` | `Date` | |
| `Date - Date` | `TimeDelta` | |
| `Time(hour=none, minute=none, second=none, microsecond=none, tzinfo=none)` | `Time` | |
| `Time.fromisoformat(s)` | `Time` | |
| `Time.hour` / `.minute` / `.second` / `.microsecond` (properties) | `Int` | |
| `Time.tzinfo` (property) | `TimeZone \| NoneClass` | |
| `Time.isoformat()` / `.strftime(fmt)` | `Str` | |
| `Time.replace(...)` | `Time` | |
| `DateTime(year, month, day, hour=none, ..., tzinfo=none)` | `DateTime` | |
| `DateTime.now(tz=none)` / `.utcnow()` / `.fromtimestamp(t, tz=none)` / `.fromisoformat(s)` / `.combine(date, time, tzinfo=none)` | `DateTime` | constructors |
| `DateTime.date()` / `.time()` | `Date` / `Time` | |
| `DateTime.timestamp()` | `Float` | |
| `DateTime.astimezone(tz=none)` | `DateTime` | |
| `DateTime.weekday()` / `.isoweekday()` | `Int` | |
| `DateTime.isoformat(sep=none)` / `.strftime(fmt)` | `Str` | |
| `DateTime.replace(...)` | `DateTime` | |
| `DateTime + TimeDelta` | `DateTime` | |
| `DateTime - TimeDelta` | `DateTime` | |
| `DateTime - DateTime` | `TimeDelta` | |
| `DateTime < / <= / > / >= DateTime` | `Boolean` | |
| `TimeDelta(days=none, seconds=none, microseconds=none, milliseconds=none, minutes=none, hours=none, weeks=none)` | `TimeDelta` | |
| `TimeDelta.days` / `.seconds` / `.microseconds` (properties) | `Int` | |
| `TimeDelta.total_seconds()` | `Float` | |
| `TimeDelta + / - TimeDelta` | `TimeDelta` | |
| `TimeDelta * Int` | `TimeDelta` | |
| `TimeDelta / Int` | `TimeDelta` | |
| `TimeDelta / TimeDelta` | `Float` | ratio |
| `TimeDelta // TimeDelta` | `Int` | floor division |
| `TimeDelta // Int` | `TimeDelta` | |
| `TimeDelta % TimeDelta` | `TimeDelta` | |
| `-TimeDelta` | `TimeDelta` | |
| `TimeZone(offset, name=none)` | `TimeZone` | |
| `TimeZone.utc` (class attr) | `TimeZone` | UTC constant |
| `TimeZone.utcoffset(dt=none)` | `TimeDelta` | |
| `TimeZone.tzname(dt=none)` | `Str` | |

The `tzinfo` extension protocol (custom subclasses of Python's abstract `datetime.tzinfo`) is out of scope; users get `TimeZone` for fixed offsets. The `Date.min`/`Date.max` class attributes and the `datetime.MINYEAR`/`MAXYEAR` integer constants are deferred until a caller asks for them.

`datetime`, `Date`, `Time`, `DateTime`, `TimeDelta`, and `TimeZone` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/datetime.py` — namespace-only, no AST rewrite.

### re + Pattern + Match — `poop/types/re.py` + `poop/transformers/re.py`

`re` mirrors Python's `re` module — regular expression matching, substitution, splitting, and compilation. `Pattern` and `Match` are the two wrapper classes, exposed both as namespace attributes (`re.Pattern`, `re.Match`) and as bare globals (mirroring how `UUID` is also reachable without the `uuid.` prefix).

| Operation | Returns | Notes |
|---|---|---|
| `re.match(pattern, string, flags=none)` | `Match \| NoneClass` | anchored at start |
| `re.search(pattern, string, flags=none)` | `Match \| NoneClass` | anywhere |
| `re.fullmatch(pattern, string, flags=none)` | `Match \| NoneClass` | full string |
| `re.findall(pattern, string, flags=none)` | `List[Str]` or `List[Tuple]` | tuples when groups exist |
| `re.finditer(pattern, string, flags=none)` | `Tuple[Match]` | materialised eagerly — POOP collections are not lazy |
| `re.sub(pattern, repl, string, count=none, flags=none)` | `Str` | |
| `re.subn(pattern, repl, string, count=none, flags=none)` | `Tuple(Str, Int)` | new string + count |
| `re.split(pattern, string, maxsplit=none, flags=none)` | `List[Str]` | |
| `re.escape(pattern)` | `Str` | escape regex meta-chars |
| `re.compile(pattern, flags=none)` | `Pattern` | |
| `re.IGNORECASE` / `MULTILINE` / `DOTALL` / `VERBOSE` / `ASCII` / `UNICODE` / `LOCALE` / `DEBUG` | `Int` | flag constants |
| `Pattern.match` / `.search` / `.fullmatch` / `.findall` / `.finditer` / `.sub` / `.subn` / `.split` | same as module-level | reuses the compiled regex |
| `Pattern.pattern` / `.flags` / `.groups` / `.groupindex` (properties) | `Str` / `Int` / `Int` / `Dict[Str, Int]` | |
| `Match.group()` | `Str` | whole match |
| `Match.group(i_or_name)` | `Str \| NoneClass` | unmatched optional → `none` |
| `Match.group(a, b, ...)` | `Tuple` | multiple groups |
| `Match.groups(default=none)` | `Tuple` | all numbered groups |
| `Match.groupdict(default=none)` | `Dict[Str, Str \| NoneClass]` | named groups |
| `Match.start(group=none)` / `.end(group=none)` | `Int` | |
| `Match.span(group=none)` | `Tuple(Int, Int)` | |
| `Match.expand(template)` | `Str` | apply `\1` / `\g<name>` backrefs |
| `Match.string` / `.re` (properties) | `Str` / `Pattern` | |

`re` and the `Pattern` / `Match` classes are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/re.py` — namespace-only, no AST rewrite.

### hashlib + Hash — `poop/types/hash.py` + `poop/transformers/hashlib.py`

`hashlib` mirrors Python's `hashlib` module — message digests (MD5, SHA-1/2/3, BLAKE2, SHAKE) and key-derivation functions (PBKDF2, scrypt). The shortcut messages live directly on `Bytes` so common code reads `b"abc".sha256().hexdigest()` — the receiver carries the data, the message names the algorithm.

| Operation | Returns | Notes |
|---|---|---|
| `hashlib.new(name, data=none)` | `Hash` | generic constructor |
| `hashlib.file_digest(path, digest, /)` | `Hash` | `path` is a `Path` — receiver-type divergence from CPython's `fileobj` |
| `hashlib.algorithms_available` (class attr) | `FrozenSet[Str]` | every algorithm OpenSSL exposes locally |
| `hashlib.algorithms_guaranteed` (class attr) | `FrozenSet[Str]` | algorithms guaranteed on every platform |
| `hashlib.Hash` (class attr) | `type[Hash]` | the wrapper class itself |
| `b.md5()` / `.sha1()` / `.sha224()` / `.sha256()` / `.sha384()` / `.sha512()` | `Hash` | shortcut on `Bytes` |
| `b.blake2b()` / `.blake2s()` | `Hash` | BLAKE2 family |
| `b.sha3_224()` / `.sha3_256()` / `.sha3_384()` / `.sha3_512()` | `Hash` | SHA-3 family |
| `b.shake_128()` / `.shake_256()` | `Hash` | length is passed to `.digest(length)` / `.hexdigest(length)` |
| `b.pbkdf2_hmac(hash_name, salt, iterations, dklen=none)` | `Bytes` | receiver = password |
| `b.scrypt(*, salt, n, r, p, maxmem=none, dklen=none)` | `Bytes` | receiver = password; defaults `maxmem=0`, `dklen=64` |
| `Hash.update(data)` | `none` | mutates in place |
| `Hash.digest(length=none)` | `Bytes` | `length` is required for shake hashes, ignored by the rest |
| `Hash.hexdigest(length=none)` | `Str` | same shape as `.digest` |
| `Hash.copy()` | `Hash` | independent clone |
| `Hash.digest_size` / `.block_size` (property) | `Int` | |
| `Hash.name` (property) | `Str` | |

`Str` does not carry the shortcut messages — encoding must be explicit (`"abc".encode("utf-8").sha256()`). This mirrors Python's bytes/str split and keeps the encoding step visible.

`hashlib` and `Hash` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/hashlib.py` — namespace-only, no AST rewrite.

### Slice — `poop/types/slice.py` + `poop/transformers/slice.py`

`slice(start, stop, step=None)` is **transformed** by `SliceTransformer` into a call to the POOP `Slice` constructor — the same approach as `range` → `Range`. The free builtin is not forbidden; it is rewritten transparently.

`obj.slice(start, stop, step=None)` is also accepted directly on every sequence type. Both forms are equivalent at runtime.

`Slice` is a first-class immutable POOP type (`poop/types/slice.py`) — hashable, comparable with `==`/`!=`, and reusable across collections.

| Method | Returns | Notes |
|---|---|---|
| `Slice(start, stop)` | `Slice` | Two-arg constructor |
| `Slice(start, stop, step)` | `Slice` | Three-arg constructor |
| `.start()` | `Int` | |
| `.stop()` | `Int` | |
| `.step()` | `Int \| NoneClass` | POOP `none` when not set |
| `.indices(length)` | `Tuple(Int, Int, Int)` | Normalised start/stop/step for a sequence of the given length; mirrors Python's `slice.indices()` |

`obj.slice(s: Slice)` overload is available on every sequence type in addition to the positional form:

| Type | Returns |
|---|---|
| `Str` | `Str` |
| `List` | `List` |
| `Tuple` | `Tuple` |
| `Bytes` | `Bytes` |
| `ByteArray` | `ByteArray` |
| `Range` | `List` |

> `Range.slice` returns `List` (not `Range`) because reconstructing a valid closed interval from sliced `Int` POOP values would require unpacking assumptions about the underlying range step.

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
| `ast.Call` with `frozenset(x)` | `_poop_frozenset_from(x)` |

### Range — `poop/transformers/range.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `range(stop)` / `range(start, stop)` / `range(start, stop, step)` | `_poop_range(...)` → `Range` |

### Raise — `poop/transformers/raise_.py`

Intercepts `UppercaseName.raise_(args)` (where `UppercaseName` starts with a capital letter) and rewrites it to a function call that works inside lambdas.

| Pattern | Replacement |
|---|---|
| `ExcType.raise_('msg')` | `_poop_raise(ExcType, 'msg')` |

> **Why not `ast.Raise`?** The transformer generates a function call (`_poop_raise(...)`) instead of an `ast.Raise` statement. Statements are illegal inside `lambda` expressions — POOP's primary block mechanism. This design allows `Try(lambda: KeyError.raise_("msg")).except_(...)` to work correctly.

> **Tradeoff**: `ExcType` must be a Python exception class (not a POOP object). Only uppercase-named receivers are intercepted; lowercase `obj.raise_()` is passed through to the object's own method at runtime.

### Class — `poop/transformers/class_.py`

Implicitly injects POOP `Object` as the base class of every user-defined class that has no explicit base, mirroring how Python 3 makes every class implicitly inherit from `object`.

| Pattern | Replacement |
|---|---|
| `class Foo:` | `class Foo(_poop_object):` |
| `class Foo(object):` | `class Foo(_poop_object):` |
| `class Foo(Object):` | `class Foo(_poop_object):` — backwards-compat for explicit Smalltalk-style declarations |
| `class Foo(Bar):` | unchanged — already has a base |

The POOP `Object` class is injected into `DEFAULT_NAMESPACE` as `_poop_object` so the rewritten AST resolves it at runtime (the mangled name is reserved by `no_poop_prefix`). User-defined classes automatically gain all `Object` methods: `print()`, `is_none()`, `not_none()`, `assert_()`, `class_name()`, `get_attr()`, etc.

> **Tradeoff**: classes that explicitly inherit from native Python types (e.g. `class Foo(Exception):`) are left unchanged — they do not gain POOP `Object` methods, consistent with how `Try` and `Error` interact with the native exception hierarchy.

