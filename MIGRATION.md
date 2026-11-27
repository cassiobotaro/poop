# Migration Recipes — Python → POOP

Quick translations of common Python idioms to POOP source code. [*Banned constructs*](#banned-constructs) lists every forbidden construct and its substitute, and [*Type reference*](#type-reference) lists what each type answers. The decision log, [`doc/adr/`](doc/adr/), records why each rule exists. For end-to-end programs, see [`examples/`](examples).

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
| `await x` | `x.await_()` |
| `asyncio.run(main())` | `Async.run(obj.main())` |

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

> Binary operators (`+`, `-`, `*`, `/`, `**`, `==`, `<`, …) stay native. The asymmetry is intentional; see [ADR 27](doc/adr/0027-binary-operators-stay-unary-ones-go-chained-comparison-is-allowed-on-ergonomics.md).

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

## Async methods (`async def` / `await`)

```python
# Python
import asyncio


class Page:
    async def fetch(self, n):
        await asyncio.sleep(0.01)
        return n * 2

    async def main(self):
        return await asyncio.gather(self.fetch(1), self.fetch(2))


print(asyncio.run(Page().main()))
```

```python
# POOP
class Page(Object):
    async def fetch(self, n):
        Async.sleep(0.01).await_()
        return n * 2

    async def main(self):
        return Async.gather(*[1, 2].map(lambda n: self.fetch(n))).await_()


Async.run(Page().main()).repr().print()
```

> `async def` is a method only in a class body. `x.await_()` is rewritten to `await x`, so it is sent only directly inside an async method: a block cannot await, so it answers the coroutine and the method awaits that answer, as in `flag.if_true_if_false(lambda: self.a(), lambda: self.b()).await_()`.

## What has no recipe

Some Python has no POOP translation at all, and looking for one is the wrong move — these are bans by design, not gaps waiting to be filled.

| Python | Why there is no POOP form |
|---|---|
| `open(...)`, `pathlib`, `io` | POOP has no file I/O. A program's only channels are `"prompt".input()` and `obj.print()`. |
| `import anything` | POOP is the language, not the library — it mirrors no stdlib module. The only injected names are `Try`, `With` and `Async`. |
| `exec` / `eval` / `compile`, `globals` / `locals` / `vars`, `breakpoint`, `exit` | Interpreter escape hatches. |
| `class X[T]`, `def m[T]()`, `type X = int` | POOP has no static types. Drop the parameter; the runtime types are POOP's own. |
| `class X(metaclass=M)`, `class X(foo=1)` | A class is built from its bases alone. A parent that must configure its subclasses answers a class-side message instead. |
| `def __getattr__(self, name)`, `__getattribute__`, `__init_subclass__`, `__set_name__` | Python's lookup, creation and descriptor protocols. `def does_not_understand(self, name)` is the one hook: it receives the selector as a `Str` and its answer is the message's. |

| `x: int`, `def f(x: int) -> str` | Not refused, but misleading: every literal becomes a POOP type, so a variable annotated `int` holds POOP's own integer at runtime. Leave annotations out. |

## Banned constructs

This table lists every construct a validator refuses and what to write instead. A row whose right-hand cell gives a reason rather than code is a ban with no substitute. [ADR 9](doc/adr/0009-a-validator-is-activated-only-with-its-substitute-except-definitive-bans.md) says which bans are definitive and why.

| Python | POOP instead, or why there is none | Validator |
|---|---|---|
| `ast.If` | `if/elif/else` looks like control flow; use `x.if_true(block)` / `x.if_false(block)` | `no_if` |
| `ast.IfExp` | Ternary expression `x if cond else y`; use `x.if_true(block)` / `x.if_false(block)` | `no_if` |
| `ast.For` | Loop looks procedural; use `col.do(block)`, `col.map(block)`, recursion | `no_loops` |
| `ast.While` | use `(lambda: cond).while_true(lambda: body)` | `no_loops` |
| `ast.AsyncFor` | none — no POOP value is an asynchronous iterator | `no_loops` |
| `ast.FunctionDef` (direct parent is not a `ClassDef`) | Free function is not a message to any object | `no_free_functions` |
| `ast.AsyncFunctionDef` (direct parent is not a `ClassDef`) | Async variant | `no_free_functions` |
| `print(...)` | `obj.print()` | `no_print` |
| `ast.Assert` | `obj.assert_('message')` (any truthy receiver) | `no_assert` |
| `ast.Raise` | `ExcType.raise_('msg')` | `no_raise` |
| `ast.Try` | `Try(block).except_(ExcType, handler).run()` | `no_try` |
| `ast.TryStar` | none — a definitive ban | `no_try` |
| `ast.With` | `With(lambda: cm()).do(lambda resource: body)` | `no_with` |
| `ast.AsyncWith` | none — POOP enters no asynchronous context manager | `no_with` |
| `ast.BoolOp` with `ast.And` | `x.and_(lambda: y)` | `no_and_or` |
| `ast.BoolOp` with `ast.Or` | `x.or_(lambda: y)` | `no_and_or` |
| `ast.Await` | `x.await_()`, inside an async method | `no_async` |
| `x.await_()` (nearest enclosing function is not an `async def`) | send it directly inside an async method; a block answers the coroutine and the method awaits that answer | `no_misplaced_await` |
| `x.await_(arg)` | `x.await_()` takes no arguments | `no_misplaced_await` |
| `x.await_` (read, not sent) | `x.await_()` | `no_misplaced_await` |
| `def await_(self)` | name the method something else; `await_` is reserved | `no_misplaced_await` |
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
| `ast.AsyncFunctionDef` in an `ast.ClassDef` body (a dunder other than `__call__`, `__aenter__`, `__aexit__`) | define it with `def`: Python calls it without awaiting it | `no_dunder_def` |
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
| `ord(c)` | `c.ord()`, on a `str`, `bytes` or `bytearray` of length one | `no_chr` |
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

## Type reference

These tables list what each type answers, message by message. The reasoning behind each choice is in [`doc/adr/`](doc/adr/).

### The class side (`PoopMeta`)

| Smalltalk message | Method | Behavior |
|---|---|---|
| `Foo name` | `Foo.name()` | the class's name as `Str` |
| `Foo superclass` | `Foo.superclass()` | the superclass **object**, or `none` at the root |
| `Foo respondsTo: #m` | `Foo.has_attr(name)` | `Boolean`; spelled as the instance side, per `CONTRIBUTING`'s naming rule |
| `Foo printNl` | `Foo.print()` | prints the class's name |
| `Foo doesNotUnderstand: #m` | `Foo.does_not_understand(name)` | same hook as `Object`'s |
| `Foo hash` | `Foo.hash()` | `Int` |
| `Foo isNil` / `Foo notNil` | `Foo.is_none()` / `Foo.not_none()` | always `false` / `true` |
| `Foo not` | `Foo.not_()` | always `false` — a class is truthy |
| `Foo printString` | `Foo.repr()` / `Foo.ascii()` | the class's name, matching `print` |
| — | `Foo.callable()` | always `true` |
| — | `Foo.dir()` / `Foo.format(spec)` | `List` of `Str` / `Str` |
| `x class` | `x.class_()` | the class object itself; `class_name()` is now `x.class_().name()` |

### `object`

`does_not_understand`, Smalltalk's `doesNotUnderstand:`:

| Smalltalk message | Method | Behavior |
|---|---|---|
| `isNil` | `is_none()` | always `false` for Object |
| `notNil` | `not_none()` | always `true` for Object |
| `not` | `not_()` | `false if bool(self) else true` |
| `class` | `class_name()` | `type(self).__name__` as `Str` |
| `perform:` | `get_attr(name)` | `getattr` with optional default |
| — | `dir()` | sorted `List` of `Str` attribute names (`builtins.dir(self)`) |

### `None`

| Method | `Object` | `NoneClass` |
|---|---|---|
| `is_none()` | `false` | `true` |
| `not_none()` | `true` | `false` |
| `if_none(block)` | does not execute | executes block |
| `if_not_none(block)` | executes passing `self` | does not execute |
| `if_none_if_not_none(none_block, present_block)` | runs `present_block` with `self` | runs `none_block` |
| `if_not_none_if_none(present_block, none_block)` | runs `present_block` with `self` | runs `none_block` |

### `bool`

| Smalltalk message | Method |
|---|---|
| `ifTrue:` / `ifFalse:` | `if_true(block)` / `if_false(block)` |
| `ifTrue:ifFalse:` / `ifFalse:ifTrue:` | `if_true_if_false(t, f)` / `if_false_if_true(f, t)` |
| `and:` / `or:` (lazy) | `and_(block)` / `or_(block)` |
| `not` / `xor:` / `eqv:` | `not_()` / `xor(other)` / `eqv(other)` |
| `&` / `\|` (eager) | `__and__(other)` / `__or__(other)` |
| `assert:` | `assert_(message)` (on `Object`, not just `Boolean`) | raises `AssertionError(message)` if `bool(self)` is falsy; returns `self` otherwise |

### Blocks

| Smalltalk message | POOP idiom |
|---|---|
| `[cond] whileTrue: [body]` | `(lambda: cond).while_true(lambda: body)` |
| `[cond] whileFalse: [body]` | `(lambda: cond).while_false(lambda: body)` |
| `[block] value` | `(lambda: expr)()` |
| `[block] value: arg` | `(lambda x: expr)(arg)` |

### Collection methods

| Smalltalk message | POOP method | Behavior |
|---|---|---|
| `do:` | `do(block)` | visits each element; returns `none` (substitute for `for` loop) |
| `collect:` | `map(block)` | returns `Map` (lazy); materialize via `list(...)`/`tuple(...)`/etc. |
| `select:` | `filter(block)` | returns `Filter` (lazy); same materialization |
| `reject:` | `filter_false(block)` | returns `Filter` (lazy) with the predicate inverted |
| `detect:` / `detect:ifNone:` | `find(block, default=…)` | first element satisfying block, or `default` — POOP `none` when none is given |
| `inject:into:` | `reduce(init, block)` | fold with required initial value; returns accumulated result |
| — | `sum(start=...)` | sum of elements; `Int(0)` for empty; optional `start` mirrors Python `sum(it, start)` |
| — | `min(key=None, default=...)` | smallest element; mirrors Python `min` |
| — | `max(key=None, default=...)` | largest element; mirrors Python `max` |
| — | `all(block)` | `true` if block holds for every element |
| — | `any(block)` | `true` if block holds for at least one element |
| — | `enumerate(start=Int(0))` | returns an `Enumerate` of `Tuple(Int(i), item)` pairs; a source that is not a collection is refused on construction |
| — | `zip(*others, strict=false)` | returns a `Zip` of `Tuple(...)`; a source that is not a collection is refused on construction; a strict mismatch numbers collections, the receiver being 1, so `a.zip(b)` and `zip(a, b)` report the same position |

### Builtin-mirroring signatures

| Type | Method | Signature | Notes |
|---|---|---|---|
| `Int` | `to_bytes` | `to_bytes(length=Int(1), byteorder=Str("big"), signed=false)` | `signed` is keyword-only, like `int.to_bytes` |
| `Int` | `from_bytes` | `from_bytes(bytes, byteorder=Str("big"), signed=false)` | classmethod; `signed` keyword-only |
| `Float` | `from_number` | `from_number(x)` | classmethod (Python 3.14); `x` an int, bool or float, refused otherwise by `a_number` |
| `Complex` | `from_number` | `from_number(x)` | classmethod (Python 3.14); `x` an int, bool, float or complex; `complex.from_number(1j)` answers `1j` unchanged |
| `ByteArray` | `resize` | `resize(size)` | Python 3.15; in place, answers `none`; a negative size is CPython's `ValueError` |
| `Str` | `format_map` | `format_map(mapping)` | `mapping` a `Dict`, `FrozenDict` or `MappingProxy`, refused otherwise by `a_mapping`; a positional field keeps CPython's `ValueError` |
| `Str` | `maketrans` | `maketrans(x, y=none, z=none)` | staticmethod; one mapping, or two equal-length strings and an optional third to delete; answers a `Dict` |
| `Str` | `translate` | `translate(table)` | `table` a mapping or a `List`/`Tuple`/`Str`, crossed to Python by `translation_table`; a `none` value deletes |
| `Bytes`, `ByteArray` | `maketrans` | `maketrans(frm, to)` | staticmethod; answers `bytes` on both, as CPython does |
| `Bytes`, `ByteArray` | `translate` | `translate(table, delete=b"")` | `table` may be `none`; a table not 256 bytes long is CPython's `ValueError`; `delete` applies before the mapping; a `bytearray` answers a new `bytearray` and is left untouched |
| `List`, `Tuple` | `index` | `index(obj, start=none, stop=none)` | optional search bounds; either may be given alone, as in Python |
| `MemoryView` | `tobytes` | `tobytes(order=Str("C"))` | `order` ∈ `{"C", "F", "A"}` |
| `MemoryView` | `hex` | `hex(sep=none, bytes_per_sep=Int(1))` | mirrors `Bytes.hex`; the one message that shows the contents |
| `MemoryView` | `tolist` | `tolist()` | a `List` of `Int`, one per byte; takes no argument, as `memoryview.tolist` does |
| `MemoryView` | `readonly` | `readonly()` | a `Boolean`: `true` over `bytes`, `false` over `bytearray`; a method, where CPython has an attribute |
| `Set`, `FrozenSet` | `union`, `intersection`, `difference` | `(*others)` | each operand may be **any iterable** (`List`/`Tuple`/…), not only another set |
| `Set`, `FrozenSet` | `symmetric_difference`, `isdisjoint`, `issubset`, `issuperset` | `(other)` | operand may be any iterable |
| `Set` | `update`, `intersection_update`, `difference_update` | `(*others)` | in-place; operands may be any iterable |
| `Set` | `symmetric_difference_update` | `(other)` | in-place; operand may be any iterable |
| `Dict` | `update` | `update(other=none, **pairs)` | `other` is a `Dict`, a `MappingProxy`, or an iterable of 2-element `(key, value)` pairs — a wrong-length element raises the faithful `ValueError`; both halves are optional, as in `dict.update([E], **F)`, and a keyword wins over the same key in the mapping |
| `Int` | `gcd`, `lcm` | `gcd(*others)`, `lcm(*others)` | any number of operands: `(12).gcd()` is 12, `(4).gcd(6, 8)` is 2 |
| `Int` | `comb`, `perm` | `comb(k)`, `perm(k=none)` | `(2).comb(5)` is 0; `(5).perm()` is the factorial |
| `Int` | `isqrt`, `factorial` | `isqrt()`, `factorial()` | a negative receiver is refused; `Boolean` answers all six through its int side |
| `Float` | `isnan`, `isinf`, `isfinite`, `isnormal`, `issubnormal`, `signbit` | no arguments | `math`'s answer as a `Boolean`: `(-0.0).signbit()` is `True` |

### `range`

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
| `slice(start, stop, step=None)` | slice → `Range` |
| `slice(slice_obj)` | slice via `Slice` value object → `Range` |
| `reversed()` | returns reversed `Range` |
| `includes(value)` | `true` if `value` is in the range |
| `count(value)` | number of occurrences (always `0` or `1`) |
| `index(value)` | position of `value`, or raises `ValueError` (`range has no element equal to 9`) |
| `start()` / `stop()` / `step()` | the underlying `Int` bounds |

### `slice`

| Method | Returns | Notes |
|---|---|---|
| `slice(start, stop)` | `Slice` | Two-arg constructor |
| `slice(start, stop, step)` | `Slice` | Three-arg constructor |
| `.start()` | `Int` | |
| `.stop()` | `Int` | |
| `.step()` | `Int \| NoneClass` | POOP `none` when not set |
| `.indices(length)` | `Tuple(Int, Int, Int)` | Normalised start/stop/step for a sequence of the given length; mirrors Python's `slice.indices()` |

A slice is immutable, hashable, comparable with `==`/`!=`, and reusable across collections. `obj.slice(s, stop)`, a slice followed by a bound, is refused. What `obj.slice(...)` answers, by receiver:

| Type | Returns |
|---|---|
| `Str` | `Str` |
| `List` | `List` |
| `Tuple` | `Tuple` |
| `Bytes` | `Bytes` |
| `ByteArray` | `ByteArray` |
| `Range` | `Range` |

### Dict views

| View | iter | set ops | comparison | mapping |
|---|---|---|---|---|
| `DictKeys` | `DictKeyIterator` | `\|`, `&`, `-`, `^` → `Set`; `isdisjoint` | `__eq__`, `__le__`, `__lt__`, `__ge__`, `__gt__` (set semantics) | `mapping()` → `MappingProxy` |
| `DictValues` | `DictValueIterator` | none (values may be unhashable) | inherits `Object` identity and hash (Python parity) | `mapping()` |
| `DictItems` | `DictItemIterator` (yields `Tuple(k, v)`) | `\|`, `&`, `-`, `^` → `Set` of `Tuple`; `isdisjoint` | full set semantics like `DictKeys` | `mapping()` |

### `MappingProxy`

`view.mapping()` on the three dict views answers a read-only `MappingProxy` over the dict, as `types.MappingProxyType` does. It answers the read messages (`at`, `get`, `keys`, `values`, `items`, `len`, `includes`, `iter`, `copy`, `reversed`, and `|` answering a `Dict`) and no mutator. It equals a `Dict` or `MappingProxy` with the same items and is unhashable.

### `Ellipsis`

`...` prints as `Ellipsis` and `class_name()` answers `ellipsis`, as `str(...)` and `type(...).__name__` do in CPython.

### Printing

| Message | Behavior |
|---|---|
| `obj.print()` | prints `str(obj)` followed by `\n`; returns `None` |
| `obj.print(end="")` | controls the terminator |
| `obj.print(flush=True)` | forces buffer flush |
| `list.print(sep=", ")` | `List`/`Tuple`: joins elements with `sep` (default `" "`) |
| `"".print()` | prints a blank line |
| a container that holds itself | shows `[...]`, `(...)` or `{...}` where it recurs, as CPython does: `[1, [...]]` |

### `Error`

| Method | Behavior |
|---|---|
| `message()` | returns exception message as `Str` |
| `kind()` | returns the POOP exception class; `kind().name()` for the name as `Str` |
| `cause()` | the error this one was raised from (`raise_from`), or `none` |
| `context()` | the error being handled when this one was raised, or `none` when there was none or it was suppressed |

### `Try`

| Message | Method | Behavior |
|---|---|---|
| `[block] on: ExcType do: handler` | `Try(block).except_(ExcType, handler)` | registers a handler; chainable |
| *(Python's `else`)* | `Try(block).else_(block)` | runs only when nothing was raised, with the protected value; chainable |
| `[block] ensure: finallyBlock` | `Try(block).finally_(block)` | sets finally block **and** executes; answers the protected block's value |
| *(terminal)* | `.run()` | executes without finally block; answers the protected block's value |
| *(terminal, in an async method)* | `.await_()` | awaits the block's coroutine inside the guard; a handler or `else_` may answer a value or a coroutine, which is awaited; answers the protected block's value |

`.run()` and `.finally_()` refuse a block that answers a coroutine: its failure would be raised only when awaited, after the guard is over.

### `With`

| Message | Method | Behavior |
|---|---|---|
| `[block] value: aResource` | `With(lambda: cm).do(lambda resource: body)` | acquires resource via `__enter__`, runs body, calls `__exit__`; answers the body's value |

`.do()` refuses a body that answers a coroutine, which would run after the manager exits; `AsyncWith` guards an awaiting body.

### `Async`

| Message | Method | Behavior |
|---|---|---|
| *(Python's `asyncio.run`)* | `Async.run(coroutine)` | runs the coroutine on a new event loop; answers its value |
| `(Delay forSeconds: n) wait` | `Async.sleep(delay, result=none)` | a coroutine that suspends for `delay` seconds and answers `result` |
| *(Python's `asyncio.gather`)* | `Async.gather(*coroutines)` | a coroutine that runs them concurrently and answers a `List` of their values, in order |

`Async` has no instances. Sending an async method answers a `coroutine`, which prints as `<coroutine>` and is awaited once with `.await_()`.

### Builtins a program may call

| Allowed | Why |
|---|---|
| `__build_class__` | what the `class` statement itself calls |
| `__name__` | read while creating a class |
| `super` | already the documented allowance — without it inheritance breaks entirely |
| `classmethod` / `staticmethod` / `property` | class-definition machinery with no message-passing substitute, by the same argument as `super`; `examples/patterns/` uses the first two |

## Rewrites

The transformers rewrite the source before it runs, so that no bare Python value reaches the program.

| Python | AST node | Replacement |
|---|---|---|
| `int` | `ast.Constant(value=int)` (except `bool`) | `_poop_int(n)` |
| `int` | `ast.UnaryOp(USub, Constant(int))` | `_poop_int(-n)` — collapsed negative literal |
| `int` | `ast.Call` with `int(x)` or `int(s, base)` | `_poop_int_from(x)` / `_poop_int_from(s, base)` |
| `float` | `ast.Constant(value=float)` | `_poop_float(n)` |
| `float` | `ast.UnaryOp(USub, Constant(float))` | `_poop_float(-n)` — collapsed negative literal |
| `float` | `ast.Call` with `float(x)` | `_poop_float_from(x)` |
| `Ellipsis` | `ast.Constant(value=Ellipsis)` | `_poop_ellipsis` |
| `Ellipsis` | `ast.Name(id="Ellipsis")` | `_poop_ellipsis` |
| `bool` | `ast.Constant(value=True)` | `_poop_true` |
| `bool` | `ast.Constant(value=False)` | `_poop_false` |
| `bool` | `ast.Call` with `bool(x)` | `_poop_bool_from(x)` |
| `None` | `ast.Constant(value=None)` | `_poop_none` |
| `str` | `ast.Constant(value=str)` | `_poop_str(s)` |
| `str` | the docstring of a class or function | left as it is — CPython stores it as `__doc__`; wrapped, it was an expression statement built on every call |
| `str` | `ast.Call` with `str(...)` | `_poop_str_from(...)`, whatever the arity |
| `bytes` | `ast.Constant(value=bytes)` | `_poop_bytes(b)` |
| `bytes` | `ast.Call` with `bytes(x)` or `bytes(s, enc)` | `_poop_bytes_from(x)` / `_poop_bytes_from(s, enc)` |
| `list` | `ast.List` (Load context) | `_poop_list(*elts)` |
| `list` | `ast.Call` with `list(...)` | `_poop_list_from(x)` |
| `tuple` | `ast.Tuple` (Load context) | `_poop_tuple(*elts)` |
| `tuple` | `ast.Call` with `tuple(...)` | `_poop_tuple_from(x)` |
| `set` | `ast.Set` | `_poop_set(*elts)` |
| `set` | `ast.Call` with `set(...)` | `_poop_set_from(x)` |
| `dict` | `ast.Dict` (no unpacking) | `_poop_dict_from_pairs(k1, v1, k2, v2, …)` |
| `dict` | `ast.Call` with `dict(...)` | `_poop_dict_from(x)` — `x` must be `Dict` or iterable of 2-element `Tuple`/`List` pairs |
| `dict` | `ast.Dict` with `**x` | `_poop_dict_merge(…)` — each run of pairs a `_poop_dict_from_pairs`, each `**x` itself |
| `complex` | `ast.Constant(value=complex)` | `_poop_complex(v)` |
| `complex` | `ast.BinOp` combining real + imaginary literal | collapsed into `_poop_complex(r+ij)` |
| `complex` | `ast.Call` with `complex(r, i)` | `_poop_complex_from(r, i)` |
| `bytearray` | `ast.Call` with `bytearray(...)` | `_poop_bytearray_from(x)` |
| `memoryview` | `ast.Call` with `memoryview(...)` | `_poop_memoryview_from(x)` |
| `frozenset` | `ast.Call` with `frozenset(...)` | `_poop_frozenset_from(x)` |
| `frozendict` | `ast.Call` with `frozendict(...)` | `_poop_frozendict_from(x)` |
| `frozendict` | `ast.Call` with `frozendict(a, **b)` | `_poop_frozendict_from(_poop_dict_merge(...))` — the dict's fold, frozen |
| `sentinel` | `ast.Call` with `sentinel(name, repr=...)` | `_poop_sentinel_from(name, repr=...)` |
| `sentinel` | `ast.Name` `sentinel` | `_poop_sentinel_cls` — the alias, for `x.is_instance(sentinel)` and `class Marker(sentinel)` |
| `range` | `ast.Call` with `range(stop)` / `range(start, stop)` / `range(start, stop, step)` | `_poop_range(...)` → `Range` |
| `zip` | `ast.Call` with `zip(a, b, ...)` | `_poop_zip(...)`, a lazy `Zip` |
| `enumerate` | `ast.Call` with `enumerate(col)` / `enumerate(col, start)` | `_poop_enumerate(...)`, a lazy `Enumerate` |

### Classes

| Pattern | Replacement |
|---|---|
| `class Foo:` | `class Foo(_poop_object):` |
| `class Foo(object):` | `class Foo(_poop_object):` |
| `class Foo(Object):` | `class Foo(_poop_object):` — backwards-compat for explicit Smalltalk-style declarations |
| `class Foo(Bar):` | unchanged — already has a base |
