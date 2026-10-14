# Design

## Context

See proposal.md - Why. What the approach rests on, verified on the tree:

- `message.__get__(instance, owner)` binds through the entry
  (`function`/`classmethod`/`staticmethod`) and wraps in a `_MethodBlock`
  only when `instance is not None and type(bound) is MethodType`. A
  `staticmethod` binds to a plain function on both sides; a `classmethod`
  binds to a `MethodType` on both sides; a plain function binds to a
  `MethodType` off an instance and stays a function off the class.
- `PoopMeta.__getattribute__` refuses a class-side read when the value is a
  `FunctionType` and `_instance_only` says the entry is a plain method; a
  `_MethodBlock` is neither, so a wrapped classmethod passes through.
- `_MethodBlock._identity` casts `_fn` to `MethodType` and reads
  `__self__`/`__func__`; a plain function has neither.
- `_MethodBlock.__call__` is `self._fn(*args, **kwargs)` with no rewording,
  so the cloaked arity sentence (`str.maketrans() missing 1 required
  positional argument: 'x'`) is what a wrong call answers today and after.

## Goals / Non-Goals

**Goals:**
- Every public method read off a wrapper, from either side, answers a
  `_MethodBlock`, except the plain-method-off-the-class read that is refused.
- Equality and hashing hold for the new wraps as they do for the old.

**Non-Goals:**
- `get_attr`'s `Block` and its POOP arity wording (`block-arity`).
- Any change to how a block calls.

## Decisions

**1. The descriptor wraps on the shape of the bound result, not on the side.**
`message.__get__` answers `_MethodBlock(bound)` when `type(bound) is
MethodType` (instance method off an instance, classmethod off either side) or
when the entry is a `staticmethod` (bound is the plain function, either
side). A plain function entry read off the class stays the raw function, so
`PoopMeta.__getattribute__` refuses it as today. *Alternative*: wrap every
callable. Rejected: the class-side refusal reads `type(value) is
FunctionType`, and wrapping would silence it.

**2. `_identity` tolerates a plain function.** `(getattr(fn, "__self__",
None), getattr(fn, "__func__", fn))`: a bound method keeps its pair, a
staticmethod's function is its own identity, so two reads compare equal and
`str.maketrans == bytes.maketrans` is false (different functions). The
`cast("MethodType", ...)` and the comment that justified it go.

**3. The test in `test_message_descriptors.py` that pinned "a staticmethod
stays native as before" flips.** It was parity with the hook; this change is
the one that moves the line, so the assertion becomes "wraps", with the
reason.

## Risks / Trade-offs

- [A classmethod read off the class now answers a `_MethodBlock` where some
  internal caller expected a bound method] → the library calls classmethods
  through the alias or `cls.` inside methods (`wrapped_instance(cls, …)`),
  never by reading them as values; the full suite is the check.
- [`inspect.signature` on the new wraps] → `_params` reads `signature(self._fn)`,
  and a plain function or bound method both have one.

## Found during apply

`PoopMeta._reflected`, the class-side `get_attr`/`has_attr` read, went through
`type.__getattribute__` and so through the descriptor: once the descriptor
wrapped a classmethod off the class, `int.get_attr("from_bytes")` answered a
`_MethodBlock` with the method's cloaked arity sentence, and the three
`block-arity` scenarios that want `block expects 1 to 2 arguments, got 0` from
that spelling failed. `_reflected` now reads the MRO dicts and binds the raw
entry past a `message`, so reflection keeps answering the `Block` the spec
describes while the written read answers the `_MethodBlock`. The split the
proposal names as out of scope is therefore preserved, by one more line.
