# Migration Recipes — Python → POOP

Quick translations of common Python idioms to POOP source code. For the full reference of which Python constructs are forbidden and why, see [`INFECTIONS.md`](INFECTIONS.md). For end-to-end programs, see [`examples/`](examples).

> Every snippet pair shows the Python form you would normally write and the POOP form the validators and transformers force you to write instead. Snippets are valid as POOP source — primitive literals like `0`, `"hi"`, `True` are wrapped to POOP types by transformers at parse time, so methods like `.at(0)` and `.print()` work directly on Python literals without any manual wrapping.

## Quick reference

A one-line summary of the most common substitutions. The sections below walk through each in context.

| Python | POOP |
|---|---|
| `print(x)` | `x.print()` |
| `if cond:` / `else:` | `cond.if_true(lambda: …)` / `cond.if_false(lambda: …)` |
| `for x in col:` | `col.do(lambda x: …)` |
| `while cond:` | `(lambda: cond).while_true(lambda: …)` |
| `not x` | `x.not_()` |
| `-x` | `x.negated()` |
| `len(x)` | `x.len()` |
| `x[i]` | `x.at(i)` |
| `x[a:b]` | `x.slice(a, b)` |
| `x and y` | `x.and_(lambda: y)` |
| `x or y` | `x.or_(lambda: y)` |

## Control flow

### `if` / `else`

```python
# Python
result = handle_admin() if user.is_admin() else handle_guest()
```

```python
# POOP
result = user.is_admin().if_true_if_false(
    lambda: handle_admin(),
    lambda: handle_guest(),
)
```

### Single-branch `if`

```python
# Python
if balance < 0:
    raise ValueError("overdraft")
```

```python
# POOP
(balance < 0).if_true(lambda: ValueError.raise_("overdraft"))
```

### `and` / `or` / `not`

```python
# Python
ok = is_admin and not is_locked or is_owner
```

```python
# POOP
ok = is_admin.and_(lambda: is_locked.not_()).or_(lambda: is_owner)
```

> The `lambda:` wrappers preserve short-circuit semantics — branches are only evaluated if reached.

## Iteration

### `for` loop

```python
# Python
for item in items:
    process(item)
```

```python
# POOP
items.do(lambda item: process(item))
```

### List / set / dict comprehension

```python
# Python
result = [x * 2 for x in xs if x > 0]
```

```python
# POOP
result = list(xs.filter(lambda x: x > 0).map(lambda x: x * 2))
```

> `map` and `filter` return lazy iterators. Materialize with `list(...)`, `tuple(...)`, `set(...)`, `bytes(...)`.

### `range` loop

```python
# Python
for i in range(1, 11):
    print(i)
```

```python
# POOP
range(1, 11).do(lambda i: i.print())
```

### `enumerate` / `zip`

```python
# Python
for i, name in enumerate(names):
    ...
for a, b in zip(xs, ys):
    ...
```

```python
# POOP
names.enumerate().do(lambda pair: ...)  # pair.at(0) is index, pair.at(1) is value
xs.zip(ys).do(lambda pair: ...)
```

## Free functions on objects

```python
# Python
n = len(xs)
y = abs(x)
print(x)
text = repr(x)
ok = isinstance(x, MyClass)
total = sum(xs)
biggest = max(xs)
```

```python
# POOP
n = xs.len()
y = x.abs()
x.print()
text = x.repr()
ok = x.is_instance(MyClass)
total = xs.sum()
biggest = xs.max()
```

> Same pattern for `getattr`/`setattr`/`hasattr`/`dir`/`format`/`hash`/`callable`/`ascii` → `x.get_attr(name)`, `x.set_attr(name, val)`, `x.has_attr(name)`, `x.dir()`, `x.format(spec)`, `x.hash()`, `x.callable()`, `x.ascii()`. `id(x)` has no method form: it answered CPython's address, which POOP has no business handing out — use `a.is_identical(b)`, the identity *question* it existed to enable. For `type(x)` use `x.class_name()` — or better, polymorphism instead of type dispatch.

### First match, with a fallback

```python
# Python
first = next((x for x in xs if p(x)), d)
```

```python
# POOP
first = xs.find(lambda x: p(x), default=d)
```

> Without `default=`, a miss answers `none` — which a matching `none` would too.

## Operators that look procedural

```python
# Python
y = -x
y = ~x
q, r = divmod(a, b)
y = round(x, 2)
```

```python
# POOP
y = x.negated()
y = x.bit_invert()
q, r = a.divmod(b)
y = x.round(2)
```

> Binary operators (`+`, `-`, `*`, `/`, `**`, `==`, `<`, …) stay native — the asymmetry is intentional, see `INFECTIONS.md` § "Binary infix operators".

## Subscripting and slicing

```python
# Python
first = xs[0]
window = xs[1:4]
```

```python
# POOP
first = xs.at(0)
window = xs.slice(1, 4)
```

> For reuse across collections, build a value with `slice(start, stop, step=None)` — the transformer rewrites the lowercase builtin into POOP's `Slice`. Pass it to `xs.slice(s)` on any sequence type.

## Membership

```python
# Python
3 in xs
"foo" in s
"key" in d
```

```python
# POOP
xs.includes(3)
s.includes("foo")
d.includes("key")
```

> `d.includes(k)` mirrors Python's `key in d` — checks keys. The views also respond to `.includes(...)` for the other axes: `d.keys().includes(k)`, `d.values().includes(v)`, `d.items().includes((k, v))`.

## Identity (`is`, `is None`)

```python
# Python
x is None
x is not None
x is y
y = f(x) if x is not None else d
```

```python
# POOP
x.is_none()
x.not_none()
x.is_identical(y)
y = x.if_not_none_if_none(lambda x: f(x), lambda: d)
```

> `is` is forbidden by the `no_is` validator. For `None` checks use `.is_none()` / `.not_none()`; for arbitrary identity use `.is_identical(other)` / `.not_identical(other)`. The two-branch form is `if_none_if_not_none(none_block, present_block)` or its twin `if_not_none_if_none`; chaining `.if_not_none(…).if_none(…)` tests the first block's *answer*, not `x`.

## Raise / try / except

```python
# Python
try:
    risky()
except ValueError as e:
    handle(e)
```

```python
# POOP
Try(lambda: risky()).except_(ValueError, lambda e: handle(e)).run()
```

> Inside lambdas you cannot `raise` — write `ExcType.raise_("msg")`. The `RaiseTransformer` rewrites it to a callable so it composes inside blocks.

## Context managers (`with`)

```python
# Python
with lock:
    critical_section()
```

```python
# POOP
With(lambda: lock).do(lambda _: critical_section())
```

> `With` takes a *factory lambda*, not the cm directly — entry is deferred until `do()` runs.

## What has no recipe

Some Python has no POOP translation at all, and looking for one is the wrong move — these are bans by design, not gaps waiting to be filled.

| Python | Why there is no POOP form |
|---|---|
| `open(...)`, `pathlib`, `io` | POOP has no file I/O. A program's only channels are `"prompt".input()` and `obj.print()`. |
| `import anything` | POOP is the language, not the library — it mirrors no stdlib module. The only injected names are `Try` and `With`. |
| `async def` / `await` | Nothing can drive a coroutine. |
| `exec` / `eval` / `compile`, `globals` / `locals` / `vars`, `breakpoint`, `exit` | Interpreter escape hatches. |
| `class X[T]`, `def m[T]()`, `type X = int` | POOP has no static types. Drop the parameter; the runtime types are POOP's own. |
| `class X(metaclass=M)`, `class X(foo=1)` | A class is built from its bases alone. A parent that must configure its subclasses answers a class-side message instead. |
| `def __getattr__(self, name)`, `__getattribute__`, `__init_subclass__`, `__set_name__` | Python's lookup, creation and descriptor protocols. `def does_not_understand(self, name)` is the one hook: it receives the selector as a `Str` and its answer is the message's. |

| `x: int`, `def f(x: int) -> str` | Not refused, but misleading: every literal becomes a POOP type, so a variable annotated `int` holds POOP's own integer at runtime. Leave annotations out. |

## Banned constructs

Every construct a validator refuses, and what to write instead. A row whose right-hand cell gives a reason rather than code is a ban with no substitute; [ADR 9](doc/adr/0009-a-validator-is-activated-only-with-its-substitute-except-definitive-bans.md) says which bans are definitive and why.

| Python | POOP instead, or why there is none | Validator |
|---|---|---|
| `ast.If` | `if/elif/else` looks like control flow; use `x.if_true(block)` / `x.if_false(block)` | `no_if` |
| `ast.IfExp` | Ternary expression `x if cond else y`; use `x.if_true(block)` / `x.if_false(block)` | `no_if` |
| `ast.For` | Loop looks procedural; use `col.do(block)`, `col.map(block)`, recursion | `no_loops` |
| `ast.While` | use `(lambda: cond).while_true(lambda: body)` | `no_loops` |
| `ast.AsyncFor` | Async variant; async has no substitute in POOP (see `no_async`) | `no_loops` |
| `ast.FunctionDef` (direct parent is not a `ClassDef`) | Free function is not a message to any object | `no_free_functions` |
| `ast.AsyncFunctionDef` (direct parent is not a `ClassDef`) | Async variant | `no_free_functions` |
| `print(...)` | `obj.print()` | `no_print` |
| `ast.Assert` | `obj.assert_('message')` (any truthy receiver) | `no_assert` |
| `ast.Raise` | `ExcType.raise_('msg')` | `no_raise` |
| `ast.Try` | `Try(block).except_(ExcType, handler).run()` | `no_try` |
| `ast.TryStar` | none — a definitive ban | `no_try` |
| `ast.With` | `With(lambda: cm()).do(lambda resource: body)` | `no_with` |
| `ast.AsyncWith` | none — a definitive ban | `no_with` |
| `ast.BoolOp` with `ast.And` | `x.and_(lambda: y)` | `no_and_or` |
| `ast.BoolOp` with `ast.Or` | `x.or_(lambda: y)` | `no_and_or` |
| `ast.AsyncFunctionDef` | POOP has no way to drive a coroutine | `no_async` |
| `ast.Await` | POOP has no way to drive a coroutine | `no_async` |
| `ast.UnaryOp` with `ast.Not` | `x.not_()` | `no_not` |
| `ast.UnaryOp` with `ast.USub` (operand is not `ast.Constant`) | `x.negated()` | `no_unary_minus` |
| `ast.UnaryOp` with `ast.UAdd` | `+x` is semantically a no-op and has no message-send equivalent — write the value directly | `no_unary_plus` |
| `ast.UnaryOp` with `ast.Invert` | `x.bit_invert()` | `no_invert` |
| `ast.Compare` with `ast.Is` | `x.is_none()` or `x.is_identical(other)` | `no_is` |
| `ast.Compare` with `ast.IsNot` | `x.not_none()` or `x.not_identical(other)` | `no_is` |
| `ast.Global` | `global` breaks encapsulation — state lives in instances, not in global scope | `no_global` |
| `ast.Nonlocal` | `nonlocal` manipulates outer scope — use instance variables | `no_global` |
| `ast.Yield` | `col.do(block)`, `col.map(block)` | `no_yield` |
| `ast.YieldFrom` | `col.do(block)`, `col.map(block)` | `no_yield` |
| `ast.NamedExpr` | `:=` combines assignment and expression — use separate assignment | `no_walrus` |
| a `decorator_list` entry on `ast.FunctionDef` / `ast.AsyncFunctionDef` / `ast.ClassDef` (not a bare `ast.Name` among `staticmethod`, `classmethod`, `property`) | send the message | `no_decorator` |
| `ast.Name` `staticmethod` / `classmethod` / `property` (not a `decorator_list` entry) | use it as a decorator | `no_class_machinery` |
| `ast.Name` `super` (not the callee of an `ast.Call`) | `super().method(...)` | `no_class_machinery` |
| `super()` (the nearest enclosing function is a `lambda`) | send it from the method and hand the block its answer | `no_class_machinery` |
| `ast.Return` with a value (directly in an `__init__` body) | `__init__` builds the receiver and answers nothing | `no_class_machinery` |
| an `ast.keyword` on `ast.ClassDef` — `class X(foo=1)`, `class X(metaclass=M)`, `class X(**opts)` | a class is built from its bases alone | `no_class_keyword` |
| `ast.FunctionDef` in an `ast.ClassDef` body (named `__getattribute__`, `__getattr__`, `__setattr__`, `__delattr__`, `__dir__`) | `does_not_understand(self, name)` for the messages a class does not answer; `set_attr`, `del_attr`, `dir` already exist | `no_dunder_def` |
| `ast.FunctionDef` in an `ast.ClassDef` body (named `__new__`, `__init_subclass__`, `__class_getitem__`, `__subclasshook__`) | a class is built from its bases alone | `no_dunder_def` |
| `ast.FunctionDef` in an `ast.ClassDef` body (named `__set_name__`, `__get__`, `__set__`, `__delete__`) | a POOP object is reached by messages, not by descriptors | `no_dunder_def` |
| `type X = int` | Creates an alias for a Python builtin type — incompatible with POOP runtime types | `no_type_alias` |
| `class X[T]`, `def m[T](self)`, `type X[T] = …` — a PEP 695 type parameter | POOP has no static types; the parameter is named as written (`drop the [T]`, `[*Ts]`, `[**P]`) | `no_type_alias` |
| `ast.Match` | polymorphism + `if_true(block)`/`if_false(block)` | `no_match` |
| `ast.JoinedStr` | concatenation: `("Hello, " + name)`, `("count: " + str(n))` | `no_fstring` |
| `ast.TemplateStr` | concatenation: `("Hello, " + name)`, `("count: " + str(n))` | `no_fstring` |
| `len(x)` | `x.len()` | `no_len` |
| `abs(x)` | `x.abs()` | `no_abs` |
| `hash(x)` | `x.hash()` | `no_hash` |
| `isinstance(x, T)` | `x.is_instance(T)` | `no_isinstance` |
| `repr(x)` | `x.repr()` | `no_repr` |
| `ascii(x)` | `x.ascii()` | `no_ascii` |
| `issubclass(A, B)` | `A.is_subclass(B)` | `no_issubclass` |
| `callable(x)` | `x.callable()` | `no_callable` |
| `id(x)` | `a.is_identical(b)` | `no_id` |
| `all(col)` | `col.all(block)` | `no_all` |
| `any(col)` | `col.any(block)` | `no_any` |
| `min(a, b)` | `a.min(b)` (on `Int`/`Float`) | `no_min`, `no_max` |
| `min(a, b, c, ...)` | `a.min(b, c, ...)` (variadic, on `Int`/`Float`) | `no_min`, `no_max` |
| `min(a, b, key=fn)` | `a.min(b, key=fn)` (keyword-only, on `Int`/`Float`) | `no_min`, `no_max` |
| `min(iterable)` | `iterable.min()` | `no_min`, `no_max` |
| `min(iterable, key=fn)` | `iterable.min(key=fn)` | `no_min`, `no_max` |
| `min(iterable, default=x)` | `iterable.min(default=x)` | `no_min`, `no_max` |
| `bin(n)` | `n.bin()` | `no_bin` |
| `hex(n)` | `n.hex()` | `no_bin` |
| `oct(n)` | `n.oct()` | `no_bin` |
| `chr(n)` | `n.chr()` | `no_chr` |
| `ord(c)` | `c.ord()` | `no_chr` |
| `divmod(a, b)` | `a.divmod(b)` | `no_divmod` |
| `pow(a, b)` | `a.pow(b)` | `no_pow` |
| `getattr(x, name)` | `x.get_attr(name)` | `no_getattr` |
| `getattr(x, name, default)` | `x.get_attr(name, default)` | `no_getattr` |
| `hasattr(x, s)` | `x.has_attr(s)` | `no_hasattr` |
| `format(x, spec)` | `x.format(spec)` — except on a `Str`, where it is `"{:spec}".format(text)` | `no_format` |
| `iter(col)` | `col.iter()` | `no_iter` |
| `next(it)` | `it.next()` | `no_iter` |
| `next(it, default)` | `it.next(default)` | `no_iter` |
| `aiter(col)` | `col.iter()` | `no_iter` |
| `anext(it)` | `it.next()` | `no_iter` |
| `setattr(obj, name, val)` | `obj.set_attr(name, val)` | `no_setattr` |
| `delattr(obj, name)` | `obj.del_attr(name)` | `no_setattr` |
| `globals()` | scope introspection — state lives in instances | `no_introspection` |
| `locals()` | scope introspection — state lives in instances | `no_introspection` |
| `vars(obj)` | exposes raw Python-native slot values (`_value`, `_items`, `_data`) that are not POOP objects — breaks encapsulation and the "all methods return POOP types" rule; no clean substitute | `no_introspection` |
| `dir(obj)` | `obj.dir()` | `no_dir` |
| `.__dict__` | none — the ban is the decision, as `no_introspection` already argues for `vars` | `no_dunder_attribute` |
| `.__class__` | `obj.class_()` | `no_dunder_attribute` |
| `.__name__` | `Klass.name()` | `no_dunder_attribute` |
| `.__mro__` / `.__bases__` | `Klass.superclass()` | `no_dunder_attribute` |
| `.__len__()` | `obj.len()` | `no_dunder_attribute` |
| `.__contains__(x)` | `col.includes(x)` | `no_dunder_attribute` |
| `.__abs__()` | `n.abs()` | `no_dunder_attribute` |
| `.__hash__()` | `obj.hash()` | `no_dunder_attribute` |
| anything else dunder-shaped | none — it is Python's protocol, not POOP's message surface; the sentence names the scope (`dunder globals`, `dunder class attributes`, `dunder locals`), since a class-body `__slots__ = ("a",)` is no global | `no_dunder_attribute` |
| `__builtins__` | the raw Python builtins **dict**, live and mutable — `__builtins__.clear()` used to run clean through every validator and corrupt the interpreter | `no_dunder_name` |
| `__loader__` / `__spec__` | `BuiltinImporter` / `ModuleSpec` — naked Python natives, and an import surface `no_import` bans | `no_dunder_name` |
| `__name__` / `__package__` / `__debug__` | raw Python `str` / `None` / `bool`, not POOP objects | `no_dunder_name` |
| anything else dunder-shaped | none — it is Python's protocol, not POOP's message surface | `no_dunder_name` |
| `type(x)` | `x.class_name()` or polymorphism | `no_type` |
| `exec(code)` | metaprogramming — not allowed in POOP | `no_exec` |
| `eval(expr)` | metaprogramming — not allowed in POOP | `no_exec` |
| `compile(src, ...)` | metaprogramming — not allowed in POOP | `no_exec` |
| `exit()` | process control — POOP offers no substitute | `no_exit` |
| `quit()` | process control — POOP offers no substitute | `no_exit` |
| `breakpoint()` | Python-specific debugging — POOP offers no substitute | `no_breakpoint` |
| `help(obj)` | interactive escape hatch (opens the Python pager) exposing wrapper internals — POOP offers no substitute | `no_help` |
| `input(prompt)` | `prompt.input()` (`poop/types/string.py`) | `no_input` |
| `open(path, ...)` | POOP offers no substitute; it has no file I/O | `no_open` |
| `ast.Delete` | objects have no explicit destruction — simply do not delete | `no_del` |
| `ast.Import` | POOP is the language, not the library — there is no stdlib surface to import, and an import would bind raw CPython values that answer to no POOP message | `no_import` |
| `ast.ImportFrom` | `from os import getcwd` would leak a raw Python callable returning a raw `str` | `no_import` |
| `ast.Name` with `id` starting in `_poop_` | mangled identifier reserved for the runtime — rewriters target it, user code must not | `no_poop_prefix` |
| `ast.Attribute` with `attr` starting in `_poop_` | keeps the runtime helpers reachable for the rewritten AST but invisible to handwritten code | `no_poop_prefix` |
| `ast.arg`, `ast.FunctionDef`, `ast.ClassDef` naming one | a binding is a reference too; the parameter's annotation is walked as well, so `x: _poop_int` is refused like `-> _poop_int` | `no_poop_prefix` |
| `ast.Attribute` (`attr` starts with a single `_`) | send the object a message that answers it; `get_attr` refuses a private name too | `no_private_attribute` |
| `ast.Assign` with target `ast.Name` in the protected set | reassigning a namespace name (`Try = 42`) breaks every later call to `Try(…)` | `no_namespace_shadow` |
| `ast.AnnAssign` with target `ast.Name` in the protected set | annotated form (`Try: int = 42`) — same problem | `no_namespace_shadow` |
| `ast.AugAssign` with target `ast.Name` in the protected set | augmented form (`Try += 1`) — same problem | `no_namespace_shadow` |
| `ast.ClassDef` whose `name` is in the protected set | `class Try: …` binds `Try` at module level, shadows the namespace | `no_namespace_shadow` |
| Unpacking targets (`ast.Tuple` / `ast.List` / `ast.Starred`) holding a protected name | tuple unpacking (`Try, x = 1, 2`) still rebinds the name | `no_namespace_shadow` |
| `def`/`async def`/`lambda` parameters in the protected set | a parameter named after a binding (`def m(self, Try): …`, `lambda Try: …`) shadows it inside the body and fails confusingly | `no_namespace_shadow` |
| rebinding a builtin a transformer rewrites (`str = "x"`, `class KeyError(Object)`, `def m(self, ValueError)`) | rebinding one would silently retarget the interpreter's internals | `no_builtin_shadow` |
| `sum(col)` | `col.sum()` | `no_sum` |
| `sum(col, start)` | `col.sum(start)` | `no_sum` |
| `map(func, col)` | `col.map(block)` returning `Map` (lazy) | `no_map`, `no_filter` |
| `filter(func, col)` | `col.filter(block)` returning `Filter` (lazy) | `no_map`, `no_filter` |
| `round(x)` | `x.round()` | `no_round` |
| `round(x, n)` | `x.round(n)` | `no_round` |
| `sorted(col)` | `col.sorted()` | `no_sorted`, `no_reversed` |
| `sorted(col, key=fn, reverse=True)` | `col.sorted(key=fn, reverse=True)` | `no_sorted`, `no_reversed` |
| `reversed(col)` | `col.reversed()` | `no_sorted`, `no_reversed` |
| `ast.Compare` (op is `ast.In`) | `col.includes(x)` | `no_in` |
| `ast.Compare` (op is `ast.NotIn`) | `col.includes(x).not_()` | `no_in` |
| `ast.Subscript` (no `ast.Slice` involved, `ast.Load`) | `obj.at(key)` | `no_subscript` |
| `ast.Subscript` (no `ast.Slice` involved, `ast.Store`) | `obj.at_put(key, value)` | `no_subscript` |
| `ast.Subscript` (a bare `ast.Slice` or an `ast.Tuple` containing one (extended slices like `obj[i:j, k:l]`), `ast.Load`) | `obj.slice(start, stop)` | `no_subscript` |
| `ast.Subscript` (a slice under `ast.Store`) | `obj.at_put(index, value)`, one element at a time | `no_subscript` |
| `ast.ListComp` / `ast.SetComp` / `ast.DictComp` / `ast.GeneratorExp` | `col.map(block)`, `col.filter(block)` | `no_comprehension` |
