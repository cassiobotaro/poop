# Design

## Context

See proposal.md — Why. Constraints the refactor works under:

- A wrong-arity message is reported from the function's `__qualname__`,
  which `cloak` sets per class. `sorted`, `min` and `max` are keyword-only
  on the mixin and already shared by every other collection, so removing the
  three overrides changes no qualname a program can see (the `_sequence.py`
  one-line-`def` argument applies to positional messages only).
- `BuiltinRewriter` subclasses declare `names`; `RESERVED_NAMES` chains
  `getattr(cls.rewriter, "names", ())`. `_ExceptionRewriter` is a plain
  `NodeTransformer` reading `MIRRORS` in `visit_Name`.
- `_AliasMeta.__call__` reads `_slots` off `alias.__dict__` and hands it to
  `_endow`, which reads `_converter` and `_empty` off the same dict itself.
- `tests/test_no_local_imports.py` warms every lazy edge by running all
  examples once, then records a second pass; the two passes sit in one test.

## Goals / Non-Goals

**Goals:**
- Every duplicated body named in the proposal exists once; every derived
  registry has no hand-kept exception.
- No message changes its answer or its sentence, except the validator
  sentences the proposal reworded, which change wording only.

**Non-Goals:**
- Behavior changes; a new validator helper beyond the four that exist.

## Decisions

- **`LiteralRewriter(ast.NodeTransformer)` in `_collection.py`** with
  `literal_node: ClassVar[type[ast.expr]]`, `literal_target: ClassVar[str]`
  and a `visit` that matches `type(node) is self.literal_node` and the
  `Load` context when the node has one (`getattr(node, "ctx", None)`); the
  per-file class becomes three attributes. `_LITERAL_KIND` is rebuilt from
  the registered rewriters at import. Alternative: generate `visit_<Node>`
  through `setattr` in `__init_subclass__` — rejected, a `visit` override
  reads the same and keeps the method visible to a reader.
- **`names = frozenset(MIRRORS)` on `_ExceptionRewriter`** and `visit_Name`
  reads `self.names`; the validator's union goes. The registry docstring's
  promise then holds for every rewriter.
- **Validator wording**: `Klass` for the class placeholder (the spelling
  `no_dunder_attribute` already uses, in three messages), `obj` for the
  instance; `<name>() is forbidden — …` for every `CallNameValidator`
  (`no_print` gains its parens); `… is forbidden — POOP offers no
  substitute` for the four definitive bans. Each reworded sentence changes
  in its validator, its test, `INFECTIONS.md`, `README.md` and the REPL
  `:explain` test in one commit per validator.
- **`no_comprehension.messages`** is a dict comprehension over
  `((ast.ListComp, "list comprehensions"), …)` with one f-string tail.
- **Tests**: `EXAMPLE_FILES` in `_support.py` is a sorted tuple with
  `ids=` derived from the relative path; the import-recorder test warms the
  edges in a `module`-scoped fixture and parametrises the recorded pass so
  one failure names one program; `test_repl.py`'s bare `Repl(Interpreter())`
  calls become the fixture, and `_indent_for`/`_value_text` cases become
  two `parametrize` tables; `test_cli.py`'s three clean-diagnostic cases
  become one parametrised test over `(path_factory, expected_reason)`.

## Risks / Trade-offs

- [Removing `List.sorted` changes the answer's type] → it does not: the
  mixin already answers `List(...)`; the test module pins the type.
- [`LiteralRewriter` matches a `Store`-context list in a tuple-unpacking
  target] → the `Load` check is kept exactly as the three bodies had it;
  `tests/test_transformers/test_unpack.py` covers the targets.
- [A reworded validator sentence is quoted in a doc the test suite does
  not read] → `grep -rn` of each old sentence across `*.md`, `poop/`,
  `tests/` is part of each rewording task's verification.
