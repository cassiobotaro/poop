# Design

## Context

See proposal.md, *Why*. Three decisions with a real alternative are recorded
as ADRs (tasks 1.1 to 1.3): `await` is the message `await_()`; an async
method answers a `Coroutine`; `Async` is a class named after the keyword,
not a mirror of `asyncio`. This document keeps what is specific to the
change.

What the code does today, read for this design:

- `no_async` refuses `AsyncFunctionDef` and `Await`. `no_free_functions`
  already treats an `async def` in a class body as a method and refuses one
  anywhere else, so lifting the `AsyncFunctionDef` row is enough to admit
  async methods.
- `ReturnTransformer`, `VarargsTransformer` and `StrTransformer` define
  `visit_FunctionDef` only, and `no_dunder_name` does too. Every other
  validator that reads functions already handles both node types.
- `no_dunder_def` is a deny-list, so `__aenter__` and `__aexit__` already
  pass; what it lacks is a rule about which dunders may be async.
- `PoopMeta.__new__` already walks every public function of a class body to
  install its `message` descriptor (ADR 41).
- `DEFAULT_NAMESPACE` is merged from `_BINDING_SOURCES`, and the protected
  set of `no_namespace_shadow` is derived from it.
- On 3.15.2, `asyncio.run`, `asyncio.gather` and `await` all accept an
  object whose only protocol is `__await__`. That was run, not assumed.

## Goals / Non-Goals

**Goals:**
- No raw coroutine ever reaches a program, whichever way the method is
  reached: a send, `super()`, `get_attr`, or an `async def __call__`.
- Wrapping costs nothing on a send that is not to an async method.

**Non-Goals:**
- Making a block awaitable. A lambda cannot be async in Python, and the
  specs answer that with "the block answers the coroutine".

## Decisions

1. **The coroutine function is replaced in the class namespace, before the
   `message` descriptors are built.** `PoopMeta.__new__` asks
   `inspect.iscoroutinefunction` once per entry and swaps each one, dunders
   included, for a synchronous function (`functools.wraps`) that answers
   `Coroutine(fn(*args, **kwargs))`. The descriptor then wraps that function
   as it wraps any other.
   *Alternative:* wrap in `message.__get__` or `_MethodBlock.__call__`. That
   puts a test on every send, the cost ADR 41 measured at +81% on the
   central operation, and it misses `super().m()` and `async def __call__`,
   which never pass through a `message`.
   Found while implementing: CPython's own "never awaited" warning cannot be
   emitted for a program's coroutine, since it imports through the frame's
   builtins and a program's hold no `__import__`. `Coroutine.__del__` emits
   the same warning from library code and closes the raw coroutine.

2. **`Coroutine` holds the raw coroutine in a slot and defines `__await__`
   only.** It is cloaked as `coroutine` and prints as `<coroutine>`, the
   shape of `<block>`. Its single-use failure is CPython's own, raised from
   the delegated `__await__`, and matched by the `RuntimeError` mirror
   through `__instancecheck__` (ADR 35).

3. **`AwaitTransformer` runs first in `_TRANSFORMER_CLASSES`.** The rewrite
   is purely syntactic, over the call the program wrote:
   `Call(Attribute(v, "await_"), [], [])` becomes `Await(v)`. Running first
   means no other transformer has to recognise `await_` in a call it has
   already rewritten, and the literal transformers still descend into
   `Await.value`. It has no bindings.

4. **`no_misplaced_await` keeps a stack of the enclosing function nodes**
   (`FunctionDef`, `AsyncFunctionDef`, `Lambda`) and judges each
   `Attribute` named `await_` by the top of the stack and by whether it is
   the `func` of a `Call`. It sits right after `no_async` in
   `DEFAULT_VALIDATORS`, so `await x` and `x.await_()` misplaced in the same
   program report in source order of their causes. It is one validator for
   one selector, which is why the reserved `def await_` lives there and not
   in `no_dunder_def`.

5. **`Async` is a POOP class whose messages are `staticmethod`s, and whose
   `__init__` refuses.** Read off the class, a `staticmethod` already
   answers a `_MethodBlock` (ADR 41), so no `class_side` machinery is
   needed: `Async` has no instance side to keep apart. Each message checks
   its arguments' kinds at the send, before any coroutine exists, so a
   wrong kind fails where it was written. `sleep` and `gather` build their
   coroutine from a private `async def` and answer it as a `Coroutine`.
   "Can be awaited" is `inspect.isawaitable`, which a `Coroutine` satisfies
   through `__await__`.

## Risks / Trade-offs

- **[Recursion depth]** ADR 61 sizes the recursion limit by frames per
  send, and an awaited send adds the coroutine's frame and the wrapper's
  `__await__`. → Task 4.3 runs a recursive async method at the depth
  `tests/` already uses for a synchronous one, and records whether the
  limit needs a separate factor.
- **[The warning prints late]** CPython emits "never awaited" when the raw
  coroutine is collected, which can be after later output. → Accepted; the
  spec pins the text, not its position.
- **[A timing test]** The *Concurrently* scenario measures time. → The
  test gathers three `Async.sleep(0.1)` and asserts under 0.25 s, a margin
  wide enough for CI.
