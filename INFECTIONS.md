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
- **Activate validator only when the substitute exists**: blocking without offering an alternative only breaks code without teaching anything. Validators without an implemented substitute live in `proposals.md` until the alternative is ready. *Exception*: **definitive bans** — constructs with no possible substitute inside POOP's model (`exec`/`eval`/`compile`, `exit`/`quit`, `breakpoint`, `globals`/`locals`/`vars`, `open`, `async def`/`await`) are activated without a substitute. Each is documented under its own validator below; the ban is the design decision, not a deferred item.
- **Representation**: all POOP types implement `__str__` (and `__repr__` delegates to it). `Object.print` calls `str(obj)` internally — every printed message goes through the type's own representation.
- **`__slots__` on all POOP types**: instance variables are declared in the class definition and fixed — never added dynamically to instances. Runtime *method* extension continues to work normally. Subclasses that need new instance variables can declare their own `__slots__` or omit them. **The shared mixins declare `__slots__ = ()` too, and that is what makes the rest true**: one slot-less class anywhere in an MRO restores the per-instance `__dict__` for everything below it, and `_ValueEqMixin`, `_IterableMixin` and `_SetAlgebraMixin` had none — so the declaration was defeated on 36 of the 49 POOP classes. `"abc".set_attr("x", 1)` succeeded (two equal `Str`s carrying different attributes) while `(5).set_attr("x", 1)` refused, one message meaning two things on two rungs of the same tower. Closing it dropped a `Str` from 56 to 40 bytes — the same as an `Int` — and 100 000 of them from 14.2 MB to 9.4 MB. An empty `__slots__` on a mixin cannot collide with a concrete class's own, which is what makes it safe across all 36; `tests/test_slots.py` sweeps the whole MRO of every class, because the descriptor is installed on the first slot-less base and a per-mixin assertion would say nothing about the next mixin. `Object.set_attr` catches the refusal that follows and answers `str is a value — it holds no state of its own; only an object of a class you defined can be given one`, where CPython named `__dict__`, a dunder `no_dunder_attribute` bans and `_reject_dunder` will not let a program spell. User classes are unaffected: `ClassTransformer` builds them without `__slots__`, so `self.count = 1` and `set_attr` keep working there.
- **Every literal is transformed**: every literal in Python source (`1`, `3.14`, `"hello"`, `True`, `False`, `None`, `...`, `[1, 2]`, `(1, 2)`, `{1, 2}`, `{k: v}`, `b"..."`, `1+2j`) is rewritten by a Transformer into its POOP equivalent before execution — no naked Python primitive ever reaches runtime.
- **Every basic type has a POOP equivalent**: `int` → `Int`, `float` → `Float`, `str` → `Str`, `bool` → `Boolean`, `NoneType` → `NoneClass`, `ellipsis` → `EllipsisClass`, `list` → `List`, `tuple` → `Tuple`, `set` → `Set`, `frozenset` → `FrozenSet`, `dict` → `Dict`, `bytes` → `Bytes`, `bytearray` → `ByteArray`, `memoryview` → `MemoryView`, `complex` → `Complex`. Python native types must not leak into POOP code.
- **All POOP methods return POOP types**: every method on every POOP type must return a POOP object — never a raw Python `int`, `bool`, `str`, `list`, etc. Returning a native type is a bug. *Exception*: Python protocol dunders (`__bool__`, `__hash__`, `__len__`, `__str__`, `__int__`, `__float__`, `__contains__`, `__repr__`) must return native types because Python itself requires it for `if`, `dict`, `len()`, `str()`, etc. to work. The rule applies to all explicitly named POOP methods (`len()`, `hash()`, `not_()`, `includes()`, `tobytes()`, etc.).
- **Mutators named after Python void-returning methods return `none`**: methods that mirror Python counterparts returning `None` (e.g., `list.append`, `set.add`, `dict.update`, `bytearray.reverse`) must return POOP `none`, not `self`. This preserves the Python mirror contract — `result = lst.append(x)` leaves `result` as `none`, matching what a Python programmer expects. POOP-specific methods with no Python equivalent (e.g., `Dict.at_put`, `ByteArray.at_put`) may still return `self` for chaining.
- **`True`, `False`, and `None` are singletons**: `true`, `false`, and `none` are unique objects — there is exactly one instance of each. All comparisons and identity checks rely on this guarantee.
- **Constructor builtins are intercepted, not banned**: `int()`, `float()`, `bool()`, `str()`, `bytes()`, `list()`, `tuple()`, `set()`, `dict()` etc. are class constructors — they ARE object instantiation and fit the OO model. Each transformer intercepts the bare call and rewrites it to return the POOP type via a `_poop_X_from(...)` factory.
- **Dunders exposed as regular methods**: every relevant dunder on a POOP type gets an alias with the Python name without underscores — `__len__` → `len()`, `__abs__` → `abs()`, `__hash__` → `hash()`, etc. Do not translate to Smalltalk names.
- **Namespace hygiene — POOP types pass as Python builtins**: every wrapper class (`Int`, `List`, …) is bound under a mangled `_poop_*` name and unreachable from user code (enforced by `no_poop_prefix`). The bare Python builtin (`int`, `list`, `object`, …) is rewritten at parse time to the corresponding mangled name. The root is the one exception user code can name directly, under **both** `object` and `Object`: `ObjectTransformer` rewrites either to `_poop_object` in any position, so `class Foo(Object)` reads naturally without the raw wrapper ever being exposed — the binding stays `_poop_object`, the names are only source spellings. Each wrapper additionally patches `__module__ = "builtins"`, `__name__ = "<lowercase>"` and `__qualname__` to match, so `repr(Int)` reads `<class 'int'>` and `Int(5).class_name()` returns `Str("int")` — POOP builtins answer to the same names Python builtins do. All three go through `cloak(cls, name)` (`poop/types/_cloak.py`), which is what makes patching one and forgetting the others unrepresentable: `__qualname__` was the one left out, and CPython prefers it in several of its own messages — Python 3.14's unhashable-key error put both spellings in a single sentence (`cannot use 'List' as a dict key (unhashable type: 'list')`). `tests/test_cloak.py` sweeps every POOP class rather than asserting per wrapper, since the leak reached all of them at once. The cloak reaches one frame further in: CPython builds a *call-signature* error from the **function's** `__qualname__`, frozen when the class body ran, so `"abc".upper(1)` blamed `Str.upper()` and `[1, 2].map()` blamed `_IterableMixin.map()` — a private name `_reject_private` exists to keep out of user code. `cloak` renames the functions a class owns; the shared mixins (`_IterableMixin`, `_PeekMixin`, `_ValueEqMixin`, `_NumericCompareMixin`, `_DictView`, `_DictItemIteratorBase`) and `Error` are cloaked as `object`, the root's own spelling, because no single builtin name is true for every wrapper that inherits them. Its twin `cloak_callable(fn, name)` covers the rewriter helpers, applied centrally in `_merge_bindings` (`poop/transformers/__init__.py`) so a new transformer cannot forget it: the mangled key stays, but `range(1, 2, 3, 4)` blames `range()` instead of `_poop_range()` — a spelling `no_poop_prefix` would refuse if the reader typed it back — and the factory-built collection helpers no longer answer `make_iterable_from.<locals>._from()`. A message that names a type composes it the same way, from `type(x).__qualname__` and `poop_type.__name__` — never from a hand-written `"ByteArray"`, which spelt half the sentence in POOP's vocabulary and half in the wrapper's. The same cloak reaches the non-builtin wrappers: `Block` answers `function` (its lambda's Python class), `Try` and `With` keep their names but drop the module path, and `Error` answers the exception it wraps (`e.class_name()` → `IndexError`, via a `class_()` that delegates to `kind()`) — so no wrapper leaks a `poop.types.*` path or an internal name through `class_()`/`class_name()`. True entry points without an AST rewrite or method equivalent are down to two — `Try` and `With` — and both keep PascalCase, being classes. No lowercase name is injected any more: those were module entry points, and POOP mirrors no modules.

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
| `ast.AsyncFor` | Async variant; async has no substitute in POOP (see `no_async`) |

### No free functions — `poop/validators/no_free_functions.py`

| AST node | Context | Reason |
|---|---|---|
| `ast.FunctionDef` | direct parent is not a `ClassDef` | Free function is not a message to any object |
| `ast.AsyncFunctionDef` | direct parent is not a `ClassDef` | Async variant |

A function is a method only when it is a **direct** statement of a class body. Counting class *nesting* was not enough: a `def` nested inside a method sits at `class_depth > 0` yet its parent is the method, not the class, so it slipped through as a receiver-less named local function. Smalltalk has blocks, not named local functions — so the validator registers each `ClassDef`'s direct-body `def`s as methods and rejects every other `FunctionDef`/`AsyncFunctionDef`, module level and method-nested alike. Use a **lambda** for a local block: it is the sanctioned receiver-less callable, invoked as `block()`.

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
| `ast.AsyncWith` | Async variant; async has no substitute in POOP (see `no_async`) | — |

### No `and`/`or` — `poop/validators/no_and_or.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.BoolOp` with `ast.And` | `x and y` looks like an operator | `x.and_(lambda: y)` |
| `ast.BoolOp` with `ast.Or` | `x or y` looks like an operator | `x.or_(lambda: y)` |

`and_` and `or_` receive a block so evaluation is lazy — the right-hand side is only evaluated if needed, preserving the short-circuit semantics of Python's `and`/`or`.

**A tuple of affixes is the substitute for `s.startswith("a") or s.startswith("b")`**, and it exists on all three receivers that have the message. CPython accepts one, and with `or` banned there is no other way to ask the question — but only `Str` mapped a POOP `Tuple` to a Python one, so `b"ab".startswith((b"a", b"z"))` answered `startswith first arg must be bytes or a tuple of bytes, not tuple`: self-contradicting from where the reader stands, since they *did* pass a tuple and CPython was describing its own. `affix_needle` (`poop/types/_affix.py`) is shared by `Str`, `Bytes` and `ByteArray`, since only the scalar branch was ever string-specific. Members unwrap through `_faithful`, so a wrong-typed member reaches CPython and raises the faithful error rather than being silently coerced.

**Chained comparisons are the one deliberate exception.** `no_and_or` inspects only `ast.BoolOp`, so a chain like `1 < 2 < 3` — a single `ast.Compare` node with multiple comparators that Python evaluates as `(1 < 2) and (2 < 3)` with short-circuit — slips through with no `and` token. This is tolerated, not overlooked: a single comparison keeps its operator (like `+`), and a chain is read as plain operator sugar rather than a hidden `BoolOp`. So chained comparison is the single place an implicit `and` survives in POOP. To spell one out explicitly instead, decompose it: `(a < b).and_(lambda: b < c)`. The question has now been raised twice and settled the same way both times — the ban would reject code no example relies on, to remove sugar POOP keeps everywhere else it spells an operator.

### No `async` — `poop/validators/no_async.py`

| AST node | Reason |
|---|---|
| `ast.AsyncFunctionDef` | POOP has no way to drive a coroutine |
| `ast.Await` | Same |

A **definitive ban**: async has no substitute inside POOP's model, so it
is activated without one, like `exec` / `breakpoint` / `open`.

Dropping the stdlib mirrors took `asyncio` with them, and `asyncio.run`
was the only thing that could ever start a coroutine. That left `async
def` as valid syntax nothing could execute — a promise the language
could not keep. The ban makes the refusal explicit and immediate rather
than letting a program define coroutines that silently never run.

Two rows are enough for the whole surface, but not for the reason one
might guess. `await` needs its own row because `ast.parse` **accepts** a
module-level `await` — only `compile()` rejects it — so without the row
the node would reach compilation and surface as a raw CPython
`SyntaxError` instead of a POOP error. `async with` and `async for` are
equally parseable at module level, but they already belong to `no_with`
and `no_loops`; rows here would only double the message.

`no_async` runs ahead of those validators in `DEFAULT_VALIDATORS` so the
root cause wins: telling someone to rewrite an `async for` inside a
method that is itself about to be rejected sends them down a dead end.
Both messages still surface under `--validators-only`, which collects
every error rather than the first. Async generators are covered twice
over — `yield` in any function is already rejected by `no_yield`.

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

### No decorator — `poop/validators/no_decorator.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| a `decorator_list` entry on `ast.FunctionDef` / `ast.AsyncFunctionDef` / `ast.ClassDef` | not a bare `ast.Name` among `staticmethod`, `classmethod`, `property` | `@f` is a function call written as syntax rather than sent as a message | send the message |

The three allowed decorators are argued for under *Explicitly allowed*; this validator is what makes that boundary real rather than merely documented. `@twice` on a method silently replaced it with an unrelated block and nothing objected. `@property(...)`, `@a.b` and `@twice` are all refused; `@property` is not.

This validator owns the `@` position only. `no_class_machinery`, immediately below, owns every other one — the three were still reachable as plain names, where they answered Python.

### No class machinery outside its position — `poop/validators/no_class_machinery.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Name` `staticmethod` / `classmethod` / `property` | not a `decorator_list` entry | class-definition machinery is not an object | use it as a decorator |
| `ast.Name` `super` | not the callee of an `ast.Call` | the allowance is the call, not the name | `super().method(...)` |

`_ALLOWED_BUILTINS` admits six names. Two are dunders — `__build_class__` and `__name__` — and `no_dunder_name` already refuses them as a bare `ast.Name`. The other four had no guard outside the positions they were argued for, and answered Python rather than POOP:

    property.print()   ->  AttributeError: type object 'property' has no attribute 'print'
    super.print()      ->  AttributeError: type object 'super' has no attribute 'print'

which is the naked-native symptom the allow-list was introduced to end, reproduced word for word — see *Builtins allow-list* below, whose own argument this completes. The scope is not new: *Explicitly allowed* already reads "Only a bare `ast.Name` among the three is accepted: `@property(...)` is refused even though `@property` is not, because a called decorator is a runtime operation, which is the distinction the allowance rests on." `no_decorator` made that real for `@`; nothing made it real anywhere else, so `p = property` and `property(getter)` both passed.

`property(getter)` is refused here for the reason `@property(...)` is refused there — one distinction, applied in both positions. `super` keeps the call position instead, because a call is exactly what its allowance is for.

### No `type` alias — `poop/validators/no_type_alias.py`

| Construct | Reason |
|---|---|
| `type X = int` | Creates an alias for a Python builtin type — incompatible with POOP runtime types |

### No `match/case` — `poop/validators/no_match.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Match` | control structure with procedural look | polymorphism + `if_true(block)`/`if_false(block)` |

### No f-strings or t-strings — `poop/validators/no_fstring.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.JoinedStr` | `{...}` interpolation hides message sends and bypasses POOP `Str` | concatenation: `("Hello, " + name)`, `("count: " + str(n))` |
| `ast.TemplateStr` | Python 3.14 t-strings share the `{...}` interpolation and yield a raw `Template`, bypassing POOP `Str` | concatenation: `("Hello, " + name)`, `("count: " + str(n))` |

`"{}".format(...)` stays as POOP's template surface — but a format *field* may not reach an attribute or an item. `str.format` resolves `{0.__class__}` and `{0[0]}` at runtime, from inside a string literal no validator can read, so `"{0.__class__}".format(5)` printed `<class 'int'>` — reopening what `no_dunder_attribute` closes, and `{0[0]}` what `no_subscript` closes, against the *raw* Python value at that (`Str.format` deep-unwraps its arguments through `to_python`). `Str._reject_field_access` refuses both spellings, recursing into nested specs (`"{0:{1.__class__}}"` resolves its spec by formatting too). Only the field name is inspected, so `{:.2f}`, `{!r}`, `{name}` and `{:{width}}` are untouched. It is the third half of the dunder ban, next to `Object._reject_dunder`: both guard a spelling that reaches the runtime as data.

**`format` is the only template surface, and printf `%` is gone.** `Str.__mod__` implemented printf-style formatting in full, which broke the same rule twice. It duplicated `format` with a second template language whose directives (`%d`, `%r`, `%-5.2f`) are Python conventions a POOP program has no other reason to learn — and no forbidden construct to substitute, which is what a method needs to earn its place. Worse, `"%(k)s" % mapping` is a **key lookup written as syntax**, exactly what `no_subscript` bans and what `_reject_field_access` rejects two paragraphs up: the same operation was refused through `format` and granted through `%`. `"%s" % (a,)` now answers `str does not understand #% with a tuple`, which is the honest reply.

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
| `id(x)` | free function with procedural look, and an address POOP has no business handing out | `a.is_identical(b)` |

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
| `min(a, b)` | free function with procedural look | `a.min(b)` (on `Int`/`Float`) |
| `min(a, b, c, ...)` | free function with procedural look | `a.min(b, c, ...)` (variadic, on `Int`/`Float`) |
| `min(a, b, key=fn)` | free function with procedural look | `a.min(b, key=fn)` (keyword-only, on `Int`/`Float`) |
| `min(iterable)` | free function with procedural look | `iterable.min()` |
| `min(iterable, key=fn)` | free function with procedural look | `iterable.min(key=fn)` |
| `min(iterable, default=x)` | free function with procedural look | `iterable.min(default=x)` |

`max` mirrors `min` exactly. The iterable form lives on
`_IterableMixin` (covers `List`, `Tuple`, `Set`, `FrozenSet`,
`Range`, `Bytes`, `ByteArray`, `MemoryView`, `Enumerate`, `Zip`)
plus direct implementations on `Str` (smallest/largest character)
and `Dict` (smallest/largest key). Empty iterable without `default`
raises `ValueError`, mirroring Python — worded as `#min of an empty
collection is undefined — send it a default instead`, where CPython
said `min() iterable argument is empty`: the free function this
message substitutes, spelled as a call the program never wrote. The
refusal is driven by passing `_MISSING` *as* the default and testing
the answer's identity, not by catching CPython's `ValueError` — the
same `except` would have caught a `ValueError` out of the user's own
`key` block and reported it as an emptiness it says nothing about.

**`key` and `default` are keyword-only everywhere, and that is not a style choice.**
The variadic form took operands only, so `(5).max(3, block)` compared the block
*as a value* instead of applying it — a block is not comparable, so this
happened to fail, but any comparable third argument would have answered a
plausible wrong number in silence. CPython spells it `max(a, b, key=fn)`, and
keyword-only is the only spelling that cannot be confused with one more operand.
`default` stays refused on the scalar form, as CPython refuses it too ("Cannot
specify a default for max() with multiple positional arguments"). The collection
rungs spell both `key` and `default` keyword-only for the same reason — CPython's
own signature is `min(iterable, *, key, default)`, and `xs.min(0)`, the plain
reading of "the smallest, or 0 if empty" (and the shape `get`/`pop` do take
positionally), handed `0` to the key slot: `[1, 2].min(0)` answered `'int' object
is not callable` and `[[3], [1]].min([9])` answered a plausible wrong list without
raising at all. The shared
body now lives in `poop/types/_minmax.py` rather than `_iterable_mixin`: the
mixin imports `Int`, so the scalar rungs could not have reached the helper
there.

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

**The strict mismatch is worded by POOP, which is why `Zip` drives the sources itself when `strict` is asked for.** CPython answers `zip() argument 2 is shorter than argument 1`: the builtin spelled as the call `a.zip(b)` substitutes, with arguments numbered from that call's perspective — argument 2 is the *first* one the program passed, since the receiver is argument 1. `Zip._gen` pairs the sources by hand in the strict case and answers `zip is strict: collection 2 ran out while collection 1 still had elements` (and, the other way round, `collection 2 still had elements when collection 1 ran out`). The position counts collections rather than call arguments, so the same number is true of both spellings, `a.zip(b)` and `zip(a, b)`. The non-strict path still runs CPython's `zip`, which cannot fail.

### `enumerate` → `Enumerate` — `poop/transformers/enumerate.py`

`enumerate(col)` and `enumerate(col, start)` are rewritten by `EnumerateTransformer` to `_poop_enumerate(col)` / `_poop_enumerate(col, start)`, which returns an `Enumerate` object.

`Enumerate` (`poop/types/enumerate.py`) is a lazy iterable POOP type. It wraps any iterable (including `Dict`) and yields `Tuple(Int(index), item)` pairs on demand, raising `TypeError` eagerly on construction if the source is not iterable. It inherits `do`, `map`, `filter`, `filter_false`, `find`, `sum`, `all`, `any` from `_IterableMixin`. Every collection type exposes `.enumerate(start=Int(0)) -> Enumerate` as a convenience method. `Dict.enumerate()` iterates over keys, consistent with Python's `enumerate(dict)`.

### No `iter`/`next` — `poop/validators/no_iter.py`

| Call | Reason | Substitute |
|---|---|---|
| `iter(col)` | iterator protocol with procedural look | `col.iter()` |
| `next(it)` | same | `it.next()` |
| `next(it, default)` | same | `it.next(default)` |
| `aiter(col)` | async variant | `col.iter()` |
| `anext(it)` | async variant | `it.next()` |

Every collection exposes `.iter()` returning a specialized one-shot iterator that mirrors Python's iterator types (`list_iterator`, `tuple_iterator`, `set_iterator` (shared by `set` and `frozenset`, as in CPython), `dict_keyiterator`, `str_iterator`, `range_iterator`, `bytes_iterator`, `bytearray_iterator`, `memory_iterator`). All inherit from `_IteratorBase` (`poop/types/_iterator_base.py`), which adds `.next()` and raises `StopIteration` on exhaustion — catchable via `Try(lambda: it.next()).except_(StopIteration, handler).run()`. It carries a sentence: `list_iterator is exhausted — send #next with a default, or ask #has_next`. The native one carries no message at all, so `_describe` degraded to the bare class name — a word naming the CPython protocol that drives `for`, the loop POOP forbids, with nothing to say what went wrong. **Every lazy view answers `has_next`** (`poop/types/_peek.py`), so the cursor protocol `examples/patterns/iterator.py` teaches works on POOP's own iterators and exhaustion is testable without an exception: `(lambda: it.has_next()).while_true(lambda: it.next().print())`. The cost was chosen rather than discovered — a one-shot Python iterator cannot be peeked, so `has_next` buffers one element, and for `Map`/`Filter` that pulls the user's block one step ahead of where it runs. The buffer is filled *only* by `has_next`: a program that never asks is unaffected, one that does opted into the lookahead. The alternative — `has_next` only where it is structurally cheap (`ListIterator`, `RangeIterator`, `StrIterator`) — leaves a protocol half the iterators answer, which is the opposite of having one. Every iteration path routes through the buffer, or a peeked element would be skipped by the `do`/`map` that came after the ask.

`Map` and `Filter` are Python generators, so a `StopIteration` raised by the user's block used to hit PEP 479 and surface as `generator raised StopIteration` — a report about a construct POOP does not have and `no_yield` bans, read by someone who never wrote one. It is caught inside the generator now and answers `a block ran off the end of an iterator — ask #has_next before #next`. What PEP 479 protects against stays protected: letting the `StopIteration` through would end the view early and answer a quietly truncated collection. `.next(default)` mirrors Python's two-arg `next(it, default)`: it answers `default` instead of raising once the iterator is exhausted. Because an iterator *is* an iterable, `_IteratorBase` also inherits `_IterableMixin`, so every iterator answers the same protocol as collections and views — `do`, `map`, `filter`, `filter_false`, `find`, `reduce`, `sum`, `min`, `max`, `all`, `any`, `enumerate`, `zip`. This mirrors Python, where an iterator is a valid argument to `filter`/`map`/`enumerate`/... The consuming messages (`find`, `reduce`, `min`, …) drain the one-shot iterator, exactly as they would in Python; the lazy ones (`map`, `filter`, `enumerate`, `zip`) return a fresh view over the not-yet-consumed remainder.

`Enumerate` and `Zip` are their own iterators (`x.iter() is x`, mirroring Python's `iter(zip(...)) is zip(...)`), and that makes them **one-shot in every direction**: `.next()`, `.do()`, `.map()` and the rest all draw from the same lazy internal generator, so a second `.do()` over the same view answers nothing. This is what Python does — `list(z)` twice on one `zip` gives the pairs and then `[]` — and what a `for` over one sees. `__iter__` answers `self` rather than a fresh generator, so an element parked by `has_next` is not skipped by whatever iterates next.

`Dict.iter()` returns `DictKeyIterator`, mirroring `iter(dict)` in Python. `Dict.values().iter()` returns `DictValueIterator`; `Dict.items().iter()` returns `DictItemIterator`. Each view also exposes `.reversed()` returning the matching reverse iterator (`DictReverseKeyIterator`, `DictReverseValueIterator`, `DictReverseItemIterator`).

### Dict views — `poop/types/dict_keys.py`, `poop/types/dict_values.py`, `poop/types/dict_items.py`

`Dict.keys()`, `Dict.values()`, and `Dict.items()` return **live view** objects mirroring Python's `dict_keys`, `dict_values`, and `dict_items` exactly. They reflect mutations to the underlying dict.

| View | iter | set ops | comparison | mapping |
|---|---|---|---|---|
| `DictKeys` | `DictKeyIterator` | `\|`, `&`, `-`, `^` → `Set`; `isdisjoint` | `__eq__`, `__le__`, `__lt__`, `__ge__`, `__gt__` (set semantics) | `mapping()` → `MappingProxy` |
| `DictValues` | `DictValueIterator` | none (values may be unhashable) | inherits `Object` identity (Python parity) | `mapping()` |
| `DictItems` | `DictItemIterator` (yields `Tuple(k, v)`) | `\|`, `&`, `-`, `^` → `Set` of `Tuple`; `isdisjoint` | full set semantics like `DictKeys` | `mapping()` |

**The set operators take any iterable; the comparisons do not.** CPython's set-like views accept any iterable for `|`, `&`, `-`, `^` and for `isdisjoint` (`{"a": 1}.keys() | ["a", "c"]` is valid) but require a set-like on the right of `<= < >= >` (`dict_keys <= list` is a `TypeError`). POOP keeps both halves through `_elements` / `_set_like_elements` in `_dict_view.py`: the algebraic half only *iterates* the operand, so a non-iterable one answers CPython's `'int' object is not iterable`, and the comparison half answers `NotImplemented` for anything but the two set-like views and `Set`/`FrozenSet`. Neither reads `other._data` — the older code did, so `{"a": 1}.keys() | [2]` answered `list does not understand #_data` and rejected a valid program at the same time. `_set_like_elements` deliberately does *not* reuse `_SetAlgebraMixin`'s `_set_like` marker: claiming a view there would make `frozenset({1}) | {2: 3}.keys()` answer a frozenset, where CPython answers a set through the view's reflected operator.

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

`obj.dir()` (and the class-side `Klass.dir()`) filters every `_`-prefixed name — dunders and privates, including the mangled `_poop_*` bindings — so the substitute never surfaces what the encapsulation rules hide, matching the REPL's `:methods`. CPython's `dir()` is exhaustive; POOP's is deliberately not.

**One predicate, in one place: `is_message` (`poop/types/_selectors.py`).** Four surfaces ask "may user code send this name?" — `dir()`, `:methods`, the near-miss hint, and the REPL's tab-completion — and three carried their own copy of the rule. The fourth, `_PoopCompleter._attr_matches`, spelt it `not name.startswith("__")`, so pressing Tab on `x._` offered `x._value` (the raw Python `str` behind the wrapper, exactly what `_reject_private` exists to keep out of user code) along with `_abc_impl` and `_eq_group`, POOP internals with no meaning in the language at all. The completer was *teaching* the spelling plain attribute access still reaches. `_name_matches` filtered `_poop_`-prefixed keys only, and now filters every `_` name. The same fix stopped the completer from reading candidate attributes off the *instance*: `getattr(obj, name)` runs a `property` getter, so pressing Tab could execute program code — it reads them off the type instead, which answers the "is it callable" question without invoking a descriptor.

### No dunder attributes — `poop/validators/no_dunder_attribute.py`

Any `__dunder__` in `ast.Attribute` position is rejected, `__init__` excepted. `vars(obj)` is banned but `obj.__dict__` *is* `vars(obj)`, and the attribute spelling reached a raw CPython `dict` at runtime; `x.__class__`, `A.__mro__` and `A.__bases__` reconstruct the `type(x)` that `no_type` bans; `x.__class__.__name__` answers a raw `str`.

| Attribute | Substitute |
|---|---|
| `.__dict__` | none — the ban is the decision, as `no_introspection` already argues for `vars` |
| `.__class__` | `obj.class_()` |
| `.__name__` | `Klass.name()` |
| `.__mro__` / `.__bases__` | `Klass.superclass()` |
| `.__len__()` | `obj.len()` |
| `.__contains__(x)` | `col.includes(x)` |
| `.__abs__()` | `n.abs()` |
| `.__hash__()` | `obj.hash()` |
| anything else dunder-shaped | none — it is Python's protocol, not POOP's message surface |

**A rule, not a list.** The obvious four (`__dict__`, `__class__`, `__mro__`, `__bases__`) were already incomplete before the ban was written: nobody had listed `__name__`. Enumerating invites the next omission.

**`__mro__` had an undotted twin.** `PoopMeta` derives from `ABCMeta`, and inherited two *public* names with it: `type.mro` and `ABCMeta.register`. `Foo.mro()` answered the same raw list `.__mro__` does — holding the Python `object` that `superclass` stops short of on purpose — under a spelling no validator reading `ast.Attribute` can see, and `dir()` never listed either name (`type.__dir__` does not merge the metaclass's), so both were unreachable by reading and reachable by typing. `Foo.register(Bar)` was worse than a leak: it made `is_instance` answer true for a class that never inherited from the receiver, moving "is a" into a side table no reader of the class can see. Both are now `class_side` refusals naming `superclass` and `is_subclass`. `mro` cannot refuse unconditionally — CPython calls the metaclass's `mro` to *compute* a new class's MRO, so an outright ban breaks every `class` statement — and the class has no `__mro__` during that call, which is the line the guard draws between the interpreter asking and a program asking.

**Raw dunder calls are in, and not on taste.** CPython *forces* `__len__` to answer a real `int` and coerces `__contains__` to a real `bool`, so those two can never honour "no naked Python primitive ever reaches runtime". `__abs__` already answers a POOP `Int` and is banned anyway: sparing it would restore the exception list the rule exists to avoid, and `.abs()` costs nothing.

**`__init__` is carved out — for the syntax, and only there.** `super().__init__(...)` is an `ast.Attribute` with a dunder attr, and `super` is explicitly allowed: without it inheritance breaks entirely and there is no message-passing substitute. The runtime guard below opts out (`dunder_message(name, allow_init=False)`), because `get_attr` is dotted-*shaped* but is not that syntax. Riding on the same flag, it inherited the exemption and handed back a callable constructor: `s.get_attr("__init__")("ZAP")` re-initialized a live `Str` in place, so every immutable wrapper was mutable — `Int`, `Str` and `Tuple` alike — and a `Dict` or `Set` keyed on one was left holding an entry reachable under neither the old spelling nor the new. `get_attr("__init__")` now answers `__init__ is forbidden — use Klass(...) instead`.

**Half the ban is a runtime guard**, in `Object._reject_dunder`. `no_getattr` bans `getattr` and offers `get_attr` / `has_attr` / `set_attr` / `del_attr` as the substitute, so `get_attr("__dict__")` reopened exactly what the validator closes — and `get_attr("__dict" + "__")` puts that spelling beyond any static validator's reach. Both halves read the same `dunder_message`, so they cannot drift. `get_attr(name, default)` is guarded before the default is consulted: a forbidden name is refused, not quietly answered with a fallback.

**The name itself must be a `Str`.** All four accessors take it through `_attr_name` (`poop/types/_unwrap.py`) before either guard runs: reading `name._value` answered `list does not understand #_value` for `get_attr([1])` — a POOP internal leaking out of the substitute the `getattr` ban points at, on every object in the language. It now answers CPython's own `attribute name must be string, not 'list'`. `Object.assert_` had the same shape and takes the plain faithful unwrap, which also lets a non-`Str` assertion message through, as `assert x, msg` does in Python.

A sibling guard, `Object._reject_private`, refuses every `_`-prefixed non-dunder name for the same reason one underscore up: `get_attr("_value")` would hand back the raw Python primitive a wrapper holds, and `_items` / `_data` / `_fn` expose the same internals. All four accessors call both guards, and the class side (`PoopMeta`) mirrors them — including `has_attr`, which once skipped the guard entirely.

**An index is not unwrapped by hand: `Int` and `Boolean` answer `__index__`.** `at` / `slice` / `insert` / `pop` / `Slice.indices` used to read `index._value`, which leaked (`[1, 2].at([0])` answered `list does not understand #_value`) *and* refused a Boolean index, though `bool` is an `int` subclass in CPython — `[10, 20][True]` is 20 and `"ab"[True]` is `"b"`. With the protocol answered, the call sites hand the wrapper straight to CPython: `self._items[index]` resolves an `Int`/`Boolean` and raises `list indices must be integers or slices, not list` for anything else. `__index__` joins `__len__`/`__bool__` as a protocol dunder that must answer a native, and `Index` (`poop/types/_index.py`) is the alias every such signature names, since POOP's `Boolean` is not an `Int` subclass. A `Range` normalizes its components to `Int` (CPython's `range(True, 5).start` is `1`); a `Slice` keeps what it was given (CPython's `slice(True, 3).start` is `True`).

**A `Range` stores an inclusive upper bound, and answers an exclusive one.** `_poop_range` subtracts one from the Python-spelled stop and `_range()` adds it back, which is an encoding, not a language feature — `__eq__` compares materialized ranges for exactly that reason. `stop()` and `__str__` used to read the slot instead, so `range(3).stop()` answered `2` and `range(3)` printed as `range(0, 2)` — a spelling that, read back as POOP source, is a *different* sequence. Both now report through `_range()`, which is the one place the encoding is undone: `range(3).stop()` is `3` and `range(0, 4, 2)` prints as itself, as CPython does. `start()` and `step()` are answered from the slots, since neither is re-encoded. `Slice`, handed its bound rather than encoding one, always answered the exclusive form — the two had disagreed about what a single selector means.

**The same `_value` name must not leak the other way, through a method's own body.** A method that unwraps a *mandatory* argument inline as `arg._value` blows up when handed a POOP value that carries no `_value` — a `List` / `Set` / `Dict` / `Tuple` passed where a `Str` / `Bytes` / `Int` was expected. `arg._value` then routes through `does_not_understand` and answers `list does not understand #_value`, exposing the internal slot name. The fix is the **faithful-unwrap idiom**, `_faithful(arg)` in `poop/types/_unwrap.py` (a thin `getattr(arg, "_value", arg)` returning `Any`): a `_value`-bearing argument unwraps as before; a foreign one reaches the underlying Python call raw, so Python raises its own `TypeError` (`count() argument 1 must be str, not list`) instead. Its optional-argument twin `_unwrap(arg, default)` does the same after the absent-check. Both are used across `Str` / `Bytes` / `ByteArray` / `Range` / `Int` / `Float`; `Int` / `Float` / `Complex` arithmetic already routed foreign operands to `NotImplemented` (via `_num_value` / `_integral_value` / `_coerce`), so they never leaked. `MessageNotUnderstood` subclassing `AttributeError` is what makes the three-argument `getattr` fall back cleanly here.

The same two shapes closed the sites that had been missed. **Operators** guard and answer `NotImplemented`: `Str.__add__`, `Bytes.__add__` and `ByteArray.__add__` used to read `other._value`, so `("a" + [1])` answered `list does not understand #_value` (the byte-like guards admit either wrapper, since CPython concatenates `bytes + bytearray` both ways). **Methods** route the operand through the faithful path: `startswith` / `endswith` on all three of `Str`, `Bytes` and `ByteArray` share `affix_needle` (`poop/types/_affix.py`), whose fall-through hands a non-`Tuple` affix to CPython raw instead of reading `._items` off it, and `Int.min` / `Int.max` / `Float.min` / `Float.max` delegate to `builtins.min` / `max` over the operands themselves — which also fixed a correctness gap, since `bool` is an `int` subclass and `(1).min(True)` had leaked rather than answering 1.

### No dunder names — `poop/validators/no_dunder_name.py`

The `ast.Name` half of the same ban: any `__dunder__` spelled as a bare name, load or store.

| Name | Reason |
|---|---|
| `__builtins__` | the raw Python builtins **dict**, live and mutable — `__builtins__.clear()` used to run clean through every validator and corrupt the interpreter |
| `__loader__` / `__spec__` | `BuiltinImporter` / `ModuleSpec` — naked Python natives, and an import surface `no_import` bans |
| `__name__` / `__package__` / `__debug__` | raw Python `str` / `None` / `bool`, not POOP objects |
| anything else dunder-shaped | none — it is Python's protocol, not POOP's message surface |

**Why a validator on top of the allow-list.** `exec` injects `__builtins__` only when the globals dict lacks one, so the executor supplies its own (below) and `__builtins__` no longer names CPython's whole namespace. The validator stays because it is the half that *teaches*: the program is refused before it runs, naming the ban, rather than answering `dict does not understand #clear` at runtime.

**One message, two node types.** Both halves read `dunder_message`, which takes `dotted=False` here so a bare name is not reported as `.__builtins__` — an attribute the program never wrote. Named substitutes carry over (`__name__` → `Klass.name()`); the `__init__` carve-out does not, because `super().__init__(...)` is an attribute and a bare `__init__` Name has no such use.

### Builtins allow-list — `poop/executor.py`

Validators and transformers cover the names someone thought to enumerate; `exec` hands a program *everything else* in CPython's builtins namespace. `OSError`, `BaseException`, `KeyboardInterrupt`, `copyright`, `NotImplemented`, `open` — 55 of Python's 71 builtin exceptions among them — were naked natives one identifier away, answering `type object 'OSError' has no attribute 'print'` instead of `does not understand #print`. The allow-list left four of its own six admissions in exactly that state — see `no_class_machinery` above, which scopes each to the position it was argued for. That contradicted `poop/types/exceptions.py`, which mirrors 16 exceptions *on purpose*: "a language with no I/O and no codecs cannot reach the `OSError` subtree".

`exec` only injects `__builtins__` when the globals dict lacks one, so `execute` supplies an allow-list and everything outside it answers `NameError: name 'OSError' is not defined` — which is what "if Python needs an import to reach it, POOP does not offer it" means.

| Allowed | Why |
|---|---|
| `__build_class__` | what the `class` statement itself calls |
| `__name__` | read while creating a class |
| `super` | already the documented allowance — without it inheritance breaks entirely |
| `classmethod` / `staticmethod` / `property` | class-definition machinery with no message-passing substitute, by the same argument as `super`; `examples/patterns/` uses the first two |

It is `setdefault`, not assignment: the REPL reuses one namespace across inputs. This is a rule where the validators are a list — it closes the whole class of escapes, including the names nobody enumerated — so `no_dunder_name` and the builtin-call bans remain as the teaching half, refusing a program before it runs.

### No `type` — `poop/validators/no_type.py`

| Call | Reason | Substitute |
|---|---|---|
| `type(x)` | free function returning a raw class object that is not a POOP value; the three-arg form is a metaprogramming escape — type dispatch belongs in methods | `x.class_name()` or polymorphism |

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

### No `help` — `poop/validators/no_help.py`

| Call | Reason |
|---|---|
| `help(obj)` | interactive escape hatch (opens the Python pager) exposing wrapper internals — no POOP equivalent |

### No `input` — `poop/validators/no_input.py`

| Call | Reason | Substitute |
|---|---|---|
| `input(prompt)` | free function with procedural look | `prompt.input()` (`poop/types/string.py`) |

Symmetric to `Object.print()` — the receiver is what gets shown. Scoped to `Str` (not `Object`) since non-string receivers as prompts are meaningless. `EOFError` propagates raw, catchable via `Try(lambda: prompt.input()).except_(EOFError, handler).run()`.

### No `open` — `poop/validators/no_open.py`

| Call | Reason |
|---|---|
| `open(path, ...)` | POOP has no file I/O |

A **definitive ban**, and now a substitute-less one. It was always listed as definitive on the grounds that POOP has no file-object abstraction, but it used to point at `Path.read_text()` / `write_text()` for the common cases. Dropping the `pathlib` mirror took that recipe with it: POOP no longer touches the filesystem at all. A program's only channels are `"prompt".input()` and `Object.print()`.

### No `del` — `poop/validators/no_del.py`

| AST node | Reason |
|---|---|
| `ast.Delete` | objects have no explicit destruction — simply do not delete |

### No `import` — `poop/validators/no_import.py`

| AST node | Reason |
|---|---|
| `ast.Import` | POOP is the language, not the library — there is no stdlib surface to import, and an import would bind raw CPython values that answer to no POOP message |
| `ast.ImportFrom` | same — `from os import getcwd` would leak a raw Python callable returning a raw `str` |

The only names POOP injects (`Try`, `With`) are already in scope and need no import.

### No `_poop_*` prefix — `poop/validators/no_poop_prefix.py`

| AST node | Reason |
|---|---|
| `ast.Name` with `id` starting in `_poop_` | mangled identifier reserved for the runtime — rewriters target it, user code must not |
| `ast.Attribute` with `attr` starting in `_poop_` | same — keeps the runtime helpers reachable for the rewritten AST but invisible to handwritten code |

Every type wrapper (`Int`, `List`, `Object`, …) lives in `DEFAULT_NAMESPACE` under a `_poop_*` key (`_poop_int`, `_poop_list_cls`, `_poop_object`, …) so the rewritten AST resolves them at runtime. This validator stops user code from referencing the same names directly, preserving the abstraction that POOP types pass as their Python builtin counterparts.

### No namespace shadow — `poop/validators/no_namespace_shadow.py`

| AST node | Reason |
|---|---|
| `ast.Assign` with target `ast.Name` in the protected set | reassigning a namespace name (`Try = 42`) breaks every later call to `Try(…)` |
| `ast.AnnAssign` with target `ast.Name` in the protected set | annotated form (`Try: int = 42`) — same problem |
| `ast.AugAssign` with target `ast.Name` in the protected set | augmented form (`Try += 1`) — same problem |
| `ast.ClassDef` whose `name` is in the protected set | `class Try: …` binds `Try` at module level, shadows the namespace |
| Unpacking targets (`ast.Tuple` / `ast.List` / `ast.Starred`) holding a protected name | tuple unpacking (`Try, x = 1, 2`) still rebinds the name |
| `def`/`async def`/`lambda` parameters in the protected set | a parameter named after a binding (`def m(self, Try): …`, `lambda Try: …`) shadows it inside the body and fails confusingly |

The **protected set** is computed dynamically from `DEFAULT_NAMESPACE` (filtered to non-`_poop_*` entries) at validator instantiation time. Today that is exactly two names: `Try` and `With`. Any future entry point protects itself automatically — no changes to this validator.

What the validator **does not** catch: method names inside classes (`class Calc: def Try(self): …`), which bind as attributes, not in the namespace scope.

### No builtin shadow — `poop/validators/no_builtin_shadow.py`

Reuses the namespace-shadow `_Visitor` over a fixed set of the 17 lowercase builtin names the type transformers rewrite to mangled `_poop_*` globals: `bool`, `int`, `float`, `complex`, `str`, `bytes`, `bytearray`, `memoryview`, `list`, `tuple`, `dict`, `set`, `frozenset`, `range`, `slice`, `enumerate`, `zip`. Rebinding one (assignment, class name, or `def`/`lambda` parameter) would silently retarget the interpreter's internals — `str = "x"` replaces the literal constructor, `def m(self, dict)` makes the body operate on the internal `Dict` class — so the validator rejects it with `'<name>' is a POOP builtin name; it cannot be rebound`. Using the names as constructors (`int("5")`) is unaffected.

### No `sum` — `poop/validators/no_sum.py`

| Call | Reason | Substitute |
|---|---|---|
| `sum(col)` | free function with procedural look | `col.sum()` |
| `sum(col, start)` | free function with procedural look | `col.sum(start)` |

Available on every `_IterableMixin` type — `List`, `Tuple`, `Set`,
`FrozenSet`, `Range`, `Bytes`, `ByteArray`, `MemoryView`, `Enumerate`,
`Zip`, `Map`, `Filter`, and the three dict views.

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
list(items.map(lambda x: x + 1))  # -> List
tuple(items.filter(lambda x: x > 0))  # -> Tuple
set(items.map(lambda x: x.lower()))  # -> Set
bytes(items.map(lambda x: x.code()))  # -> Bytes
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
| `sorted(col, key=fn, reverse=True)` | free function with procedural look | `col.sorted(key=fn, reverse=True)` |
| `reversed(col)` | free function with procedural look | `col.reversed()` |

`sorted` lives on `List` and `Tuple`; both accept `key` and `reverse`, matching Python's `sorted` and `List.sort`.

**Every receiver answers `reversed` with its own kind.** `List` → `List`, `Tuple` → `Tuple`, `Range` → `Range`, the dict views → their reverse iterators — and `Str` → `Str`, which it did not: it answered a `List` of one-character `Str`s, making `reversed` the single message on a string that changes the type, so `s.reversed().upper()` failed where every other chain composes. `"abc".slice(...)` and `"abc".at(0)` both answer a `Str`, and `list(s.reversed())` is the spelling for anyone who wanted the characters.

Four receivers answered nothing at all, so the ban had no substitute on them: `Bytes` → `Bytes`, `ByteArray` → `ByteArray` (beside the in-place `reverse`, whose hint used to point there — an *in-place mutation* offered as the substitute for a reversal that copies, and nothing at all on immutable `Bytes`), `MemoryView` → `MemoryView` (the native `[::-1]` view copies nothing), and `Dict` → `DictReverseKeyIterator`, one line delegating to `self.keys().reversed()`, which is exactly what `reversed(d)` yields in CPython.

**`key` and `reverse` are keyword-only, on `sorted` and on the in-place `sort`.** CPython spells them `sorted(iterable, /, *, key, reverse)` and `list.sort(*, key, reverse)`, and the reason is the one `min`/`max` already settled: positionally a block is indistinguishable from any other value, so `xs.sorted(f)` and `xs.sorted(reverse_flag)` read the same to the receiver. An absent `key` is `_is_absent`, the test every other optional argument in the language uses — `xs.sorted(key=None)` used to reach CPython as a comparison block and answer `'NoneType' object is not callable`, because POOP's `None` is a `NoneClass` instance and not Python's. The same fix reaches `min`/`max` through `poop/types/_minmax.py`, so `(5).max(3, key=None)` and `col.min(None)` answer rather than refuse.

### No `in` / `not in` — `poop/validators/no_in.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Compare` | op is `ast.In` | `x in col` has a procedural look | `col.includes(x)` |
| `ast.Compare` | op is `ast.NotIn` | `x not in col` has a procedural look | `col.includes(x).not_()` |

### No subscript — `poop/validators/no_subscript.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Subscript` | no `ast.Slice` involved | `obj[key]` looks like an operator | `obj.at(key)` |
| `ast.Subscript` | a bare `ast.Slice` or an `ast.Tuple` containing one (extended slices like `obj[i:j, k:l]`) | `obj[1:3]` looks like an operator | `obj.slice(start, stop)` |

**`at`'s own failures had to stop describing a subscript.** Every wrapper handed the index straight to CPython, so the message named the construct this validator bans: `string index out of range`, `list indices must be integers or slices, not str`, and — for a missing key — the bare `'b'`, a repr with nothing to say a lookup failed. `poop/types/_at.py` owns the wording for all nine wrappers that answer `at`, since writing it out nine times is how the next one gets forgotten: `str has no element at 10 — it has 3 elements`, `list.at expects an int index, got a str`, `dict has no key 'b'`. A `MappingProxy` names itself rather than the `Dict` behind it. An unhashable key is left to CPython on purpose — that failure is about the key, not the lookup, and `cannot use 'list' as a dict key` is already in POOP's vocabulary. Composing a sentence for `KeyError` also meant giving the mirrors `Exception.__str__`: `KeyError.__str__` answers `repr(args[0])`, so a POOP sentence came back wrapped in Python's quotes.

The same treatment reaches the operations next to it, all of which spelt the method as a Python *call* rather than as a message sent: `pop index out of range` and `pop from empty list` (now `list has no element at 9 — it has 2 elements` / `list has no element to remove — it is empty`), `list.index(x): x not in list` and `list.remove(x): x not in list`, which also used the placeholder `x` where the value the reader passed belongs (now `list has no element equal to 9`). The six messages that *remove* an element were reworded from the same two helpers rather than from six new sentences: `d.pop("b")` and `d.popitem()` answer `dict has no key 'b'` / `dict has no element to remove — it is empty` (CPython said `'b'` and `popitem(): dictionary is empty` — a bare repr, then a call and a word POOP does not use for a `dict`), `{1}.remove(2)` and `set().pop()` answer `set has no element equal to 2` / `set has no element to remove — it is empty`, and `ByteArray.pop` / `.remove` answer exactly what `List.pop` / `.remove` do. `no_element_equal_to` and `nothing_to_remove` take the mirror class as an argument because the sentence is receiver-independent and the class is not — `set.remove` raises `KeyError` where `list.remove` raises `ValueError`, and a handler naming the one CPython names must keep matching. `Dict.pop(key, default)` and `Set.discard` are untouched: they ask rather than assert, and neither raises. A `slice` bound is checked in `_resolve_py_slice` before the sequence ever applies it, so it answers `slice bounds must be int, got a str` instead of `slice indices must be integers or None or have an __index__ method` — subscripting and a banned dunder in one breath. `int` and `float` conversions answer `'abc' is not a valid int` / `'abc' is not a valid float` (`'zz' is not a valid int in base 16` when a base was given) rather than `invalid literal for int() with base 10`, which names a call and a base the reader never passed. The base is validated directly rather than read back out of CPython's text — that text says `base` too, so telling the two failures apart by their wording made `int("abc")` answer the base's error.

**The operator path is the one that cannot be fixed at the source.** `"a" + 1` runs `Str.__add__`, which answers `NotImplemented`, then `Int.__radd__`, which answers `NotImplemented` too, and only then does CPython compose `unsupported operand type(s) for +: 'str' and 'int'` — describing an operator as a type-level protocol rather than as a message. No wrapper sees the failure, so there is nothing to catch. `poop/types/_message.py` rewrites the two shapes POOP can reach into `str does not understand #+ with an int` and `int does not understand #< with a str`, deliberately the same register as `MessageNotUnderstood` (`int does not understand #plus`), since it is the same kind of refusal. The operator is kept as the reader typed it rather than translated to a verb: POOP allows binary operators, so `+` is the spelling in the program. Both `executor._describe` and `Error.message()` read through it, so a caught error is not the one place Python's wording survives. `pow` and `divmod` lose the builtin call from the selector, and the messages `Int`/`Float` compose themselves use the same helper rather than restating CPython's.

This is the fragile half and is kept deliberately small: matching another language's message text is a dependency on its internals. Two shapes are recognised, anything unmatched passes through unchanged — so a rewording upstream degrades to the old behaviour rather than to a crash — and `tests/test_message.py` pins both shapes against real operations, so a Python upgrade that changes them fails loudly. `tests/test_no_python_wording.py` runs the failing programs end to end and refuses the phrases naming a forbidden construct; per-site assertions cannot stop the next wrapper from reintroducing one.

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

These are class-definition decorators, not runtime operations on values. They define how a method is bound, not what it does. Blocking them would prevent idiomatic class definitions without a principled POOP substitute. Allowed — and, since `no_decorator`, **only** these three. `@` otherwise applies an arbitrary expression, which is a function call written as syntax rather than sent as a message, exactly the shape `no_subscript`, `no_fstring` and `no_if` exist to remove; nothing checked the boundary, so a plain block silently replaced a method (`@twice` on `def bar(): return 1` made `Foo.bar()` answer `2`). Only a bare `ast.Name` among the three is accepted: `@property(...)` is refused even though `@property` is not, because a called decorator is a runtime operation, which is the distinction the allowance rests on.

### Binary infix operators (`+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`)

`a + b`, `a == b`, `a < b` and their siblings are allowed. These are `ast.BinOp` and `ast.Compare` nodes — the same syntactic family as `+=`, which is already explicitly allowed.

The rationale mirrors Smalltalk: binary messages (`+`, `-`, `*`, …) are the idiomatic way to express arithmetic and comparison. Blocking them would force `a.add(b)`, `a.lt(b)` etc., which is more verbose without being more expressive or principled. The key asymmetry is with *unary* operators: `-a` (USub), `~a` (Invert) have named message equivalents (`a.negated()`, `a.bit_invert()`) and carry no ergonomic benefit in infix form, so they are blocked. Binary forms have no principled substitute.

#### Chained comparison (`a < b < c`)

Chained comparisons fall under this allowance **deliberately**, and they are the one case here that needs its own argument.

Unlike every other construct in *Explicitly allowed*, this one **does** have a substitute: `(1 < x).and_(lambda: x < 10)`. It also delivers exactly the short-circuit semantics `no_and_or` exists to route through a block — with no `and` token, so `no_and_or` (which visits `ast.BoolOp` only) never sees it. Smalltalk cannot express the form at all: `1 < x < 10` parses as `(1 < x) < 10` — binary messages are strictly left-to-right, with no precedence — sending `#<` to a Boolean, which answers `doesNotUnderstand:`.

It is allowed anyway, on ergonomics. `a < b < c` expands to `(a < b) and (b < c)`, whose conjuncts must share the middle operand, so no arbitrary `P and Q` is reachable this way. The construct is a range check, not a general `and` escape hatch — banning it would cost every range check its Python-obvious spelling to close a gap that admits only range checks.

Both halves of that asymmetry are real, and verified by running them: `1 < x < 10` answers `True` while `(1 < x) and (x < 10)` answers `and operator is forbidden — use .and_(lambda: ...) instead`. So is the short-circuit — a `Probe` whose `__lt__` prints, evaluated as `p < p < p`, prints once.

This is therefore the sole allowance resting on Python ergonomics rather than on the absence of a substitute. The opposite call was made for raw dunder access (`no_dunder_attribute`, above): `xs.__len__()` also has a substitute, but unlike a chain it leaks a raw Python primitive as well, so ergonomics had nothing to weigh against.

### Numeric comparisons follow CPython's numeric tower

`Int(1) == Float(1.0)` → `true`. `Int(1) == Complex(1+0j)` → `true`. `True == 1` → `true`. POOP's numeric types (`Int`, `Float`, `Complex`, `Boolean`) compare by value across the tower exactly like CPython, in both directions — `Boolean` is part of it because `bool` is an `int` subclass in Python.

Comparison across *non-numeric* types stays `false` (an `Int` is never equal to a `Str`), mirroring CPython. Each `__eq__` returns `NotImplemented` for operands outside its numeric tower so Python's reflected-comparison fallback applies, keeping the relation symmetric.

## Active types

### PoopExcMeta — `poop/types/exceptions.py`

POOP mirrors the exceptions it can actually reach: `Exception`, `ArithmeticError`, `LookupError`, `ZeroDivisionError`, `OverflowError`, `IndexError`, `KeyError`, `AttributeError`, `NameError`, `TypeError`, `ValueError`, `RuntimeError`, `NotImplementedError`, `RecursionError`, `AssertionError`, `StopIteration`. `Try.except_(ValueError, h)` and `ValueError.raise_("msg")` now take a POOP class, closing the last raw primitive in POOP's substitutes for `try` and `raise`.

Sixteen, not "~100+": Python 3.14 has 71 builtin exceptions, and a language with no I/O and no codecs can never raise the `OSError` subtree or the `Unicode*` family. `RecursionError` is in the list because recursion is POOP's substitute for every loop, which makes it the most reachable of the lot.

**No translation layer is needed**, and that is what makes this affordable: `Try._execute()` catches `except BaseException` and then matches with `isinstance()` — POOP's own code, never a Python `except` clause. So a metaclass `__instancecheck__` is enough for a POOP class to match its native twin, and the mirrors subclass that twin so they stay raisable.

Three constraints:

- `_native` is read from the class's own `__dict__`, never inherited. A user's `class MyError(Exception)` would otherwise inherit the root's `_native = Exception` and catch **every** exception in the program — silent and total. The obvious alternative, an `__init_subclass__` setting `_native = cls`, recurses forever.
- The root also inherits `Object`, so a user exception lands inside the Object tree and answers `print()` / `class_name()`. Before this, `class MyError(Exception)` sat outside it entirely.
- `ExceptionTransformer` **must run after `RaiseTransformer`**. That one matches an uppercase `ast.Name` followed by `.raise_(...)`; rewriting `ValueError` to `_poop_ValueError` first leaves a name starting with an underscore and silently stops `raise_` from being recognised.

`Error.kind()` answers the POOP class, not a `Str` — `e.kind().name()` for the name. An unmirrored native answers with the nearest mirrored ancestor rather than leaking the raw class back out.

**A caught error refuses under the name it answers everywhere else.** `Error` is cloaked as `object`, since no exception name is true for the *class* — but `explain` labels a receiver with `type(obj).__name__`, so `e.zzz()` said `object does not understand #zzz` while the same `e` answered `ZeroDivisionError` from `class_name()` and printed it from `__str__`. That was the fourth spelling of the leak those three close. `Error.does_not_understand` now passes the wrapped class's name as `explain`'s optional `label`; every hint shape (Smalltalk selector, typo, `:methods`) is unchanged, and Python agrees on the wording — `except ZeroDivisionError as e` reports `'ZeroDivisionError' object has no attribute 'zzz'`. The label is passed, not derived: asking each receiver for its class would route through a message a proxy is free to answer with anything.

**The table is also how POOP raises its own diagnostics.** A wrapper composing a POOP message used to carry it on a native class — POOP's advice labelled with Python's vocabulary, and nothing stopping the next wrapper from doing the same. The rule inside `poop/types/` and `poop/transformers/` is now one line: a failure a program can reach is raised as `MIRRORS["TypeError"](...)`, never as the bare builtin. Because the mirrors subclass their twin the change is invisible at runtime — anything that caught the native still catches it — which is the point: it is a guardrail for the wording work, not a behaviour change. `tests/test_mirrored_raises.py` sweeps both packages, since per-site tests cannot stop the next wrapper from reintroducing a native. Two spellings stay native, both exempt by rule rather than by site: `__getattr__`'s dunder refusal (Python's attribute protocol answering Python's own probe, and reached while `exceptions` is still importing — the mirrors are built on `Object`) and the abstract-stub / import-time guards no program can reach.

### PoopMeta — `poop/types/meta.py`

Classes are objects and answer messages, as in Smalltalk. `Foo.print()` used to answer `Object.print() missing 1 required positional argument: 'self'` — Python failing to bind a method, not POOP refusing a message.

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

**All** of `Object`'s protocol is answered class-side, each by its own `class_side` descriptor — a metaclass cannot inherit them into class-side lookup, which is why `class_side` exists at all. Without them the bans contradicted themselves: `hash(Foo)` answers "use `obj.hash()` instead" while `Foo.hash()` answered a binding error, naming a substitute that did not exist on that receiver. Beyond the value-answering messages above, the class side also carries `is_identical` / `not_identical` (for banned `is`), `is_instance` (for banned `isinstance`), `get_attr` / `set_attr` / `del_attr` (for the banned `getattr` family, dunder guard included), `assert_` (for banned `assert`, always holding since a class is truthy), and `if_none` / `if_not_none` (a class is never none). `Foo.is_instance(Object)` is `false` — a class is an instance of its metaclass, not its bases; `Foo.is_subclass(Object)` is the "descends from" question.

`Foo.class_()` and `Foo.class_name()` are **refused**, and name `#name` instead. Smalltalk answers the metaclass — `Foo class` is `Foo class` — and POOP has none to answer with: `PoopMeta` is not itself a POOP class (`type(PoopMeta)` is `type`), so handing it back would leak the raw class object the class side exists to remove. Answering `Foo` would quietly make `class_name` mean one thing on an instance and another on a class.

`Foo new` is **not** provided: `Foo()` already builds an instance and is not forbidden, so a `new` message would be Smalltalk parity rather than a substitute for anything — the bar cascades and `yourself` failed to clear.

Three constraints, each load-bearing:

- `PoopMeta` derives from `ABCMeta`, not `type`. `Boolean(Object, ABC)` otherwise fails with `metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases`.
- Every class-side message is a **data descriptor** (`class_side`), not a plain method. Attribute lookup on a class searches the class's own MRO *before* the metaclass, so a plain `PoopMeta.print` would never be reached — `Object.print` would win and answer the unbound function this exists to remove. Only a data descriptor is consulted first. Instances are unaffected: instance lookup never consults the metaclass, so `Foo().print()` still finds `Object.print`. Being a data descriptor means it also owns assignment, and it refuses: `Foo.name = 5` and `Foo.set_attr("name", 5)` both answer `#name is answered by every class — it cannot be rebound`. It used to raise `AttributeError(self._name)` — `AttributeError: name`, which reads as if the *word* `name` were the problem and says neither what was refused nor why.
- Nothing declares the metaclass. `ClassTransformer` already routes every user class through `Object`, and a metaclass is inherited.

`Object superclass` answers `none`, mirroring Smalltalk's `nil` — which is also what keeps the raw Python `object` at the root out of reach.

### Object — `poop/types/object.py`

Concrete root of all POOP types. The table below highlights the universal methods that map directly onto Smalltalk messages — it is **not exhaustive**. The full API also includes `if_none`, `if_not_none`, `hash`, `callable`, `is_subclass`, `repr`, `ascii`, `format`, `has_attr`, `set_attr`, `del_attr`, `does_not_understand`, and `print` (see `poop/types/object.py` for signatures).

**There is no `id`.** It answered `id(self)` — CPython's address, the raw pointer POOP otherwise never admits exists — and that answer was not merely leaky but *wrong*: CPython recycles addresses, so an object created after another was collected claims the same identity, which is not a behaviour Smalltalk's `identityHash` has. It also collapsed onto `hash` for anything that does not hash by value, since `__hash__` returned the same number: two distinct messages, one answer, and that answer an address. Answering a POOP-owned identity instead would need an `_identity` slot on `Object` — a pointer on every object in a language where every integer is one — to buy a message whose only power over `is_identical` is keying a `Dict` by identity, which no example asks for. So `is_identical` is the substitute `no_id` names, and it answers the identity *question* without materialising a number. `hash` stays exactly as it was, because `Dict` and `Set` key on `__hash__` and value types must hash by value for them to work at all — but `Object.__hash__` now answers Python's own identity hash rather than the address verbatim.

#### `does_not_understand` — Smalltalk's `doesNotUnderstand:`

An unknown message answers `MessageNotUnderstood`, not Python's `'int' object has no attribute 'frobnicate'`. The message names the receiver's class and the selector, and adds the best hint it has: the POOP name of a Smalltalk selector (`Smalltalk's #size is #len here`), a close match for a typo (`did you mean #upper?`), or a pointer at `:methods`. The Smalltalk selectors live in a written-down table (`poop/types/_selectors.py`) because string similarity cannot map `size` to `len` — the two share no letters.

Override `does_not_understand(name)` to answer an unknown message instead of refusing it; this is the metaobject hook that makes real proxies possible. The override answers a callable, which is also the only way to reach the arguments — attribute lookup runs before the call.

Three implementation constraints, each load-bearing:

- `MessageNotUnderstood` inherits `AttributeError`. `hasattr` and three-argument `getattr` swallow that and nothing else, so a plainer base would break `Object.has_attr` and `get_attr(name, default)` — POOP's own substitute for the banned `getattr`.
- Dunder names never reach the hook. Python probes any object for `__copy__`, `__getstate__` and friends, and a proxy would otherwise answer those probes as if a user had sent them.
- `__getattr__` is hidden behind `if not TYPE_CHECKING`. A visible one answers `Any` for every name, which would make `xs.frobnicate()` type-check on every POOP object and stop `ty` from catching typos anywhere in the codebase. Statically an unknown message is still an error; the hook changes what happens when one is sent, not what is knowable before.

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

`ReturnTransformer` (`poop/transformers/return_.py`) keeps the implicit-return path on the POOP side: a bare `return` becomes `return _poop_none`, and a function body that does not end in `return`/`raise` gets a trailing `return _poop_none` appended, so a void method answers the `none` singleton instead of raw `NoneType`. `__init__` is skipped (CPython requires it to return real `None`).

`VarargsTransformer` (`poop/transformers/varargs.py`) keeps variadic parameters on the POOP side: a method with `*args` / `**kwargs` gets a prologue (`args = _poop_tuple_from(args)`, `kw = _poop_dict_from_kwargs(kw)`) so `args` is a POOP `Tuple` and `kw` a POOP `Dict` (with `Str` keys) instead of a raw `tuple`/`dict`. Variadic lambdas wrap their body in a nested lambda that receives the converted values.

It carries the **call site** too, which is the other end of the same round trip. Python's `**` demands raw `str` keys and a POOP `Dict` holds `Str`, so a splat answered CPython's own words about a POOP object — `A().m(**{"a": 1})` raised `TypeError: keywords must be strings`. Three of the four splat positions already worked (`f(*xs)` because a `Tuple` is iterable, `def m(**kw)` by the prologue above, `{**a, **b}` through `_poop_dict_merge`), and `DictTransformer` had already met the same constraint for `dict(**other)` and worked around it there; only the general call was left. Each `**d` is now wrapped as `**_poop_kwargs_from(d)`, the inverse of `_poop_dict_from_kwargs`: keys unwrap, values stay POOP objects, so a `**kw` parameter on the far side re-wraps them into a `Dict` unchanged. A `MappingProxy` splats too. Both failure modes reach CPython raw through the faithful-unwrap idiom, so `f(**{1: 2})` still answers `keywords must be strings` — now about a key the program actually wrote — and `f(**5)` answers `argument after ** must be a mapping, not int`. The rewrite must run after `DictTransformer` and `RaiseTransformer`, which the declaration order guarantees; it covers `_poop_raise(Exc, **kw)` for free.

`UnpackTransformer` (`poop/transformers/unpack.py`) keeps starred unpacking on the POOP side: CPython's `UNPACK_EX` builds the rest-collection of `c, *rest = xs` as a raw `list`, so after each assignment containing a `*target` the transformer appends `target = _poop_list_from(target)` — one per starred name, handling nested (`a, (b, *inner) = …`) and attribute (`a, *self.rest = …`) targets.

### EllipsisClass — `poop/types/ellipsis.py`

`EllipsisClass(Object)` with singleton `ellipsis`. Transformer rewrites `ast.Constant(value=Ellipsis)` → `_poop_ellipsis`.

`...` is a placeholder, not a value with messages, so `EllipsisClass` carries no behaviour of its own beyond the universal `Object` protocol — the same shape as `NoneClass`, and for the same reason: it exists so `...` is not the one literal that reaches runtime as a naked Python primitive.

`__str__` returns `"Ellipsis"` and `class_name()` answers `"ellipsis"`, matching CPython's `str(...)` and `type(...).__name__`.

No validator bans `...`: with the literal transformed, `pass` and `...` are both valid stub bodies and neither leaks a primitive. Note that POOP's own examples declare no abstract methods at all — the base class simply omits the message and lets polymorphism supply it — so `...` has no idiomatic role in POOP beyond Python muscle memory.

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

**Calling a block with the wrong number of arguments answers a block's message.** CPython reported it against the raw lambda — `<lambda>() takes 1 positional argument but 2 were given` — naming the Python class POOP cloaks as `function` and prints as `<block>`, in a calling convention a block does not have. Since blocks are POOP's only control flow, this is also one of the most-read messages in the language. `Block.__call__` now answers `block expects 1 argument, got 2`, stating the arity exactly (`0 arguments`, `1 to 2 arguments`, `at least 1 argument` for a variadic block, and `block does not accept 3 arguments` for a callable CPython cannot introspect). A `TypeError` raised by the block's *body* passes through untouched, and the two are told apart by the traceback: a signature mismatch is raised by the call machinery before the block runs, so it stops at `Block.__call__`, while a body failure has the block's own frame below. `while_true` / `while_false` drive the condition through `__call__` for the same reason.

**A method fetched by name is a block too.** `get_attr` guards *which* names may be read, but what came back was CPython's bound method — callable, yet understanding no message: `"abc".get_attr("upper").print()` raised Python's own `AttributeError`, the last member of the `getattr`-substitute family still handing back a native. `_as_block` (in `block.py`, used by both `Object.get_attr` and the class side) wraps a raw callable answer, so a method reads back as the same kind of object a lambda does — it still calls, prints as `<block>`, and answers `class_name()` → `function`. State, a `default` fallback, and a POOP class (callable, but already an object with its own protocol) pass through untouched.

**The other spelling stays a leak, on purpose and on a measurement.** `[1, 2].len` is ordinary `ast.Attribute` syntax that no validator refuses, and it answers CPython's bound method — so the two ways of asking for a method disagree, one giving a `Block` and one giving a native. The only hook that sees a *successful* lookup is `__getattribute__`, which every message send goes through: wrapping there (skipping `_`-prefixed names, or `Block.__call__` re-wraps its own `_fn` without bound) measured **1.12 s → 2.02 s** on 200k sends, +81% on the central operation of the language, and broke nine wrong-arity diagnostics by making them blame the wrapper instead of the receiver. A validator cannot close it either: an `ast.Attribute` in `Load` position is indistinguishable from a state read without runtime types, and `self.count` is a plausible field name that is also a message. The leak is accepted, and it is narrow — POOP has no free functions to hand a bare method to, so the spelling has no idiomatic use.

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
| — | `sum(start=...)` | sum of elements; `Int(0)` for empty; optional `start` mirrors Python `sum(it, start)` |
| — | `min(key=None, default=...)` | smallest element; mirrors Python `min` |
| — | `max(key=None, default=...)` | largest element; mirrors Python `max` |
| — | `all(block)` | `true` if block holds for every element |
| — | `any(block)` | `true` if block holds for at least one element |
| — | `enumerate(start=Int(0))` | returns an `Enumerate` of `Tuple(Int(i), item)` pairs |
| — | `zip(*others, strict=false)` | returns a `Zip` of `Tuple(...)` |

`map`/`filter`/`filter_false` are **lazy** — they return `Map`/`Filter` iterators (same family as `Enumerate`/`Zip`) regardless of the receiver's type, mirroring Python's `map`/`filter` builtins. The block runs only as the result is consumed. To materialize, pass the lazy result to a constructor: `list(col.map(f))`, `tuple(col.filter(g))`, `set(col.map(f))`, `bytes(col.map(g))`. Methods that consume the iterator (`do`, `sum`, `min`, `max`, `find`, `reduce`, `all`, `any`) work on `Map`/`Filter` directly without materialization.

`Dict.do` is not from the mixin — it passes `Tuple(key, value)` pairs to the block instead of plain elements. `Bytes` and `ByteArray` override `find` for substring search (different semantics from the mixin's element-finding `find`).

### Builtin-mirroring method signatures

Every builtin-substitute method mirrors the **full** Python signature of the method it replaces — the same optional and variadic arguments, so `n.to_bytes()` and `xs.index(x, start, stop)` work exactly as in CPython. Optional arguments accept the POOP wrapper *or* `none` (both fall back to the builtin's default), following the same convention as the collection methods above (`zip(*others, strict=false)`, `enumerate(start=Int(0))`). "Mirrors the full signature" includes the *combinations*: `List.index` and `Tuple.index` branched on which bound was present and the first branch dropped `stop` on the floor, so `[1, 2, 3].index(3, stop=1)` answered `2` where CPython raises — and the same branch read an explicit `none` stop as *stop at 0*, which makes every search fail. Both pass the bounds straight through now, defaulting a missing `stop` to `len` rather than `None` because `list.index`, unlike `str.index`, takes no `None` bound.

| Type | Method | Signature | Notes |
|---|---|---|---|
| `Int` | `to_bytes` | `to_bytes(length=Int(1), byteorder=Str("big"), signed=false)` | `signed` is keyword-only, like `int.to_bytes` |
| `Int` | `from_bytes` | `from_bytes(bytes, byteorder=Str("big"), signed=false)` | classmethod; `signed` keyword-only |
| `List`, `Tuple` | `index` | `index(obj, start=none, stop=none)` | optional search bounds; either may be given alone, as in Python |
| `MemoryView` | `tobytes` | `tobytes(order=Str("C"))` | `order` ∈ `{"C", "F", "A"}` |
| `MemoryView` | `hex` | `hex(sep=none, bytes_per_sep=Int(1))` | mirrors `Bytes.hex`; the one message that shows the contents |
| `Set`, `FrozenSet` | `union`, `intersection`, `difference` | `(*others)` | each operand may be **any iterable** (`List`/`Tuple`/…), not only another set |
| `Set`, `FrozenSet` | `symmetric_difference`, `isdisjoint`, `issubset`, `issuperset` | `(other)` | operand may be any iterable |
| `Set` | `update`, `intersection_update`, `difference_update` | `(*others)` | in-place; operands may be any iterable |
| `Set` | `symmetric_difference_update` | `(other)` | in-place; operand may be any iterable |
| `Dict` | `update` | `update(other)` | `other` is a `Dict`, a `MappingProxy`, or an iterable of 2-element `(key, value)` pairs — a wrong-length element raises the faithful `ValueError` |

**Python's numeric accessors are messages too.** `real`, `imag`, `numerator`, `denominator` (on `Int` / `Float` / `Complex`) and `start` / `stop` / `step` (on `Range`) are `Int`- or `Float`-answering **methods**, sent as `(5).numerator()` and `range(1, 5).start()`. They were `@property` getters, which made the operation an attribute access — the shape the language exists to remove — and made the message spelling fail with `'int' object is not callable`, naming a native for a value POOP presents as an `int`. Their neighbours in the same files were already methods (`Int.conjugate()`, `Int.as_integer_ratio()`, `Complex.abs()`, `Float.is_integer()`, and `Slice.start()` / `stop()` / `step()`), so the split was inconsistent within a single file rather than a policy. `@property` remains allowed *in user code* as a class-definition decorator; what it may not do is define what an operation is. `tests/test_cloak.py` sweeps every wrapper for a public `property` so the next one cannot slip in — the class-side data descriptors in `poop/types/meta.py` live on the metaclass and are outside that sweep by construction.

The distinction between set **methods** and set **operators** follows CPython exactly: the *methods* above accept any iterable, but the *operators* (`|`, `&`, `-`, `^`, `<`, `<=`, `>`, `>=`) still require two set-likes (`{1} | [2]` is a `TypeError`) — see *Explicitly allowed → Binary infix operators*. A non-iterable operand passed to a method raises the same `TypeError` CPython would.

### Map / Filter — `poop/types/map.py`, `poop/types/filter.py`

`Map` and `Filter` are lazy iterator types in the same family as `Enumerate` and `Zip`. They wrap a source iterable and a block, and apply the block on demand:

- `Map(source, block)` yields `block(item)` for each item.
- `Filter(source, block)` yields `item` when `block(item)` is truthy.

Both inherit `_IterableMixin` so chains like `col.map(f).filter(g).sum()` keep iterating once through the source. Both are one-shot, exactly as `Enumerate` and `Zip` are and as Python's own `map`/`filter` are: `__iter__` answers `self`, `_materialize` builds the internal generator once and drops the source and block with it, so a view that has been consumed answers nothing on a second pass — by `.next()`, by `.do()`, or by a chained view.

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
| `slice(start, stop, step=None)` | slice → `Range` |
| `slice(slice_obj)` | slice via `Slice` value object → `Range` |
| `reversed()` | returns reversed `Range` |
| `includes(value)` | `true` if `value` is in the range |
| `count(value)` | number of occurrences (always `0` or `1`) |
| `index(value)` | position of `value`, or raises `ValueError` (`range has no element equal to 9`) |
| `start()` / `stop()` / `step()` | the underlying `Int` bounds |

**A sliced `Range` is a `Range`**, as `range(10)[1:3]` is `range(1, 3)` in CPython and as `reversed()` already answered. Wrapping the selected elements in a `List` allocated one `Int` per member of the *result*, so `range(1000000000000).slice(0, 3)` — three elements in Python — materialized a trillion. The exclusive stop is shifted back by `sign` to round-trip through the constructor's inclusive convention, the same encoding `reversed()` undoes.

### Object.print — `poop/types/object.py`

All POOP objects inherit `print()` from `Object`. `List` and `Tuple` override to support `sep`.

| Message | Behavior |
|---|---|
| `obj.print()` | prints `str(obj)` followed by `\n`; returns `None` |
| `obj.print(end="")` | controls the terminator |
| `obj.print(flush=True)` | forces buffer flush |
| `list.print(sep=", ")` | `List`/`Tuple`: joins elements with `sep` (default `" "`) |

`"".print()` prints a blank line.

**A container that holds itself prints the ellipsis, it does not exhaust the stack.** `List`, `Tuple` and `Dict` build their displayed form from `repr` of each element, so `xs.append(xs)` made `xs.print()` recurse until CPython gave up — a `RecursionError` about POOP's internals, raised by a program that only asked to see its data. All three carry `reprlib.recursive_repr` with the fill value CPython uses for that container (`[...]`, `(...)`, `{...}`), so `[1, [...]]`, `([(...)],)` and `{'a': {...}}` come back exactly as Python prints them. `Set` and `FrozenSet` need no guard: reaching a cycle through one would mean holding something unhashable.

### Error — `poop/types/error.py`

`Error(Object)` wraps a caught Python exception. Handlers in `Try.except_` always receive an `Error` object.

| Method | Behavior |
|---|---|
| `message()` | returns exception message as `Str` |
| `kind()` | returns the POOP exception class; `kind().name()` for the name as `Str` |

`__str__` is built on the identity `class_()` already answers — `"ZeroDivisionError: division by zero"` — not on the wrapper. It used to print `Error(division by zero)`, naming a `poop.types` detail user code can neither name nor construct, so the same object identified itself two different ways: `e.class_name()` answered `ZeroDivisionError` while `e.print()` answered `Error(...)`. A message-less exception degrades to the bare class name rather than a dangling colon, as `executor._describe` does for the same reason.

### Try — `poop/types/try_.py`

`Try(Object)` implements deferred try/except/finally as a message-passing builder. The block is executed lazily — only when `.run()` or `.finally_()` is called.

| Message | Method | Behavior |
|---|---|---|
| `[block] on: ExcType do: handler` | `Try(block).except_(ExcType, handler)` | registers a handler; chainable |
| `[block] ensure: finallyBlock` | `Try(block).finally_(block)` | sets finally block **and** executes; answers the protected block's value |
| *(terminal)* | `.run()` | executes without finally block; answers the protected block's value |

`.run()` and `.finally_()` answer the protected block's value, or the matching handler's value when one fires — like every other POOP block, and like Smalltalk's `on:do:`. This is what makes `try: return f() except: return default` expressible; without it `no_try` would ban a construct with no substitute. Both are terminal, so builder chaining is unaffected: `.except_()` is the chainable message. The cleanup block's own value is discarded, mirroring Smalltalk's `ensure:`.

`exc_type` is a POOP exception class (see *PoopExcMeta* below). Unhandled exceptions are always re-raised. Multiple `.except_()` calls are matched in order.

`Try` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/try_.py` — namespace-only, no AST rewrite.

### With — `poop/types/with_.py`

`With(Object)` implements the context manager protocol as a message-passing builder. The context manager block is executed lazily — only when `.do()` is called. A `With` is single-use: `.do()` releases its captured block once it runs, so re-invoking `.do()` raises `RuntimeError` rather than re-running — mirroring `Try`'s single-use semantics and avoiding retaining the closure (and anything it captured) past execution.

| Message | Method | Behavior |
|---|---|---|
| `[block] value: aResource` | `With(lambda: cm).do(lambda resource: body)` | acquires resource via `__enter__`, runs body, calls `__exit__`; answers the body's value |

`.do()` answers the body's value, for the same reason `Try.run()` does. When `__exit__` suppresses an exception the body never produced a value, and `.do()` answers `none` — Python's `with` simply carries on past the block in that case.

The context manager object must implement Python's `__enter__`/`__exit__` protocol — a deliberate primitive leak, consistent with `Try` using native exception types. Exceptions propagate via the standard `__exit__` return value: if `__exit__` returns falsy, the exception is re-raised; truthy suppresses it.

**A non-block argument is refused at the boundary, where it has a name.** `Try(5)`, `.except_(ValueError, 5)` and `With(5)` all answered `'int' object is not callable`, one frame inside CPython's call machinery — true of every POOP object, and silent about what was expected. `With(a_manager)` is the mistake worth optimizing for: `With` takes a block that *answers* a manager, and passing the manager itself is the obvious first attempt. `_require_block` (`poop/types/block.py`, beside the `Block.__call__` rewording that established the rule) answers `the manager argument must be a block, got a C — write With(lambda: …)`, and the check runs in `__init__` rather than in `run`/`do` for the same reason both slots below are resolved up front: the failure lands where the mistake was written, not after a deferred block has already had side effects.

**Both slots are resolved before either is called**, as Python's `with` does. `With` used to enter first and reach for the exit half only after the body had run, so a manager that could be entered but never exited ran its acquisition and then failed — the side effect happened with nothing left to undo it. The lookup is on the *type*, where Python's protocol reads it from, so a `does_not_understand` hook answering a callable cannot forge a context manager. The refusal names the missing half of the protocol (`it cannot be entered` / `it cannot be exited`) rather than the dunder CPython names: a diagnostic spelling `__exit__` names the construct `no_dunder_attribute` bans, which is why the two failing programs are in the `test_no_python_wording` sweep.

> **Tradeoff**: context managers must implement Python's native protocol (`__enter__`/`__exit__`). POOP cannot redefine resource acquisition semantics without reimplementing every standard context manager (files, locks, etc.), which is impractical.

`With` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/with_.py` — namespace-only, no AST rewrite.

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

### Ellipsis — `poop/transformers/ellipsis.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=Ellipsis)` | `_poop_ellipsis` |
| `ast.Name(id="Ellipsis")` | `_poop_ellipsis` |

The `Name` row is not redundant: `...` and `Ellipsis` are two spellings of the same value, and rewriting only the literal would leave the name handing out the raw primitive — the same asymmetry `vars()` / `obj.__dict__` shows for validators.

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
| `ast.Call` with `str(...)` | `_poop_str_from(...)`, whatever the arity |

**A constructor call never resolves to the wrapper class.** Every rewriter used to guard its `visit_Call` on the arity its converter could handle (`not node.keywords and len(node.args) <= 1`) and let anything else fall through to `visit_Name`, which renames the bare builtin to the *class* binding — and a class constructor is variadic, `List(*elements)`. So one name meant "convert" at one arity and "build from these elements" at another, and only the first matched Python: `list(1, 2)` answered `[1, 2]` where CPython raises `list expected at most 1 argument, got 2`, and `set(1, 2)` answered `{1, 2}`. `list(a, b)` is a plausible slip for `[a, b]`, and being *accepted* is the failure mode POOP's diagnostics work hardest to avoid. The scalar wrappers fell through the same way, and there the answer was right but the report named `__init__` — a dunder `no_dunder_attribute` bans outright — from a construct spelled without a dunder anywhere (`str(b"ab", "utf-8")` answered `str.__init__() takes 2 positional arguments but 3 were given`, for a call CPython answers `"ab"` to). Every `<builtin>(...)` now reaches its converter, which refuses over-supply through the shared `refuse_extra_arguments` (`poop/transformers/_arity.py`): `list is built from at most one collection, got 2 arguments — write a literal for elements`. `_poop_str_from` also grew the decoding form CPython has, delegating to `Bytes.decode` so the codec table above governs it. The `visit_Name` rename stays — a bare `list` used as a value still answers POOP's class — but it is no longer reachable by a *call*.

**`encode`/`decode` name their surface instead of inheriting CPython's codec table.** Handing the codec name straight through meant `"a".encode("rot13")` answered `'rot13' is not a text encoding; use codecs.encode() to handle arbitrary codecs` — advice no POOP program can follow, since `import` is forbidden and `_ALLOWED_BUILTINS` has no route to a module. `poop/types/_codec.py` accepts four text encodings (`utf-8`, `utf-16`, `latin-1`, `ascii`, plus the spellings a reader would reasonably type: `utf8`, `latin1`, `iso-8859-1`, `us-ascii`, case-insensitively) and the three codec-independent error handlers (`strict`, `ignore`, `replace`), refusing anything else with `unknown encoding 'rot13' — POOP encodes utf-8, utf-16, latin-1 and ascii`. The `errors=` argument is checked for the same reason the encoding is: `namereplace` and `backslashreplace` are the same codec machinery reached under another name. This is the argument `poop/types/exceptions.py` already makes — "a language with no I/O and no codecs cannot reach the `OSError` subtree or the `Unicode*` family" — applied to the one door that was still open.

### Bytes — `poop/transformers/bytes.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=bytes)` | `_poop_bytes(b)` |
| `ast.Call` with `bytes(x)` or `bytes(s, enc)` | `_poop_bytes_from(x)` / `_poop_bytes_from(s, enc)` |

### List — `poop/transformers/list.py`

| AST node | Replacement |
|---|---|
| `ast.List` (Load context) | `_poop_list(*elts)` |
| `ast.Call` with `list(...)` | `_poop_list_from(x)` |

### Tuple — `poop/transformers/tuple.py`

| AST node | Replacement |
|---|---|
| `ast.Tuple` (Load context) | `_poop_tuple(*elts)` |
| `ast.Call` with `tuple(...)` | `_poop_tuple_from(x)` |

### Set — `poop/transformers/set.py`

| AST node | Replacement |
|---|---|
| `ast.Set` | `_poop_set(*elts)` |
| `ast.Call` with `set(...)` | `_poop_set_from(x)` |

### Dict — `poop/transformers/dict.py`

| AST node | Replacement |
|---|---|
| `ast.Dict` (no unpacking) | `_poop_dict_from_pairs(k1, v1, k2, v2, …)` |
| `ast.Call` with `dict(...)` | `_poop_dict_from(x)` — `x` must be `Dict` or iterable of 2-element `Tuple`/`List` pairs |

### Complex — `poop/transformers/complex.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=complex)` | `_poop_complex_literal(v)` |
| `ast.BinOp` combining real + imaginary literal | collapsed into `_poop_complex_literal(r+ij)` |
| `ast.Call` with `complex(r, i)` | `_poop_complex_from(r, i)` |

### ByteArray — `poop/transformers/byte_array.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `bytearray(...)` | `_poop_bytearray_from(x)` |

### MemoryView — `poop/transformers/memory_view.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `memoryview(...)` | `_poop_memoryview_from(x)` |

**A `MemoryView` prints what it is, not where it lives.** `__str__` was `repr(self._value)`, so `memoryview(b"ab").print()` answered `<memory at 0x70cb7ab59240>` — the raw pointer `Object.__hash__` refuses to answer for the reason its own comment gives, under the class name `memory`, which is neither the POOP name nor the cloak, and unstable across runs so that no test could pin it and no example could show it. It answers `<memoryview of 2 bytes>` instead. Printing the bytes themselves would re-materialize an arbitrarily large buffer just to print it — the cost a `Range` refuses when sliced — so the contents are shown on request by `hex()`, and `slice(...)` and `includes(x)` complete the set of messages the `no_subscript` and `no_in` bans point at: `mv[0:2]` is a `memoryview` in CPython and `98 in memoryview(b"ab")` is `True`, and a view you cannot look into is one gap with four spellings.

### FrozenSet — `poop/transformers/frozen_set.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `frozenset(...)` | `_poop_frozenset_from(x)` |

### Range — `poop/transformers/range.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `range(stop)` / `range(start, stop)` / `range(start, stop, step)` | `_poop_range(...)` → `Range` |

### Raise — `poop/transformers/raise_.py`

Intercepts `UppercaseName.raise_(args)` (where `UppercaseName` starts with a capital letter) and rewrites it to a function call that works inside lambdas.

| Pattern | Replacement |
|---|---|
| `ExcType.raise_('msg')` | `_poop_raise(ExcType, 'msg')` |
| `ExcType.raise_('msg', code=42)` | `_poop_raise(ExcType, 'msg', code=42)` |

> **Why not `ast.Raise`?** The transformer generates a function call (`_poop_raise(...)`) instead of an `ast.Raise` statement. Statements are illegal inside `lambda` expressions — POOP's primary block mechanism. This design allows `Try(lambda: KeyError.raise_("msg")).except_(...)` to work correctly.

> **Tradeoff**: `ExcType` must be a Python exception class (not a POOP object). Only uppercase-named receivers are intercepted; lowercase `obj.raise_()` is passed through to the object's own method at runtime.

> **Keywords are forwarded**, and `_poop_raise` takes `**kwargs` for it. They used to be dropped on the floor — and `raise` is a statement, so `raise_` is the *only* way to signal an error: an exception whose fields arrive by keyword could not be raised at all. The failure named the argument the program *did* pass, `MyError.raise_("boom", code=42)` answering `missing 1 required positional argument: 'code'`. A `**kwargs` splat rides along on the same `**kwargs`.

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
