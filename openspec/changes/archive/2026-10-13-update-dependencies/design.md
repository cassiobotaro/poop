# Design

## Context

See proposal.md - Why. What was verified on the current tree, read-only, with
the exact versions the lock would move to:

- `uv lock --upgrade --dry-run`: seven updates, listed in the proposal. No
  package is added or removed; the resolution stays at 18 packages.
- `uvx ruff@0.17.0 check` and `format --check`: clean on the whole tree.
- `uvx prek@0.5.5 validate-config .pre-commit-config.yaml`: valid; the `ty`
  hook runs under it.
- `uv run --with typer==0.27.3 pytest tests/test_cli.py tests/test_repl.py`:
  125 passed.
- `uvx ty@0.0.87 check poop/ tests/`: 15 diagnostics, exit 1 (11 errors, 4
  warnings). The pinned 0.0.70 reports none. Each is listed by family under
  Decisions, with the site it lives at.
- Dependabot's own log for the failing `uv` runs: "Currently, the following
  Python versions are supported in Dependabot: 3.10.*, 3.11.*, 3.12.*, 3.13.*,
  3.14.*". The project requires 3.15.
- Repository conventions that bind this: floors equal the locked version
  (`c2e2183`); `[tool.ty.rules]` already ignores one rule project-wide
  (`invalid-method-override`, for the `Boolean`-returning dunders) and the
  tree carries 64 line-level `# ty: ignore[...]` with a reason each; hooks run
  `ruff check --fix`, `ruff format` and `ty check` on commit.

## Goals / Non-Goals

**Goals:**
- Every declared dependency at its latest release, floors matching the lock.
- `uv run ty check poop/ tests/` clean under 0.0.87, by fixing sites rather
  than by muting a rule.
- The stale Dependabot pull requests closed, with the reason recorded where the
  next reader will look.

**Non-Goals:**
- Changing `requires-python` to let Dependabot run. 3.15 is the project's
  floor by design (AGENTS.md, README, the `frozendict`/`sentinel` mirrors).
- Removing the `uv` entry from `dependabot.yml`. Its weekly failure is noise,
  but the entry costs nothing and resumes unattended once 3.15 is supported;
  deleting it would need someone to remember to put it back.
- Adopting ruff 0.17's new rules beyond what `select` already turns on.

## Decisions

**1. One lock refresh, floors raised in the same commit.** `uv lock --upgrade`
rather than per-package bumps: the four Dependabot PRs each move one package
and are already behind (`ruff 0.16.9` vs `0.17.0`, `ty 0.0.84` vs `0.0.87`).
Floors move to the locked versions so that `uv sync` on any machine resolves to
what CI tested, which is the reason `c2e2183` gives.
*Alternative*: merge the four PRs and then bump the rest. Rejected: they
cannot be rebased by Dependabot (unsupported Python), and each would still
leave the toolchain short of latest.

**2. `_eq_group` / `_order_group` overrides keep the base's declared type.**
Eight sites write `_eq_group: ClassVar[str] = "bytes"` over a base
`ClassVar[str | None] = None`. ty's `invalid-mutable-override` is right that a
narrower type on a writable attribute is unsound in general. The attributes are
never written after class creation, but the honest fix is cheaper than a
suppression: annotate the overrides `ClassVar[str | None]`, matching the base,
so the readers (`_same_group` and its twin) keep narrowing with `is not None`
as they already do.
*Alternative*: `# ty: ignore[invalid-mutable-override]` on eight lines, or the
rule off in `[tool.ty.rules]`. Rejected: eight identical suppressions say less
than one matching annotation, and the rule catches real mistakes elsewhere.

**3. `ValidationError.lineno` / `col_offset` keep their narrowing, suppressed
with the reason.** `PoopError` declares `lineno: int | None` because a parse
error may have no position; `ValidationError` declares `int` because a
validator always has a node. The narrowing is a documented guarantee readers
may rely on, not an accident, so these two lines take
`# ty: ignore[invalid-mutable-override]` with that sentence, as the other 64
line-level ignores in the tree each carry theirs.
*Alternative*: widen to `int | None`. Rejected: it would turn a guarantee into
a check at every consumer.

**3b. The ty fixes and the bump land in one commit.** Found while applying: the pinned ty 0.0.70 does not know the rule name `invalid-mutable-override` and fails (`ignore-comment-unknown-rule`, exit 1) on the two suppressions decision 3 adds, while the new ty fails on the unfixed tree. Neither half passes the `ty check` hook alone, so groups 1 and 2 share a commit. The alternative that keeps two commits is widening `ValidationError` to `int | None`, which decision 3 rejects.

**4. `Block.__get__` casts the receiver once.** `partial(self, instance)` binds
an `object` to a block whose `ParamSpec` ty now checks; the block *is* called
with the receiver first (that is what `__get__` means), so a
`cast("Callable[..., R]", self)` at the one site states the binding and keeps
the docstring's reasoning (the receiver is bound onto the block, not `_fn`).
*Alternative*: type `instance` as `P.args`. Not expressible for a descriptor
receiving one positional.

**5. `@contextmanager` functions return `Generator[None]`.** typeshed
deprecated the `Iterator[T]` overload of `contextmanager`; `Generator[None]`
(3.13+ defaults for the other two parameters) is the replacement it names.
Three sites, each already importing from `collections.abc`.

**6. The sentinel test asserts what it means.** `assert Sentinel(Str("")).print`
asserts that a bound method is truthy, which is always true; the comment says
the intent is that an empty name is accepted as CPython accepts it. It becomes
`assert str(Sentinel(Str(""))) == ""`, which is the observable fact.

**7. Close the four Dependabot PRs with one comment each.** Each comment names
this change and the reason Dependabot cannot rebase them. Closing rather than
leaving: a stale PR that cannot be updated invites a merge of an old version
over the new lock.

## Risks / Trade-offs

- [ruff 0.17 or ty 0.0.87 behave differently under the hooks than under `uvx`]
  → the hooks run the locked binaries on the commit that introduces them; the
  full gate runs before and after `uv sync`.
- [A later ty release adds diagnostics again] → expected for a 0.0.x tool;
  the pattern here (fix at the site, suppress with a reason only for a
  deliberate narrowing) is what the next bump follows.
- [Dependabot opens new PRs that again cannot run] → until 3.15 is supported
  it opens none: the job fails before it reaches the resolver. The config stays
  so that it resumes on its own.
- [Coverage 7.16 changes line attribution and the 95% floor moves] → the
  floor has 4.95 points of headroom (99.95%); the full `pytest` run is in the
  tasks.
