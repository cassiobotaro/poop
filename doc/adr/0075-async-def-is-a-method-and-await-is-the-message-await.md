# 75. Async def is a method and await is the message await_

Date: 2026-11-27

## Status

Accepted

Amends [9. A validator is activated only with its substitute, except definitive bans](0009-a-validator-is-activated-only-with-its-substitute-except-definitive-bans.md)

## Context

ADR 9 lists `async def` and `await` among the definitive bans. Its reason is that dropping the stdlib mirrors took `asyncio` with it, and `asyncio.run` was the only thing that could start a coroutine. Once POOP offers a way to run a coroutine, nothing else holds the ban.

An `async def` is a definition, not an operation, so ADR 7's question of whether a construct looks like an object receiving a message does not apply to it, as it does not apply to `def`. `await x` is different. It is a prefix keyword applied to an expression, the shape ADRs 7 and 27 refuse for `not x`, `-x` and `~x`, each of which has a named message. ADR 27 records chained comparison as the only construct allowed on ergonomics alone. The prefix form also reads inside out when awaits are chained: `(await (await c()).get(u)).json()`.

A method named `await` cannot be written. `await` is a keyword, so `x.await()` fails to parse before any validator runs.

A lambda cannot be async in Python, and `lambda: await x` is a `SyntaxError`. POOP's control flow is made of blocks (ADR 28), so no spelling of `await` can appear inside an `if_true` or a `do` block.

## Decision

We will accept an `async def` that is a direct statement of a class body as a method, under the same rule ADR 68 gives `def`. Everywhere else it stays refused as a free function.

We will keep `await x` refused, as an ordinary ban whose substitute is `x.await_()`. The trailing underscore is how POOP already spells a message named after a keyword (`and_`, `except_`, `raise_`). A transformer rewrites `x.await_()` to `await x`, because a method cannot suspend the coroutine that sent it. Only the frame that executes `await` can.

We will refuse, before the rewrite, every use of `await_` it cannot honour: one whose nearest enclosing function is not an `async def` (module level, a synchronous method, a block), one sent with arguments, one read without being sent, and a method named `await_`, which the rewrite would never reach. The refusal keeps CPython's sentence, `'await' outside async function`, and adds where to send it.

## Consequences

`async def` and `await` leave the list of definitive bans. `await` follows ADR 9's ordinary rule, refused with the substitute named.

Awaits chain left to right, as every other message does: `self.client().await_().get(u).await_()`.

A block cannot await. It answers the coroutine, and the method awaits that answer: `flag.if_true_if_false(lambda: self.a(), lambda: self.b()).await_()`. A sequence of awaits that depends on a loop is written as recursion over async methods.

`await_` becomes a reserved selector. A program cannot define a method by that name.

Without the validator, a misplaced `await_()` would surface after the rewrite as a raw CPython `SyntaxError` about an `await` the program never wrote.
