# Proposal

## Why

`ty` is locked at 0.0.87 while 0.0.107 is out, and the dependency pass of
2026-11-22 (`3374de4c`) had to hold it back: the new release renames five
rules the tree names and reports four errors the old one did not. Two of
those errors are one real bug. `Tagged.raise_(cls="x")` answers `TypeError:
Tagged.raise_() got multiple values for argument 'cls'`: the class-side
`raise_` hands its keywords to the exception's fields, but its own receiver
parameter takes the name `cls` away from every program's exception class,
and the refusal names a parameter the program never wrote.

## What Changes

- **`ty` 0.0.87 → 0.0.107**, floor raised to the locked version.
- **Five renamed rules follow their new names** in `pyproject.toml`, in the
  `ty: ignore[...]` comments of `poop/errors.py`,
  `tests/test_types/test_block.py` and `tests/test_types/test_meta.py`, in
  two `type: ignore[...]` comments in the suite, and in
  `.github/copilot-instructions.md`:
  `invalid-method-override` → `incompatible-method-override`,
  `unresolved-attribute` → `missing-attribute`,
  `invalid-mutable-override` → `incompatible-mutable-override`,
  `invalid-return-type` → `invalid-explicit-return`,
  `call-non-callable` → `not-callable`.
- **The class-side `raise_` takes its receiver positionally**, on
  `PoopExcMeta` and on its refusing twin on `PoopMeta`. Every keyword a
  program writes, `cls` included, now reaches the exception's constructor
  (or the refusal `A cannot be raised — only a class descending from
  Exception can`). This is the fix `ty` 0.0.106 asks for: a function whose
  receiver can also be passed by keyword does not satisfy the `_Message`
  protocol once `**kwargs` is in play.
- **`sum` binds its result gradually**, as it already binds its running
  total, so `functools.reduce` is no longer solved against `Object`, which
  declares no `+`. No change in what `sum` answers.
- **One test narrows before it sends**:
  `test_a_class_answers_its_superclass_as_a_class_not_a_name` holds the
  answer of `superclass()` in a name, so the identity assertion narrows
  `PoopMeta | NoneClass` for the `name()` that follows.

Out of scope, and why: `self` as a keyword on an instance-side message (a
program's own `__init__(self, ...)` is the program's signature, and `ty`
reports nothing there); widening the suite's `ty` override to
`missing-union-attribute` (one site, and not a block, which is what the
override is for); the other dependencies, bumped in `3374de4c`; any new
`ty` rule that is off by default.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `class-side`: adds the requirement that `raise_` on a class keeps no
  keyword for itself, so a field named `cls` arrives by keyword like any
  other.

## Impact

- `pyproject.toml` (the `ty` floor, two rule names), `uv.lock`.
- `poop/types/exceptions.py`, `poop/types/meta.py`: one `/` each in the
  `raise_` signature.
- `poop/types/_iterable_mixin.py`: `sum`.
- `poop/errors.py`: two ignore comments.
- `tests/test_types/test_exceptions.py` (two new tests),
  `tests/test_types/test_meta.py`, `tests/test_types/test_block.py`,
  `tests/test_message_descriptors.py`, `tests/test_types/test_object.py`.
- `INFECTIONS.md` (the `raise_` paragraph), `.github/copilot-instructions.md`.
- No new dependency. Closes Dependabot PR #86.
