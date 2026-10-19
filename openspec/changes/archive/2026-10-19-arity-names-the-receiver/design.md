# Design

## Context

See proposal.md for the motivation. The facts that shape the approach:

- `cloak` (`poop/types/_cloak.py`) renames a function's `__qualname__` once,
  at its definition site, to `<cloaked class>.<name>`. A shared mixin is
  cloaked as `object`, `ByteArray` reuses `Bytes`'s functions and
  `FrozenDict` reuses `Dict`'s, so the frozen prefix belongs to the
  *definer*, and a definer shared by many receivers cannot hold a name that
  is true for all of them.
- Every public method read off an instance or a class passes through
  `_MethodBlock.__call__` (`poop/types/block.py`): the `message` descriptor
  wraps instance-side reads, and `class_side.__get__` wraps class-side
  ones. That call is the one place where both the receiver and the function
  are in hand.
- `class_side.__set_name__` (`poop/types/meta.py`) cloaks the function to
  the bare message name, and its comment records that `Foo.print()` was
  "not available here: one function is shared by every class".
- CPython names the class that **defines** the method:
  `(5).__reduce_ex__()` names `object`, `Stack().append()` names `list`,
  `bytearray.lower()` and `frozendict.keys()` name themselves (each defines
  its own methods, and `frozendict` is not a `dict`), and `int.mro(1)` names
  `int`.
- The wording sweep (`tests/test_no_python_wording.py`) skips any sentence
  matching `_ARITY`, so it has never looked at the name inside one.

## Goals / Non-Goals

**Goals:**
- Every wrong-arity sentence names a class a program can write that
  answers the message, and that class is the one CPython would name.
- No cost on a successful send.

**Non-Goals:**
- Changing the sentence's shape, or any POOP-worded arity refusal (see the
  proposal).
- `bool` naming `int` for the messages CPython's `bool` inherits from `int`.
  `Boolean` re-supplies the int side itself and is not an `Int` in POOP, so
  it names `bool`. This is the one divergence left, and it names a class
  that does answer the message.

## Decisions

### The callee is renamed at the call, in `_MethodBlock.__call__`

The call becomes `try: return self._fn(*args, **kwargs)` with an
`except TypeError` that rewrites only a *binding* failure. A binding failure
is raised in `__call__`'s own frame before the method body runs, so its
traceback has no frame below `__call__`. The test is
`exc.__traceback__.tb_next is None`, together with the text starting with
the function's current `__qualname__` followed by `()`. A `TypeError` the
method body raises fails the first test and passes through untouched, even
when its text happens to start with the same name. The rewrite replaces
that prefix and re-raises `mirrors.TypeError(...) from None`, the shape
every POOP sentence takes. A `try` costs nothing on 3.15 when nothing is
raised, so the hot path, which INFECTIONS.md measures frame by frame, is
unchanged.

Alternatives considered:
- Renaming at definition: impossible for a definer shared by several
  receivers, which is the whole defect.
- Rewording every arity failure in POOP's words: rejected by the
  established policy and by the user's choice to stay close to CPython.

### Which class is named

For a receiver that is a class (the class side, and a classmethod read off
a class), the prefix is that class's name: `int.hash()`, `Foo.print()`.
For an instance:

1. If the message's owner (the first class in the receiver's MRO whose
   `__dict__` holds the name) is the root `Object`, or a program's own
   class, the current prefix stands. It already names what CPython names.
2. Otherwise the prefix is the nearest wrapper in the receiver's MRO. For a
   wrapper that is the receiver's own class (`list`, `bytearray`,
   `frozendict`, `list_iterator`, `dict_keys`). For a program's subclass of
   a wrapper it is the wrapper it extends (`list` for `class Stack(list)`).

The owner is compared by identity with `Object`, because the shared mixins
are cloaked with the same name `object`. "Wrapper" and "program's class"
are told apart the way `_wrapper_classes` in the sweep already does: a
wrapper is cloaked into `builtins`, and a program's class is not. The
exact predicate is an implementation detail of this one function.

### A `staticmethod` carries the class it was read through

A `staticmethod` binds to a plain function with no `__self__`, so the rule
above has no receiver to read. The wording sweep found the case:
`bytearray.maketrans` blamed `bytes.maketrans()`. The `message` descriptor
already knows `owner` at `__get__`, so it passes that class to
`_MethodBlock`, which keeps it in one slot. `_cpython_name` then reads that
class's MRO in place of a receiver's.

### The class side needs no change of its own

`class_side.__get__` already answers `_MethodBlock(MethodType(fn, cls))`,
so the class receiver is `__self__`, and the rule above names it. The
comment in `class_side.__set_name__` that called this unavailable is
updated to point here.

### `print` is keyword-only everywhere it is defined

`Object.print`, `List.print`, `Tuple.print` (with `sep`), the
exception-instance `_print` and `PoopMeta.print` take `*, end=…, flush=…`
(and `sep=…`). A positional argument then fails at binding, and the rule
above words it: `object.print() takes 1 positional argument but 2 were
given`, `list.print() …`, `int.print() …`. This is the sentence CPython
gives for a keyword-only parameter, including the `(and 1 keyword-only
argument)` form when `end` is also passed. The alternative, printing the
extra positionals as CPython's `print(*objects)` does, was rejected: the
receiver *is* the object being printed, and a second one would be a free
function's argument list in a message's place.

### The sweep checks the name inside the arity sentence

`_ARITY` keeps exempting the shape. The sweep now reads the callee out of
it and fails unless:
- for a class receiver, it is that class's name;
- for an instance, it is the receiver's own class name, or `object` for a
  message `Object` defines, or the wrapper a program's subclass extends.

The sweep states that oracle independently of the implementation. It reads
the owner from the receiver's MRO and the names from `type(receiver)`, and
it runs over every sample with six arguments, which is what found the four
shapes.

## Risks / Trade-offs

- [A `TypeError` raised at binding by something other than arity, such as
  an unknown keyword (`got an unexpected keyword argument 'x'`)] → It
  carries the same `<qualname>()` prefix and benefits from the same rename.
  That is intended, and a test pins one case.
- [A program's class method shadowed by a mixin name] → The owner is the
  program's class, rule 1 applies, and its own qualname stands.
- [The rewrite changes the exception object a handler receives] → It
  becomes a mirror `TypeError` raised `from None`, as every POOP-worded
  failure is. `except_(TypeError, …)` matches it as before, and the chain
  report shows nothing under it.
- [Tests that pin today's wrong names] → Grep `tests/` for `object\.` and
  `bytes\.` arity strings while doing the rename task, and update them in
  the same commit.
