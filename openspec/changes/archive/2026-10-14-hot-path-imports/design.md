# Design

## Context

See proposal.md - Why. What the approach rests on, verified on the tree:

- The cycles are structural. `boolean.py` imports `_NumericCompareMixin` to
  inherit it, so `_numeric_compare.py` cannot import `boolean` at module
  level; `block.py` imports `Object`, so `object.py` cannot import `block`;
  `float.py` imports `int.py`. Every local import carries a `# circular:`
  comment naming its edge, and the closed proposal to hoist them was right.
- `_NumericCompareMixin` already declares `_order_value()` as "the raw
  Python number behind `self`, supplied by each rung", and `Int`, `Float`
  and `Boolean` all implement it. `_num_value` re-derives the same number by
  importing the three classes and testing them in order.
- `functools.cache` on a zero-argument function is a C-level
  `lru_cache` hit after the first call, measured at roughly 50 ns on 3.15;
  a function-local `from x import y` is roughly 215 ns (the `IMPORT_NAME`
  and `IMPORT_FROM` opcodes go through `__import__` and `sys.modules`); a
  module global is roughly 20 ns.
- The import counter (patching `builtins.__import__` and reading the
  caller's frame) is what produced the ranking in the proposal and runs in
  under a second over all examples. Baseline micro-timings on this machine,
  best of five, 20 000 iterations: `Int < Int` 3744 ns, `Int == Int` 4199,
  `Int + Int` 3062, `Int * Float` 3727, `an_int(Int)` 1609, `(5).abs()`
  3805, `List.at` 4690, `Str.len` 4921.

## Goals / Non-Goals

**Goals:**
- No `poop/`-internal import fires on the hot paths: a message send, the
  numeric comparisons and arithmetic, `print`, the argument guards.
- Zero change in behavior or wording; the suite and the wording sweep pass
  untouched.
- The line between "hot, bind late" and "cold, import locally" is written
  down with the measurement behind it, so the next contributor knows which
  to write.

**Non-Goals:**
- Hoisting imports to module level, or restructuring the hub modules.
- Asserting timings in CI.
- Touching cold sites.

## Decisions

**1. `_num_value` reads the hook the mixin already has.** `isinstance(other,
_NumericCompareMixin)` then `other._order_value()`, else `NOT_NUMERIC`. No
import, no rung order, and `Complex` stays out because it never joined the
mixin (it has no ordering). *Alternative*: `singledispatch` registered from
each rung's module, as `_bridge.py` does. Rejected: it is a second
registry for a fact the class hierarchy already states, and its dispatch
(~100 ns) is slower than one `isinstance` on a shared base.

**2. The numeric `__eq__` tests the mixin before importing `Complex`.** The
order flips: coerce through `_num_value` first; only on `NOT_NUMERIC` ask
whether `other` is a `Complex` (late-bound). `Int == Complex` and
`Complex == Int` keep their answers, since `Complex.__eq__` is unchanged and
CPython's reflected lookup still runs it. *Alternative*: make `Complex`
join the mixin for equality only. Rejected: the mixin's docstring says why
it does not, and the docstring is right.

**3. One helper, `late(module, name)`, for the remaining hot sites.** It
answers a zero-argument getter wrapped in `functools.cache`; the module
is imported and the attribute read on the first call and never again.
Call sites read `_method_block = late("poop.types.block", "_MethodBlock")`
at module level and `_method_block()(value)` inside the function. The
getter is typed through a `TYPE_CHECKING` import of the real name and a
`cast`, so ty keeps checking the call. *Alternatives*: a module global
assigned by the dependent module on import (fastest, ~20 ns, but it
couples `block.py` to `object.py`'s internals and depends on import order
nobody states); `importlib.import_module` inline (no faster than the
import it replaces); `sys.modules[...]` reads (same cost, and crash
before the module loads). The cached getter is the one that is both
faster and order-independent. If the profile later shows the ~50 ns on
`__getattribute__` matters, the global pattern is the documented next step.

**4. The guard counts imports, not nanoseconds.** A test patches
`builtins.__import__`, runs each hot operation a few times after a warm-up,
and asserts that no import whose caller is a function under `poop/` fired.
It is deterministic and fails on the exact line that regressed. The timing
comparison runs once, in this change, with the same script and session as
the baseline, and lands in this file under *Measured*. *Alternative*: a
benchmark directory with a floor. Rejected: CI timing noise would make it
flap, and the repository has no benchmark convention to join.

**5. `_argument` keeps its local imports of wrapper classes; only the
`_unwrap` ones bind late.** `a_needle`, `a_mapping` and `translation_table`
import `Str`, `List`, `Dict`-family classes, but they are the refusal-side
guards of a few messages and fired five times across all examples. The six
`_is_absent` / `_searched` imports are on `an_int`, `a_fill`, `bytes_like`,
`byte_order`, `a_number`, which every optional-argument message reaches;
those bind late.

## Risks / Trade-offs

- [A late getter is called before its module can import, at class-definition
  time] → the getter runs only inside method bodies, never at module level;
  `test_late.py` asserts a getter built for a not-yet-imported module
  resolves on first call.
- [The `__eq__` reorder changes an answer for a foreign operand] → the miss
  path is unchanged (`false`), and `tests/test_types/test_complex.py` and
  the numeric-tower tests pin every cross-rung pair; the wording sweep
  runs the operator table over every receiver pair.
- [The gain is smaller than estimated] → the after-measurement is a task;
  if `Int < Int` and `Int == Int` do not improve by at least 20 % and a
  message send by at least 10 %, stop and report before archiving rather
  than keep a refactor that bought nothing.
- [Someone writes a new local import on a hot path] → the counter test
  names the file and line.

## Measured

Same script, same session, best of five runs of 20 000 iterations, ns/op.

| Operation | Before | After | Change |
|---|---|---|---|
| `Int < Int` | 3806 | 3011 | -21 % |
| `Int == Int` | 4264 | 2482 | -42 % |
| `Int + Int` | 3059 | 2770 | -9 % |
| `Int * Float` | 3817 | 3435 | -10 % |
| `an_int(Int)` | 1644 | 1095 | -33 % |
| `(5).abs()` | 3935 | 3430 | -13 % |
| `List.at` | 4852 | 4375 | -10 % |
| `Str.len` | 4162 | 3491 | -16 % |
| `true.if_true` | 3049 | 2363 | -22 % |

The gates held: the two comparisons cleared 20 % and the message send 10 %.
The send only did so after decision 3's contingency fired: with the cached
getter alone `(5).abs()` measured 3726 ns against 3825 for the local import
(-3 %), so `_MethodBlock` is installed into `object.py` as a module global
by `block.py` (3430 ns, -13 %), the getter staying as the fallback for a
public method read before `block` has loaded.

The same experiment put a floor under a message send: 1646 ns with
`__getattribute__` doing no wrapping at all. The `_MethodBlock` wrap is
therefore about half the cost of every send. Out of scope here, recorded in
`INFECTIONS.md` as the next performance change if one is wanted.
