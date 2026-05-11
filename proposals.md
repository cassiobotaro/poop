# Proposals

## 1. Docs — `NoLoopsValidator` message predates Block

`poop/validators/no_loops.py:21` suggests:

```
(lambda: cond).while_true(lambda: body)
```

But `while_true` lives on `Block`, and the `BlockTransformer` wraps every lambda automatically — so the user-facing idiom in real POOP code is:

```
Block(lambda: cond).while_true(Block(lambda: body))
```

The current message technically works (because lambdas get wrapped), but it doesn't match how examples in `INFECTIONS.md` and `MIGRATION.md` write loops, and it leaves the reader wondering where `while_true` comes from.

**Proposal.** Update the message to spell out `Block(lambda: ...)`. Same pattern for `visit_For` if a `Block`-flavoured suggestion exists.

**Risk.** None — message-only.
