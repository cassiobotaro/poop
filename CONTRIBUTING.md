# Contributing to POOP

Thanks for your interest! POOP is a Python interpreter infected by Smalltalk —
the goal is that **every operation looks like a message sent to an object**.

This document is the canonical source for contributor workflow and conventions.
By participating, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting started

POOP requires Python 3.15 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/cassiobotaro/poop.git
cd poop
uv sync --dev
prek install                        # enable git hooks
uv run pytest                       # run the test suite
uv run poop examples/basics/hello_world.py # run an example
```

The pipeline is `parse → validate → transform → execute(namespace)`. Source files:

- `poop/parser.py` — wraps `ast.parse`
- `poop/validators/` — AST validators that reject forbidden constructs
- `poop/transformers/` — AST transformers that rewrite literals/calls into POOP types
- `poop/types/` — POOP types (`Object` is the root)
- `poop/executor.py` — compiles and executes AST in an injectable namespace
- `poop/interpreter.py` — orchestrates the full pipeline

Reference catalog of validators, transformers, and types:
[`INFECTIONS.md`](INFECTIONS.md). Open backlog: the active changes under
[`openspec/changes/`](openspec/changes/); closed ones are in its `archive/`.

## Workflow

### Atomic commits

One concern per commit — one validator, one type, one transformer, one bug fix.
Never group unrelated changes.

For multi-part work (e.g. a new validator + a new type + an example), split into
separate commits in dependency order.

### Confirm scope before multi-part plans

Open work that spans more than ~3 files or introduces a public-API change
deserves a quick alignment first: an OpenSpec change (`/opsx:propose`, which
writes its proposal, design and tasks for review) or an issue. The maintainer
may want only a subset implemented, which is what the task list is for.

### Pre-commit hooks

`prek install` registers the hooks defined in `.pre-commit-config.yaml`. They
run on every commit:

- `ruff check --fix`
- `ruff format`
- `ty check poop/ tests/`

A failed hook means the commit did **not** happen — fix the issue and create a
**new** commit. Do not `--amend` after a hook failure.

## Conventions

### Imports

All imports live at the top of the module. A circular import is broken by a
module-level **lazy import** (PEP 810, Python 3.15):

```python
# circular: float imports int
lazy from poop.types.float import Float
```

The import runs on the first *use* of the name, inside a method body, when
both modules exist; after that the name is a plain module global. Every lazy
import carries a `# circular:` comment naming the edge it breaks — a lazy
import with no cycle to break should be an eager one. A function-local import
is never written (ruff's `PLC0415` refuses it, with no exemptions), and
`tests/test_no_local_imports.py` runs every example program under an import
recorder to catch one that ruff cannot see.

Imports needed exclusively for type annotations go inside an
`if TYPE_CHECKING:` block at the top of the module — never function-local,
never alongside runtime imports. A name needed at runtime *and* in annotations
is one lazy import, not a lazy import plus a `TYPE_CHECKING` copy: the lazy
name resolves in annotations too, through `annotationlib`.

Why the hubs cannot simply import eagerly is worth knowing. `import
poop.types.boolean` at the top of `object.py` would *execute* `boolean.py`
right there — and `boolean.py` needs `Object` as a base class the moment it
runs, so importing `object.py` first would run `boolean.py` before `Object`
exists. Every hub in the package (`object`, `meta`, `exceptions`, `boolean`,
`none`, `string`, `block`) is needed at class-definition time by the modules
it would import, and the package `__init__` is empty on purpose, so any module
can be the first one imported. A deferred import is therefore the honest
spelling; before 3.15 the only one available was function-local, which cost a
Python-level import on every call (~215 ns against ~30 ns for the resolved
lazy name) and was written 272 times.

### Language

- OpenSpec artifacts under `openspec/` (proposals, designs, specs, tasks) are
  written in **English**, regardless of the language used in the conversation
  that produced them.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `INFECTIONS.md`, and `README.md` are
  also English.
- Code comments are in English.

### Examples must have a Smalltalk version

Every file in `examples/` must include the equivalent Smalltalk code in its
docstring, like this:

```python
"""
Smalltalk:
    Transcript show: 'Hello, World!'.
"""

"Hello, World!".print()
```

The Smalltalk version anchors the language design — POOP code should look like
its Smalltalk twin.

Place a new example in the subfolder that matches what it teaches:

- `examples/basics/` — language fundamentals (control flow, collections, classes
  with state).
- `examples/idiomatic/` — idiomatic POOP usage (method chaining, null-safe
  cascades, etc.).
- `examples/patterns/` — Sandi Metz / GoF object-oriented patterns.

### Use the actual current year

License files, copyright notices, dates, and similar references must use the
**actual current year** (not a placeholder, not the year the project started).

### GitHub Actions versions

When editing `.github/workflows/*.yml`, verify each action version is current
(do not pin to a years-old tag without a reason).

## Adding a new validator / transformer / type

Every infection follows the same pattern.

### A new validator (e.g. `no_foo`)

1. Create `poop/validators/no_foo.py`. Subclass one of the three shapes when
   it fits, setting its class attributes — `CallNameValidator` (`forbidden`,
   `message`) for a builtin name, `NodeValidator` (`messages`) for a node
   type, `OpValidator` (`node_type`, `messages`) for an operator. Otherwise
   subclass `CollectingValidator` (`poop/validators/base.py`) and set
   `visitor` to an `ErrorCollector`, or override `collect()` when the visitor
   needs arguments — never `validate()`, which the base derives by raising the
   first collected error. Collecting is the primitive because
   `--validators-only` reports every error, and a raise has already thrown
   away the rest of the walk.
2. Register it in `DEFAULT_VALIDATORS` (`poop/validators/__init__.py`).
3. Add tests under `tests/test_validators/test_no_foo.py`. A
   `CallNameValidator`'s mechanical contract (refusal, line number, method
   allowed, plain code passes) is covered by the shared parametrised
   `tests/test_validators/test_call_name.py`, so its own test file holds only
   what is specific to it.
4. Add an entry to `INFECTIONS.md` with a `Substitute` column pointing to the
   POOP equivalent. **Activate a validator only when the substitute exists** —
   blocking without offering an alternative breaks code without teaching.

### A new transformer (e.g. `foo`)

1. Create `poop/transformers/foo.py`.
2. Register it in `_TRANSFORMER_CLASSES` (`poop/transformers/_registry.py`), which
   builds `DEFAULT_TRANSFORMERS`. Declare any helper in a `BINDINGS` ClassVar —
   `DEFAULT_NAMESPACE` is assembled from those and refuses duplicate keys; do not
   write into it directly. Registration order is the transform order and is
   sometimes load-bearing (`SliceTransformer` after `NoneTransformer`) —
   comment the reason when it is.
3. Add tests under `tests/test_transformers/test_foo.py`.
4. Add an entry to `INFECTIONS.md`.

### A new type (e.g. `Foo`)

1. Create `poop/types/foo.py` inheriting from `Object` (or a relevant mixin),
   with the builtin's name as a class keyword — `class Foo(Object,
   name="foo")` — which is what cloaks the class under the name it answers
   to. Declare `__slots__`. Methods must return POOP types — never bare
   Python values.
2. Wire dunders (`__iter__`, `__add__`, …) to public Python-named methods
   (`iter()`, `__add__` is fine to keep, but new Smalltalk-style behaviour goes
   in a public method).
3. Add tests under `tests/test_types/test_foo.py`.
4. Add an entry to `INFECTIONS.md`.

### Method naming

Methods follow Python names, not Smalltalk names: `map`, not `collect`;
`filter`, not `select`. The exception is `do` (from Smalltalk `do:`) used for
iteration — `for` is a keyword, `for_each` is a Java/JS idiom.

## Closing a change

The backlog is the set of active changes under `openspec/changes/`. One change
per theme, one task per finding: an audit with twenty findings is one change
with twenty checkboxes in its `tasks.md`, not twenty changes. A change that
alters observable behavior carries delta specs; one that only touches tooling,
typing or docs declares `skip_specs: true`.

When a change is implemented:

1. Work through its tasks in atomic commits as described above
   (`/opsx:apply`), ticking each task as it lands.
2. Update `INFECTIONS.md` in the same commit as the code when the change
   touched validators, transformers, or types; the catalogue holds the *why*,
   the specs hold the *what*.
3. Archive it (`/opsx:archive`): delta specs sync into `openspec/specs/`, and
   the change moves to `openspec/changes/archive/<date>-<name>/`.
4. Commit the archive: `chore(openspec): archive <name>`.

Code, tests and docs cite commits, not change names: the git log is the
changelog, and the archive is the record of how a decision was reached.

## Pull requests

- Branch from `main`. Use a short, lowercase, hyphenated name
  (`feat/iterator-types`, `fix/list-append`).
- Open the PR against `main`. Title under 70 characters; details in the
  description body.
- Required before opening:
  - `uv run pytest` passes
  - `uv run ruff check` and `uv run ruff format` pass
  - `uv run ty check poop/ tests/` passes
  - For UI-facing changes (none today, but in the future): manual smoke test
- The description should explain **why**, not just **what**. The diff already
  shows what.
- Reference the OpenSpec change (`openspec/changes/<name>/`) if the PR
  implements one.

## Versioning

The project no longer publishes tagged releases: there are no git tags,
no GitHub Releases, and no release workflow. The `version` field in
`pyproject.toml` is informational — bump it when it makes sense, following
SemVer.

Commit messages still follow [Conventional
Commits](https://www.conventionalcommits.org/), which keeps the git log
readable and maps cleanly onto SemVer intent:

- `fix:` → patch (`1.0.0` → `1.0.1`)
- `feat:` → minor (`1.0.0` → `1.1.0`)
- `feat!:` / `BREAKING CHANGE:` → major (`1.0.0` → `2.0.0`).
- `docs:`, `chore:`, `refactor:`, `test:`, `style:` → no version
  bump.

The git log is the changelog — there is no `CHANGELOG.md` and no
GitHub Releases page.

## Testing

- Tests live next to their target: `poop/types/foo.py` → `tests/test_types/test_foo.py`.
- Verify expected values against actual language semantics before assuming the
  implementation is wrong (e.g. ascii repr quoting, inclusive vs exclusive
  bounds, `__radd__` requirements for `builtins.sum`).
- `examples/` is excluded from `ty`, and ruff skips `F821`, `ANN`, `PLW0108` and
  `ARG005` there, because example files are POOP programs rather than Python
  modules: they rely on names injected at runtime (`True` → POOP boolean,
  etc.), carry no Python annotations, spell every block as a `lambda` (the
  twin of Smalltalk's `[...]`, which ruff would inline into the bare-method
  spelling `INFECTIONS.md` keeps unidiomatic), and a `With.do` body may ignore
  the manager it is handed.
- `uv run pytest` enforces a 95% coverage floor (`--cov-fail-under=95` in
  `addopts`) — a run whose tests all pass still exits non-zero below it.
- To measure coverage of a single module in isolation, override the project-wide
  `--cov=poop` from `addopts` and waive the floor for that run:
  `uv run pytest tests/test_types/test_X.py --cov-config=/dev/null --cov=poop.types.X --cov-fail-under=0`.
  The default `addopts` reports a TOTAL percentage averaged across every module
  in `poop`, so a single-file run shows ~48% TOTAL even when the module itself
  is 99% covered — which would trip the floor. `--cov-config=/dev/null` does not
  waive it on its own: the floor lives in pytest's config, not coverage's.

## License

By contributing, you agree your contributions are licensed under the same
license as the project (see `LICENSE`).
