# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 62–75 come from one review of `poop/` as Python code rather than as a
language: what a Python engineer would change about how the interpreter is
written. Two of them (62, 63) turned out to be behaviour, and lead for that
reason; the rest are ordered roughly by how much code each one touches.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues while the backlog has open items; the next one is 76.
Once every item has been implemented and deleted, numbering starts over at 1.

### 64. 158 of the 298 function-local imports break no cycle

`CONTRIBUTING.md`: "All imports live at the top of the module. Use a
function-local `import` only to break a circular import." `poop/` holds 298
function-local imports of its own modules. Building the module-level import
graph and asking, for each one, whether its target already reaches the
importing module, says 158 of them could be hoisted together without closing
a cycle. The sharpest cases import the module at the top *and* inside the
function:

```python
# poop/types/_iterable_mixin.py
from poop.types._argument import MISSING          # line 19, module level

    def do(self, block=MISSING):
        from poop.types._argument import a_block  # and again in map, filter,
                                                   # filter_false, find, reduce,
                                                   # all and any
```

`reduce` re-imports `MISSING` itself, shadowing the module-level name with the
same object. `bytes.py` has 21 such imports and none closes a cycle today;
`float.py` 16 and none; `string.py` 17 of 19. Sixteen modules also import
`to_boolean` at runtime at the top and then again under `if TYPE_CHECKING:`
(ruff `TC004`).

The 140 that remain are real, and concentrated: `meta.py` (44) and `object.py`
(39) sit under everything, so the root's protocol cannot name `Boolean` or
`Str` at import time. Those should stay — but only three sites in the whole
package say so (`# circular: block imports Object`), so a reader cannot tell a
load-bearing lazy import from a habitual one.

Two pairs are free one way only: `float → int` (12 sites) and `int → float`
(8) each hoist alone and form a cycle together, so the hoist is a set to pick,
not a search-and-replace.

**Fix.** Hoist the 158, drop the 16 duplicate `TYPE_CHECKING` imports, and turn
on ruff's `PLC0415` so each survivor carries a `# noqa: PLC0415` naming its
cycle. Trialled for `_iterable_mixin.py` (the eight `a_block` imports and
`_sorted`'s `a_key` hoisted): suite and `ty` pass. The per-call cost is small
but not zero — every `xs.do(…)` and `xs.map(…)` runs an import statement
before it does anything — and the rule in `CONTRIBUTING.md` would become one
the linter holds.

---

### 66. Sixty-one of the 71 validators are the same anonymous class

```python
>>> Counter(type(v).__qualname__ for v in DEFAULT_VALIDATORS).most_common(3)
[('make_call_name_validator.<locals>._Validator', 38),
 ('make_node_validator.<locals>._Validator', 16),
 ('make_op_validator.<locals>._Validator', 7)]
```

The three factories build a *class* per configuration, and every one of those
classes is then instantiated exactly once, with no arguments, in
`DEFAULT_VALIDATORS`. A class whose only variation is closed-over data is an
instance wearing a class's clothes: `NoLenValidator` and `NoAbsValidator`
differ by a frozenset and a string. Two of the factories also assemble their
visitor with `type("_Visitor", (ErrorCollector,), {f"visit_{…}": fn})` to get
per-node-type dispatch that a dict lookup in `visit` gives directly.

The hand-written validators have the mirror-image problem. Each repeats

```python
class NoSubscriptValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_NoSubscriptVisitor(), tree)
```

— ten times, seven of them with a zero-argument visitor — where the
transformers, one package over, say the same thing as data:
`rewriter = _ListRewriter`. And `CollectingValidator.collect` raises
`NotImplementedError` instead of being abstract, so a subclass that forgets it
fails at the first program rather than at import.

**Fix.** Ordinary classes taking their configuration in `__init__` —
`CallNameValidator(forbidden, message)`, `NodeValidator(messages)`,
`OpValidator(node_type, messages, allow=…)` — so `NoLenValidator =
CallNameValidator({"len"}, "…")` is an instance with a real type and a useful
`repr`; `forbidden` becomes a plain attribute, which is what `:explain` already
reads through `getattr`. `CollectingValidator` gains a `visitor: ClassVar`
defaulting `collect`, as `BaseTransformer.rewriter` does, and becomes an `ABC`.
The three validators that hand arguments to their visitor keep overriding.

Out of scope, but worth deciding once: the 38 call-name validators are 38
modules and 38 imports for what is a `dict[str, str]` of name → message. One
table would also make validation one walk instead of 71 (11.8 ms against
0.13 ms for a single `ast.walk` on `examples/patterns/interpreter.py`), at the
cost of the one-file-per-infection convention `CONTRIBUTING.md` teaches.

---

### 67. Ten rewriters carry one `visit_Call`, and a docstring defends a difference that is gone

`_forwarding.py` explains why it exists: "This differs from `_collection.py`'s
`CollectionRewriter`, which guards on `not node.keywords and len(node.args) <=
1` and drops keywords — so these three need their own factory rather than
reusing it." Proposal 44 removed that guard. The two `visit_Call` bodies are
now the same but for `self.builtin` against a closed-over `builtin`, and so
are the two `visit_Name`s.

The same pair is written out by hand in `int.py`, `string.py`, `bytes.py`,
`byte_array.py`, `complex.py`, `memory_view.py` and `object.py`; `slice.py`
adds one line to it. Across `poop/transformers/` that is 48
`ast.copy_location(...)` calls and 56 hand-built `ast.Name(id=…, ctx=…)` nodes
for what is, almost everywhere, "this name, at that node".

Three smaller leftovers of the same history:

- `boolean.py` and `float.py` still guard on `not node.keywords`, with comments
  saying an unguarded rewrite answered `0.0` / `False` off the helper's
  default. True when written; both converters now open with
  `refuse_extra_arguments`, so either route ends at the same refusal
  (`float takes no keyword arguments — …`) and the guard only decides how many
  hops it takes.
- `_ClassRewriter` rewrites `object` / `Object` in a base list, with its own
  `("object", "Object")` tuple beside `object.py`'s `_OBJECT_NAMES`.
  `ObjectTransformer` rewrites both names in every position, base lists
  included — `_ObjectRewriter` alone turns `class A(object)` into
  `class A(_poop_object)` — so only the empty-bases branch does anything.
- `_ReturnRewriter.visit_FunctionDef` is a one-line call to
  `_rewrite_function`, which has no other caller.

**Fix.** One `BuiltinRewriter` base — what `CollectionRewriter` already is,
taking a set of names so `object` fits — subclassed by every constructor
rewriter; `make_forwarding_rewriter` and its docstring go. Two AST builders in
`base.py`, `name_at(id, node)` and `call_at(target, args, node, keywords=())`,
replace the `copy_location` boilerplate. `_ClassRewriter` keeps only the
implicit-base branch.

---

### 68. The CLI and the REPL each keep their own consoles and their own error printer

`cli.py` and `repl.py` both declare `_OUT = Console()` / `_ERR =
Console(stderr=True)`, and both define the same decision:

```python
if _ERR.is_terminal and not _ERR.no_color:
    _ERR.print(render_error(exc, source), soft_wrap=True)
else:
    …format_error(exc, source)…
```

— `cli._emit_error` through `typer.echo`, `repl._print_error` through
`_ERR.print`. `errors.py` was written so the two surfaces report alike; the
last step, choosing between its two renderers, is the part still duplicated.

`Interpreter` is built for injection — validators, transformers and namespace
are constructor arguments — and the REPL quietly ignores two of the three:
`Repl.__init__` copies `DEFAULT_NAMESPACE` rather than the interpreter's, and
`_EXPLAIN_CALLS` is computed at import from `DEFAULT_VALIDATORS`. So
`Repl(Interpreter(namespace=…, validators=…))` validates with the injected
set, runs against the default namespace, and explains the default bans.

Two methods on `Interpreter` are also thinner than their names:
`transform_source` is `return self._validate_and_transform(source, filename)`,
and `run_file` — its own copy of the `utf-8-sig` read and of the comment
explaining it — is called only from tests, since the CLI reads the file itself
to keep the source for the error gutter.

**Fix.** A `report(exc, source, console)` in `errors.py` owning the
terminal/plain choice, used by both front ends, with one shared console pair.
`Repl` takes its namespace and its explain topics from the interpreter it was
handed (say, an `interpreter.new_namespace()` and a public `validators`). Make
`_validate_and_transform` the public `transform_source`, and either have the
CLI call `run_file` or drop it.

---

### 69. `repl.py` imports `readline` in three functions and tracks one registration in a global

`readline` is absent on one platform, and the module handles that three times:
`_setup_readline`, `_save_history` and `_readline_input` each open with their
own `try: import readline / except ImportError`. Whether history saving has
been registered is a module-level flag flipped through `global
_history_saver_registered`.

The same file writes to stdout two ways: `_OUT.print(...)` for values, headers
and the banner, and bare `print(...)` eight times — each with a `# noqa: T201`
for a rule the project does not enable (item 75) — for usage lines, `:help`,
and `:explain` output. The two paths wrap differently and only one of them is
the console the module's own comment says "decides per destination".

Smaller, same module: `_meta` dispatches three commands through `if`/`elif`;
`run` saves and restores `sys.displayhook` by hand around a 65-line loop;
`try: … except FileNotFoundError: pass` is `contextlib.suppress`.

**Fix.** One guarded import at the top (`try: import readline` / `except
ImportError: readline = None`), with the three functions testing the name. The
saver registers itself once behind `functools.cache` rather than a `global`.
Every write goes through `_OUT`. `_meta` becomes a `dict` of command → bound
method, and the displayhook swap a small `@contextmanager`, which also lets
`run`'s body be read without its `try`/`finally` frame.

---

### 70. Twenty ordering methods and five `__rmul__`s are one method each

`Str`, `Bytes`, `ByteArray`, `List` and `Tuple` each write `__lt__`, `__le__`,
`__gt__` and `__ge__` out in full, and the four differ by one character:

```python
def __lt__(self, other: object) -> Boolean:
    if not isinstance(other, Bytes | ByteArray):
        return NotImplemented
    return to_boolean(self._value < other._value)

def __le__(self, other: object) -> Boolean:
    if not isinstance(other, Bytes | ByteArray):
        return NotImplemented
    return to_boolean(self._value <= other._value)
```

The pattern is already solved in-house: `_numeric_compare.py` writes each as
`return self._order(other, operator.lt)`. And `_ValueEqMixin` already holds
the two facts an ordering needs — `_eq_attr`, the payload to compare, and
`_eq_group`, which wrappers compare across.

In the same five classes `__rmul__` is a second copy of `__mul__`: the bodies
compile to identical bytecode in all five.

The duplication has a cost beyond lines. The `Bytes` comment above `__lt__`
records that ordering against `bytearray` was "the one operation on the pair
that did not" follow `==` and `+` — four methods had to be fixed in two
classes, and `_eq_group` already knew the answer.

**Fix.** An `_OrderedMixin` next to `_ValueEqMixin` generating the four from
`operator.lt` / `le` / `gt` / `ge` over `_eq_attr`, with the comparable test
the equality mixin already has; each generated function gets its `__name__`
set so `cloak` reports it under the right selector. `__rmul__ = __mul__` in the
five classes. `functools.total_ordering` is not the tool: it answers `bool`,
and POOP's comparisons answer `Boolean`.

---

### 73. A shadowed builtin is reached five different ways

POOP's wrappers define methods named `print`, `hash`, `repr`, `len`, `sorted`…
so the modules that hold them need another route to the real builtin. There
are five:

```python
import builtins                                   # object.py, string.py, dict.py
import builtins as _builtins                      # int.py, float.py, boolean.py, …
from builtins import print as _builtins_print     # object.py, list.py, tuple.py
from builtins import hash as builtins_hash        # meta.py — four separate statements
_bytes = bytes  # alias to avoid shadowing by Bytes class name in annotations
```

`meta.py` and `object.py` each use two of them in one file. Nine modules carry
the last form (`_dict`, `_set`, `_tuple`, `_slice`, `_bytes`, `_list`, `_str`,
`_float`, `_int`), and the reason given does not hold as written: a class named
`Bytes` cannot shadow `bytes`, and none of the nine classes defines a method
with the builtin's name. Trialled on `bytes.py` — alias deleted, `_bytes` →
`bytes` — the suite and `ty` pass.

`poop/transformers/__init__.py` has the one real shadow, and it is
self-inflicted: importing the submodules `dict`, `list` and `object` binds
those names in the package namespace, so the file opens with three `from
builtins import (dict as _dict, …)` blocks and writes `_list[type[…]]`
throughout.

**Fix.** One convention — `import builtins` and qualified `builtins.print(…)`
at the call site, which is greppable and needs no alias table — and delete the
module-level aliases wherever removing them leaves `ty` green. Move the
registry (`_TRANSFORMER_CLASSES`, `_merge_bindings`, `DEFAULT_NAMESPACE`) out
of `__init__.py` into `poop/transformers/_registry.py`, where no submodule
shadows anything, and re-export the three public names.

---

### 74. `_bridge.py` is two `isinstance` ladders with the complexity check switched off

`to_python` and `to_poop` are nine and thirteen `if isinstance(…): return`
rungs, each under a `# noqa: C901 — flat isinstance ladder, one branch per
primitive/container`. The comment is accurate, and it describes a dispatch
table. (The one on `to_python` no longer suppresses anything — `RUF100`
reports it unused.) The ladders also depend on rung order in a way nothing
states: `bool` must be tested before `int` because it is a subclass, and a new
wrapper is added by finding the right height in two functions.

**Fix.** `functools.singledispatch` for both directions, one registered
function per type. Dispatch follows the MRO, so `bool` beats `int` without
anyone ordering it, the pairing of the two halves becomes two adjacent
`register` blocks per type, and the `noqa`s go because there is no branchy
function left to excuse. `to_python` is on a warm path (`meta._adapted` calls
it for every non-native protocol answer), and `singledispatch` caches per
type, so the lookup is one dict hit.

---

### 75. Twenty-four `noqa` directives silence rules that are not enabled

`pyproject.toml` selects `E4`, `E7`, `E9`, `W`, `F`, `UP`, `I`, `C90`, `S`,
`ANN`, `PYI`. The code suppresses rules outside that set: `# noqa: T201`
eleven times, `BLE001` four, `N801` three, `PERF203` two, and `TRY301`,
`B015`, `PLR1702`, `PLR2004` once each across `poop/` and `tests/` — 24
directives, plus one `C901` that is enabled and no longer fires, by `ruff
check --extend-select RUF100`. Each records that someone considered the rule
and judged the line fine; none of those rules runs, so nothing checks the
lines that carry no comment.

Running the wider set over `poop/` says what it would have caught:

- `PLW1641` (`__eq__` without `__hash__`) — eight classes, four of them item
  62's bug.
- `PLC0415` (import outside top level) — item 64.
- `B905` — five `zip()` calls without `strict=`. Four are fine as they are;
  `_poop_dict_from_pairs` pairs its arguments with `zip(it, it)`, which drops
  an odd trailing element in silence where `itertools.batched(pairs, 2,
  strict=True)` would refuse.
- `RUF022` / `RUF023` — `poop.types.__all__` and four `__slots__` unsorted.
- `SIM102` / `SIM105` — two collapsible `if`s, one `contextlib.suppress`.
- `TC004` — the sixteen duplicate `to_boolean` imports of item 64.

One modernisation belongs with it: 24 of the 187 modules open with `from
__future__ import annotations`. On the required 3.14, annotations are already
evaluated lazily (PEP 649), so the import is redundant, and the other 163
modules show the package runs without it.

**Fix.** Add `B`, `SIM`, `BLE`, `T20`, `PLC0415`, `PLW1641` and `RUF` (for
`RUF100`, which keeps suppressions honest from then on) to `select`, fix or
annotate what they report, and delete the directives for rules the project
decides not to adopt. `N801` is the one to leave off deliberately: `class_side`
is lowercase because it is used as a decorator, and the three comments saying
so can become one line in the config.
