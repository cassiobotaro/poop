# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

---

### 1. The class side is invisible to `dir()` and `:methods`

**Severity: low (a documented surface no discovery tool shows).**

`dir(cls)` never merges the metaclass's names — CPython's `type.__dir__` walks
the class's own MRO only — so **none** of the class-side protocol appears in
POOP's introspection substitutes:

```bash
class Foo(Object):
    pass

Foo.dir().includes("name").print()        # -> False
Foo.dir().includes("superclass").print()  # -> False
ValueError.dir().includes("raise_")       # -> False
```

`INFECTIONS.md` already records the half of this that motivated the closure of
`mro` and `register` ("`dir()` never listed either name, so both were
unreachable by reading and reachable by typing") — but it recorded it about the
two names POOP *refuses*. The same gap hides the **26** it answers — `PoopMeta`
carries 28 `class_side` descriptors, and only `mro` and `register` are refusals:
`name`, `superclass`, `print`, `class_name`, `get_attr`, `is_instance`,
`assert_`, `if_none`, and the rest, plus `raise_`, a message on `PoopExcMeta`.
`:methods` reads the same `dir()`, so the REPL cannot show them either.

**Solution.** `PoopMeta.dir` (`poop/types/meta.py`) merges the `class_side`
descriptors found on `type(cls).__mro__` into its answer. The refusing ones
must not be listed — offering a name that answers "that is Python's, use
`superclass`" is worse than omitting it — which needs a way to tell a refusal
from a message. The cheap version is a set of names in `meta.py`; the honest
one is a flag on the descriptor (`class_side(fn, refuses=True)`, or a sibling
decorator), so a new refusal cannot be added and forgotten. Prefer the flag,
for the reason `_EXEMPT` in `test_mirrored_raises.py` gives about lists that
have to be kept in step by hand.

Tests under `tests/test_types/test_meta.py` (every answered class-side message
is listed; neither `mro` nor `register` is) and `tests/test_repl.py` (`:methods`
on a class shows them).
