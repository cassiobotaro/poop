# Tasks

Each ADR task is one commit, `docs(adr): <title>`, written with the `adr`
skill in the Nygard format of design decision 1 and checked against the
`INFECTIONS.md` lines it extracts. Line numbers below refer to
`INFECTIONS.md` at `ab9c32a2`; `arch:` is `openspec/changes/archive/`.

## 1. Inventory and open questions

- [x] 1.1 Write `openspec/changes/adopt-adr-log/inventory.md`: every ADR in group 3 with its source, its date per design decision 3 (`git log -S` for `INFECTIONS.md` paragraphs, archive prefix for `arch:` decisions) and its resulting number from `0002` in date order; verify every `###` heading of `INFECTIONS.md` appears either in the inventory or in the "reference only" list of task 4.1.
- [x] 1.2 Resolve the three passages that may be stale before extracting them, by running POOP: line 1254 (`Range.slice` answers `List`) against line 1139; line 1037 (a bare method attribute is a leak) against the `message` descriptor; lines 964-966 (`is_instance` takes raw classes) against the class side. Record each answer in `inventory.md`; the ADR states the current behaviour and the stale sentence is not carried over.

## 2. Open the log

- [x] 2.1 Add `.adr-dir` (`doc/adr`) and `doc/adr/0001-record-architecture-decisions.md`, the adr-tools seed verbatim, dated the commit day. Why POOP replaces `INFECTIONS.md` is the last ADR (3.65), dated the day it lands, so the log stays in date order.

## 3. Retroactive ADRs

### Principles (lines 9-57)

- [x] 3.1 Everything is an object; every operation is a message
- [x] 3.2 Message aesthetics decides whether a construct is infected
- [x] 3.3 Methods use Python names, not Smalltalk's (with `do`, `reduce`, and the single-receiver `math` functions of `arch:2026-10-22-float-answers-315-math`)
- [x] 3.4 A validator is activated only with its substitute; definitive bans (with `try/except*`, lines 107-109, and `import`/`open`/`async`/`input`, lines 131-160, 634-663)
- [x] 3.5 Every type represents itself through `__str__`, and a displayed value reads back as itself (line 48)
- [x] 3.6 `__slots__` on every POOP class, mixins included
- [x] 3.7 Every literal is transformed (with the docstring rule, lines 1309-1317, `arch:2026-10-14-fix-behaviour-leaks`)
- [x] 3.8 Every basic type has a POOP wrapper
- [x] 3.9 POOP methods answer POOP types (with `return none`, `*args` and unpacking, lines 985-991)
- [x] 3.10 Void mutators answer `none`
- [x] 3.11 `true`, `false` and `none` are singletons
- [x] 3.12 Constructor builtins are intercepted, not banned
- [x] 3.13 Dunders are exposed as plain methods
- [x] 3.14 Wrappers are mangled and cloaked as builtins (with reserved names derived from registries, lines 693-714)
- [x] 3.15 A bare builtin name is the converter alias

### Namespace and encapsulation

- [x] 3.16 Programs are confined to a builtins allow-list (582-599)
- [x] 3.17 Dunder access is banned by rule, at runtime too; `__init__` only on a `super()` receiver (529-580)
- [x] 3.18 Single-underscore internals are unreachable (675-691, 557)
- [x] 3.19 One `is_message` predicate serves every discovery surface (519-527)
- [x] 3.20 A class may not define lookup, creation or descriptor dunders (253-261, `arch:2026-10-15-close-raw-python-leaks`)
- [x] 3.21 Class machinery is accepted only where it was argued for (215-243, 820-826)
- [x] 3.22 A class is built from its bases alone (245-251, 263-270)

### Value types and equality

- [x] 3.23 Numeric equality follows CPython's numeric tower (846-850)
- [x] 3.24 `Boolean` stays outside `Int` and answers the int side (44, 852, 1016, `arch:2026-10-15-fix-wrapper-equality-and-errors`)
- [x] 3.25 Comparison rules live in `__eq__`, symmetric across subclasses (923, 933, same archive)
- [x] 3.26 No `id`: identity is a question (927, 339-343)
- [x] 3.27 `Range` stores an inclusive bound, decoded in one place, and reads its bounds by index (42, 561, 1139-1141; per 1.2)
- [x] 3.28 `FrozenDict` and `MappingProxy` are both kept (1438, 1451)
- [x] 3.29 Python 3.15's `sentinel` is wrapped faithfully (1449-1453, `arch:2026-10-22-adopt-315-idioms`)

### Exceptions

- [x] 3.30 Only the exceptions POOP can reach are mirrored (856-864)
- [x] 3.31 Mirrors match through `__instancecheck__`, with no translation layer (866-872)
- [x] 3.32 `raise_` is a class-side message, `raise_from` an instance one (872, 880, 1463-1471, `arch:2026-11-22-bump-ty`, `arch:2026-10-19-complete-exception-protocol`)
- [x] 3.33 Built exceptions have a POOP instance side (876, `arch:2026-10-15-close-raw-python-leaks`)
- [x] 3.34 `Error` wraps a caught exception and honours suppression (1162-1177, `arch:2026-10-19-complete-exception-protocol`)
- [x] 3.35 POOP raises a reachable failure only through a mirror, and the report names it (52, 882)
- [x] 3.36 `Try` answers values and `else_` receives the value; it checks both arguments where written (38, 1179-1198)
- [x] 3.37 `With` keeps the native protocol and passes POOP values; it checks both arguments where written (38, 1200-1222)
- [x] 3.38 The recursion limit is sized by frames per send (860)

### Diagnostics

- [x] 3.39 A diagnostic never names a banned construct; operator errors are reworded by a pinned regex (30, 796-804, 587-588)
- [x] 3.40 Arity refusals keep CPython's sentence and name POOP's class (34, 1031, `arch:2026-10-19-arity-names-the-receiver`, `arch:2026-10-19-arity-refusals-teach`)
- [x] 3.41 `does_not_understand` answers with layered hints (935-951)
- [x] 3.42 Wrong kinds are refused in POOP's words, wrong values in CPython's (563-565, 1341, 1405)

### Blocks and messages

- [x] 3.43 Every `lambda` is a `Block`; loops are messages to blocks (1018-1022, 1039)
- [x] 3.44 `and_` and `or_` take blocks (118-125)
- [x] 3.45 Binary operators stay, unary ones go; chained comparison is allowed on ergonomics (816-844, 129)
- [x] 3.46 The `message` descriptor is installed at class build; method blocks wrap on the bound result; a method is a block whichever way it is read (32, 929, 1033, `arch:2026-10-14-object-hooks-off-the-hot-path`, `arch:2026-10-14-method-blocks`; per 1.2)
- [x] 3.47 The class side is data descriptors on a `type` metaclass and refuses instance messages (36, 884-917, 964-966; per 1.2)
- [x] 3.48 Substitutes mirror the full builtin signature; accessors are methods (1073-1104, 382-398, 429, 559, 774, 1156, 1272, 1421)
- [x] 3.49 `Str.format` is the only template surface (278-289, 444-452, 1341, `arch:2026-10-14-text-mirrors-complete`)

### Strings and bytes

- [x] 3.50 Text codecs are limited to four encodings, constructors included (40, 1339, 864)
- [x] 3.51 `Bytes` and `ByteArray` share a mixin cloaked as `bytes` (1403-1409, 565, 127)
- [x] 3.52 `MemoryView` is a one-dimensional byte view that answers `index` and `count` (46, 1419-1421)

### Iteration and collections

- [x] 3.53 `map` and `filter` answer lazy, one-shot views (727-749, 1063, 1106-1115, 480-482)
- [x] 3.54 Every iterator answers `has_next` by buffering one element (478-480)
- [x] 3.55 `Str` and `Dict` join the iterable mixin; subscripts follow the AST context (1065-1071, 768-772, 783-794)
- [x] 3.56 Sets and views copy CPython's method/operator asymmetry (496-498, 1102-1104)

### Class machinery and constructors

- [x] 3.57 `Object` is the implicit base of every class (1473-1486)
- [x] 3.58 Native-demanding protocol slots are adapted at class build (1323)
- [x] 3.59 A builtin subclass constructs as the builtin does; a class refuses binary operators (1319-1337, 1256)

### Executor and performance

- [x] 3.60 A non-tty stdin is a program, not a REPL (`arch:2026-10-15-cli-repl-streams`)
- [x] 3.61 Lazy imports break cycles; performance is guarded structurally (931, 913, `arch:2026-10-14-lazy-imports`, `arch:2026-10-14-hot-path-imports`, `arch:2026-10-14-object-hooks-off-the-hot-path`)

### Reporting and the REPL

- [ ] 3.62 The uncaught report shows the chain, nearest first, by CPython's rule (50)
- [x] 3.63 A source file is read the way CPython reads it (54)
- [x] 3.64 `:explain` covers every message a validator composes (56)

### This change

- [ ] 3.65 Decisions live in `doc/adr/`, replacing `INFECTIONS.md`, dated the day it lands: *Context* names `INFECTIONS.md`'s three jobs and decision 4 of `arch:2026-10-14-backlog-to-openspec`, which it reverses; *Decision* is the log, the `MIGRATION.md` reference and the OpenSpec rule of design decision 6. Written after group 4, before 5.1.

## 4. `MIGRATION.md`

- [ ] 4.1 Add *Banned constructs*: one row per ban from every validator table (`Python | POOP substitute | validator`), definitive bans linking ADR 3.4; verify every validator in `DEFAULT_VALIDATORS` has at least one row, and list in `inventory.md` the sections that were reference only.
- [ ] 4.2 Add *Type reference*: the API tables (PoopMeta, Object, NoneClass, Boolean, Block, collection methods, builtin-mirroring signatures, Range, Slice, Error, Object.print, the transformer rewrite tables) moved without rationale; verify every snippet added runs under `uv run poop`.
- [ ] 4.3 Repoint the intro sentence and the line-185 § link to the new section and ADR 3.45.

## 5. OpenSpec configuration

- [ ] 5.1 In `openspec/config.yaml`, rewrite `context` and `rules.specs` and add `rules.design` as design decision 6 states; verify `openspec instructions design --change adopt-adr-log --json` returns the ADR rule and `openspec instructions specs --change adopt-adr-log --json` no longer names `INFECTIONS.md`.

## 6. Contributor documents

- [ ] 6.1 `CONTRIBUTING.md`: the catalogue pointer (line ~33), Language, the four "Add an entry to `INFECTIONS.md`" steps (a row in the `MIGRATION.md` table, an ADR when there is a decision) and *Closing a change* step 2.
- [ ] 6.2 `AGENTS.md`: the docs bullet ("Update `README.md` and `INFECTIONS.md` …") and any other mention.
- [ ] 6.3 `README.md` "Where to next": `doc/adr/` and the `MIGRATION.md` reference; verify `uv run pytest tests/test_doc_counts.py -q` passes.
- [ ] 6.4 `.github/copilot-instructions.md` step 5 and `.claude/skills/backlog/SKILL.md` step 3.

## 7. Citations in code

- [ ] 7.1 Repoint the `INFECTIONS.md` citations in `poop/` and `pyproject.toml` to the ADR path (design decision 7); verify `uv run ruff check` passes.
- [ ] 7.2 Same for `tests/`; verify `uv run pytest -q` passes.

## 8. Retire `INFECTIONS.md`

- [ ] 8.1 Diff the `INFECTIONS.md` section list against `inventory.md` plus `MIGRATION.md`; then `git rm INFECTIONS.md`, delete `inventory.md`, and verify `git grep -n INFECTIONS -- ':!openspec/changes/archive' ':!openspec/changes/adopt-adr-log' ':!doc/adr'` prints nothing.
- [ ] 8.2 Full gate: `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest` (read pytest's summary line) and `openspec validate adopt-adr-log --strict`.

## Workflow follow-up

- Archive with `/openspec-archive-change`; the change declares `skip_specs`, so there is no sync.
