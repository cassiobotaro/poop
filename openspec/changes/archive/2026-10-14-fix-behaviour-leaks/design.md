# Design

## Context

See proposal.md - Why. What each fix rests on, verified on the tree:

- `_IterableMixin.sum` folds with `total += item`; `List.__iadd__` extends in
  place, so the running total aliases the first element (or `start`).
  `functools.reduce` and `operator` are already imported in the module.
- `_SliceRewriter.call_args` inserts a `None` when `len(node.args) == 1`;
  an `ast.Starred` is one node, so `slice(*xs)` is folded as if it had one
  value. `_poop_slice_from` receives the expanded values and already refuses
  more than three.
- `Object.get_attr(self, name, *default)` forwards `*default` to
  `builtins.getattr`, which refuses a fourth argument in its own words;
  `PoopMeta.get_attr` reads `default[0]` and ignores the rest. `MISSING` in
  `poop/types/_sentinel.py` is the project's marker for an absent argument.
- `no_poop_prefix._Visitor.visit_arg` reports the parameter name and does
  not call `generic_visit`, so `node.annotation` is never visited.
- `_DictRewriter.visit_Call` folds `dict(a, k=v, **b)` into
  `_poop_dict_merge`; `VarargsTransformer.visit_Call` (declared later in the
  pipeline) now wraps every `**x` in `_poop_kwargs_from`, so a plain
  `_poop_dict_from(a, k=v, **_poop_kwargs_from(b))` is what every other
  call already compiles to. `_poop_dict_from` is cloaked as `dict`, so
  CPython's duplicate-keyword sentence names `dict()`.
- `Bytes.hex` passes `(str, bytes)` to `text_like`; `ByteArray.hex` passes
  nothing and converts a `bytearray`; `MemoryView.hex` is a third copy.
  `_BytesLikeMixin` is where the two byte wrappers share bodies.
- `_resolve_py_slice(start_or_slice, stop, step)` takes the `Slice` branch
  without looking at `stop` or `step`.
- `StrTransformer` wraps every `ast.Constant` whose value is a `str`,
  docstrings included; `ast.get_docstring(node, clean=False)` identifies the
  one to leave. `VarargsTransformer.visit_FunctionDef` splices its prologue
  at `body[:0]`.
- `_displaying_through` reads `getattr(sys, "ps1", None)` and restores by
  assignment, so an absent attribute comes back as `None`.

## Goals / Non-Goals

**Goals:**
- Each of the nine behaviors answers what the delta specs say, with a test
  per scenario.
- No new wording family: every refusal here is either an existing POOP
  sentence reused on a new receiver, or CPython's sentence under the cloaked
  name, which is what every message answers for wrong arity today.

**Non-Goals:**
- Rewording wrong-arity calls to messages in general (a separate theme).
- Any of the shared-helper refactors the review found; those are
  `share-type-helpers` and `trim-transformers-validators`.

## Decisions

- **`sum` through `functools.reduce(operator.add, items, total)`** rather
  than `total = total + item` in the loop: same semantics, and the reduce
  spelling is the one that cannot be "optimized" back to `+=` by a later
  reader. The first element still seeds the total when `start` is absent, as
  before.
- **The slice fold moves to `_poop_slice_from`**, not to a smarter rewriter:
  the rewriter cannot know how many values a `Starred` carries, and the
  converter already sees them all. With the hook gone, `BuiltinRewriter.
  call_args` is deleted and the `_registry.py` comment that orders
  `SliceTransformer` after `NoneTransformer` is dropped (the converter sees
  Python's `None` or POOP's `none` and `_coerce` handles both).
- **`get_attr(name, default=MISSING)`** on both sides. The instance side
  calls `getattr(self, raw)` or `getattr(self, raw, default)` by the marker;
  the class side keeps its `try/except AttributeError` and answers `default`
  when it is not `MISSING`. A third argument then reaches CPython's own arity
  check under the cloaked qualname, the shape every message already answers.
- **The dict fold is deleted, not fixed.** Fixing it would mean reimplementing
  CPython's keyword rules (string keys, no duplicates) inside
  `_poop_dict_merge`; deleting it lets the one general mechanism answer. The
  two refusals it exposes are CPython's and name nothing POOP bans: `keywords
  must be strings` is the sentence `_poop_kwargs_from`'s docstring already
  accepts for `f(**{1: 2})`, and `dict() got multiple values for keyword
  argument 'x'` names the message under its cloak. `_FrozenDictRewriter`
  becomes a plain `BuiltinRewriter` with no `visit_Dict` and no `_merge_call`.
  `_fold_parts` stays for the `{**a, "k": v}` display; `_pairs_call` is
  inlined since nothing overrides it.
- **One `hex` on `_BytesLikeMixin`**, using the `Bytes` body (`(str, bytes)`
  kinds); `MemoryView.hex` calls the same module-level function over its
  `_value`. The mixin docstring's list of what differs per class loses `hex`.
- **The mixed slice form is refused up front** in `_resolve_py_slice`, before
  either branch resolves, with the `#slice takes … — write …` shape the
  argument helpers use. The sentence quotes the two valid spellings so the
  reader is handed both.
- **`StrTransformer` skips the docstring position** by checking, in
  `visit_ClassDef`/`visit_FunctionDef`, whether
  `ast.get_docstring(node, clean=False)` is not `None` and leaving `body[0]`
  unvisited in that case. `VarargsTransformer` inserts at index 1 under the
  same test. Only the first statement is exempt: a later bare string is still
  a `Str`, as the spec says. The module is deliberately *not* exempt: the
  REPL runs each input as a module, so `"abc"` at the prompt and `:methods
  "abc"` would have evaluated a raw Python `str` (found by
  `tests/test_repl.py` on the first run), and a POOP program cannot read a
  module docstring anyway.
- **`sys.ps1`/`sys.ps2` restored by deletion** when absent before: the
  context manager records presence with a sentinel and `delattr`s on exit.
  `sys.displayhook` always exists and is restored by assignment as now.

## Risks / Trade-offs

- [A program relied on `dict(a, **b)` accepting a non-`Str` key] → It never
  could through `{**a, **b}` or `f(**b)`, and the display path is untouched;
  the spec scenario pins the new answer.
- [Removing the docstring wrap changes `--transformers-only` dumps that a
  test compares verbatim] → `tests/test_transformers/test_str.py` and
  `test_varargs.py` are updated with the specs' scenarios in the same group.
- [`hex` moving to the mixin changes the qualname CPython reports for a
  wrong-arity `hex` call from `bytes.hex()` to `object.hex()`] → The mixin
  is cloaked as `bytes` on purpose (`_BytesLikeMixin(_Mixin, name="bytes")`),
  so the qualname stays `bytes.hex()`; verified in the task.
