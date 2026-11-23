# 62. Lazy imports break cycles; performance is guarded structurally

Date: 2026-10-14

## Status

Accepted

## Context

The modules in `poop/types` import each other in real cycles. A hub (`object`, `meta`, `boolean`, `none`, `string`, `block`, `float`, `_bridge`) is needed at class-definition time by modules it would import: `boolean` inherits `_numeric_compare`'s mixin, `block` imports `Object`, `float` imports `int`. A proposal to hoist the deferred imports to module level was closed for that reason. Each deferred import was function-local, with a `# circular:` comment naming the edge it breaks.

A function-local import costs about 215 ns on 3.15 against about 20 ns for a module global. Counting the imports that fire while every example program runs (6294 across 43 programs) showed a handful carrying almost all of it: `Object.__getattribute__` importing `_MethodBlock` on every message sent (1809 fires), `Int._arith` importing `Float` on every operator (887), `_num_value` running three imports on every comparison between numbers (555 each), `print` two per line, the numeric `__eq__` two more.

The `2026-10-14-hot-path-imports` change answered first with a cached getter, `late(module, name)` (about 70 ns), at the hot sites, and, for the hottest one, a module global installed by `block.py`. That change had weighed the installed global as the fastest shape but one that couples `block.py` to another module's internals and depends on an import order nobody states, and adopted it only when the getter alone missed its gate. The `2026-10-14-lazy-imports` change then replaced all three mechanisms (function-local imports, `late()` getters, the installed global) with Python 3.15's `lazy import` (PEP 810): a module-level `lazy from poop.types.float import Float` runs the import on the first *use* of the name, inside a method body, when both modules exist, and the name is a plain global after that (about 30 ns). `sys.set_lazy_imports("all")` with a filter was rejected because it would hide the per-edge decision the code writes down.

The same changes, and `2026-10-14-object-hooks-off-the-hot-path`, measured their performance claims with one script in one session, best of five runs. A benchmark directory with a floor was rejected: CI timing noise would make it flap. Measurement has also reversed a choice once before: `PoopMeta` used to derive from `ABCMeta` for one class, `Boolean(Object, ABC)`, and every `isinstance` against a POOP class went through `ABCMeta.__instancecheck__`, 422 ns instead of 86, with a loop-heavy benchmark about a quarter slower (ADR 37).

## Decision

Every deferred import in the package is a module-level `lazy from ... import`, placed after the eager imports, with its `# circular:` comment on the line above. No eager import becomes lazy, since a class-definition-time dependency must stay eager. A name also imported under `if TYPE_CHECKING:` keeps only the lazy import.

Hot paths avoid the import where the class hierarchy already answers: `_num_value` reads `_order_value()`, the hook `_NumericCompareMixin` already declares, instead of importing the three rungs, and the numeric `__eq__` coerces first and asks for `Complex` only on the miss.

Performance is guarded by structure, never by timing in tests:

- Function-local imports are refused by ruff (`PLC0415`, no exemptions).
- `tests/test_no_local_imports.py` runs every example program under an import recorder and asserts that no `poop/`-internal import fires from inside a function, naming the file and line of one fired through `exec` or a transformer.
- A change made for speed records its before/after timings in its design, from one script in one session, against a stop or no-regression gate stated before the change is applied, as the three changes above did.

## Consequences

`poop/types/_late.py` and the installed global are gone; one mechanism of the language replaces them. The `# circular:` comment tells a later reader whether a lazy import may be made eager.

An `ImportError` on a lazy edge moves from startup to first use; the suite and the examples exercise every lazy edge, and the recorder test fails on a broken one.

Imports used only in annotations stay under `TYPE_CHECKING`. Timing is never asserted in CI; the guards are deterministic and fail on the exact line that regressed.
