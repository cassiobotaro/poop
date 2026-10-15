# Design

## Context

See proposal.md — Why. The constraints that shape the fixes:

- Validators collect rather than raise; the three shared helpers
  (`NodeValidator`, `CallNameValidator`, `ShadowValidator`) cover a node
  table, a name set and a protected-name set. A `ClassDef` keyword and a
  dunder `def` are neither: `ast.keyword` also hangs off every `Call`, and a
  `FunctionDef` is refused by *name* only inside a class body, so both need
  a small `ErrorCollector` of their own.
- `BuiltinRewriter` sends a bare builtin name to `name_target`; the twelve
  constructors with a convert/build gap bind a `builtin_alias(...)` as
  `_poop_<name>_cls` and point `name_target` at it. `Slice` declares payload
  slots (`_start`, `_stop`, `_step`), which is all `_AliasMeta.__call__`
  needs to rebuild a converter's answer as a subclass.
- `Object.__getattribute__` ends in `self.does_not_understand(name)` with the
  raw `str` CPython handed it; `Object.does_not_understand` composes the
  refusal from it. `Error.does_not_understand` and `PoopMeta` have their own
  copies of the hook.
- `exceptions._build` makes every mirror a subclass of the native and of
  `Object`, cloaked; `_PYTHON_ATTRIBUTES` refusals are installed on the
  metaclass only, so an instance still resolves `args` through
  `BaseException`.

## Goals / Non-Goals

**Goals:**
- Every program in the proposal's list fails at validation with a POOP
  sentence, or runs and answers a POOP object.
- No existing example or test changes its answer.

**Non-Goals:**
- Rewording failures that already answer a POOP object (change
  `fix-wrapper-equality-and-errors`).
- A general "no dunder in a class body" rule: `__slots__` and `__doc__`
  assignments are `no_dunder_name`'s, and the operator slots are documented
  as legal.

## Decisions

- **Type parameters go in `no_type_alias`'s table**, not a new validator:
  `ast.TypeVar`, `ast.ParamSpec` and `ast.TypeVarTuple` are nodes
  `generic_visit` reaches, the message is one sentence, and the catalogue
  section already exists. The `[T]` spelling in the message is composed from
  the node (`*Ts`, `**P`), which means a small `_Visitor` subclass that
  formats rather than a static string — the table pattern allows a callable
  message or the row stays static with a generic `drop the [...]`; the
  spec asks for the spelled form, so the visitor formats.
- **`no_class_keyword` is its own validator**, after `no_decorator` in
  `DEFAULT_VALIDATORS` (class-definition machinery sits together). It reports
  one error per keyword, at the keyword's position, and spells `**name` for a
  `None`-arg keyword.
- **`no_dunder_def` carries a deny-list, not an allow-list.** An allow-list
  would refuse every operator slot not enumerated (there are forty), and the
  cost of missing one is a legal program refused; the cost of missing a
  deny-list entry is one more leak, which the wording sweep catches. The
  deny-list is the lookup, creation and descriptor protocols named in the
  spec; each row carries its own sentence so `__getattr__` can name
  `does_not_understand`. Placed after `no_class_keyword`.
- **`super()` in a lambda and `return <value>` in `__init__` extend
  `no_class_machinery`'s visitor**, which already tracks whether it is inside
  a class body and already special-cases `super`. A stack of enclosing
  function kinds (`def` vs `lambda`) is pushed as it descends.
- **`does_not_understand` receives `Str(name)`** at the one call site in
  `Object.__getattribute__`; `Object.does_not_understand`, `Error`'s and
  `PoopMeta`'s override read `str(name)` back, so the composed sentence is
  unchanged and the three built-in hooks keep their signatures. The
  type annotation becomes `Str`.
- **Exception instances get their instance side in `_build`**: `message`,
  `kind`, `raise_` and `__str__` are added to the namespace of the root
  mirror (`BaseException`'s), and the three natives are refused through an
  instance-level `__getattribute__` guard keyed on `_PYTHON_ATTRIBUTES`,
  reusing `_refuse_python_attribute` for the sentence. `Error` keeps wrapping
  a *caught* exception: a program never holds an `Error` it built, so the two
  surfaces do not collide. Alternative considered: make the mirror
  constructor answer an `Error` — rejected because `class Field(Exception)`
  then could not store fields on `self`.
- **`slice` binds `_poop_slice_cls = builtin_alias(Slice, _poop_slice_from,
  "slice")`** and `name_target` points at it; `no_builtin_shadow` already
  reserves the name, so no reservation changes.

## Risks / Trade-offs

- [The `__getattribute__` guard on exception instances slows every attribute
  read on an exception] → it is one dict lookup on a frozen set of five
  names, on a path that runs only when a program handles an error.
- [A program that defined `__getattr__` legitimately breaks] → no example
  does (`grep -rn "__getattr__" examples/` is empty); the message names the
  substitute.
- [`no_dunder_def`'s deny-list misses a slot] → `tests/test_no_python_wording.py`
  already sweeps a user class against every dunder it can spell; the new
  validator's test parametrises over `dir(object)` and asserts each name is
  either refused, in the documented legal set, or absent from the language.
