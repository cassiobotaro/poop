# Inventory

Working list for `adopt-adr-log`, deleted in task 8.1. Number, date (design decision 3), task, title.

| ADR | Date | Task | Title |
|---|---|---|---|
| 1 | commit day | 2.1 | Record architecture decisions |
| 2 | 2026-04-21 | 3.7 | Every literal is transformed |
| 3 | 2026-04-21 | 3.8 | Every basic type has a POOP wrapper |
| 4 | 2026-04-21 | 3.9 | POOP methods answer POOP types |
| 5 | 2026-04-21 | 3.11 | `true`, `false` and `none` are singletons |
| 6 | 2026-04-22 | 3.1 | Everything is an object; every operation is a message |
| 7 | 2026-04-22 | 3.2 | Message aesthetics decides whether a construct is infected |
| 8 | 2026-04-22 | 3.3 | Methods use Python names, not Smalltalk's |
| 9 | 2026-04-22 | 3.4 | A validator is activated only with its substitute; definitive bans |
| 10 | 2026-04-22 | 3.5 | Every type represents itself through `__str__`, and a displayed value reads back as itself |
| 11 | 2026-04-22 | 3.6 | `__slots__` on every POOP class, mixins included |
| 12 | 2026-04-22 | 3.12 | Constructor builtins are intercepted, not banned |
| 13 | 2026-04-22 | 3.13 | Dunders are exposed as plain methods |
| 14 | 2026-04-22 | 3.14 | Wrappers are mangled and cloaked as builtins |
| 15 | 2026-04-22 | 3.18 | Single-underscore internals are unreachable |
| 16 | 2026-04-22 | 3.19 | One `is_message` predicate serves every discovery surface |
| 17 | 2026-04-22 | 3.20 | A class may not define lookup, creation or descriptor dunders |
| 18 | 2026-04-22 | 3.21 | Class machinery is accepted only where it was argued for |
| 19 | 2026-04-22 | 3.22 | A class is built from its bases alone |
| 20 | 2026-04-22 | 3.26 | No `id`: identity is a question |
| 21 | 2026-04-22 | 3.44 | `and_` and `or_` take blocks |
| 22 | 2026-04-22 | 3.49 | `Str.format` is the only template surface |
| 23 | 2026-04-22 | 3.53 | `map` and `filter` answer lazy, one-shot views |
| 24 | 2026-04-22 | 3.55 | `Str` and `Dict` join the iterable mixin; subscripts follow the AST context |
| 25 | 2026-04-23 | 3.34 | `Error` wraps a caught exception and honours suppression |
| 26 | 2026-04-23 | 3.37 | `With` keeps the native protocol and passes POOP values; it checks both arguments where written |
| 27 | 2026-04-23 | 3.45 | Binary operators stay, unary ones go; chained comparison is allowed on ergonomics |
| 28 | 2026-04-26 | 3.43 | Every `lambda` is a `Block`; loops are messages to blocks |
| 29 | 2026-05-05 | 3.10 | Void mutators answer `none` |
| 30 | 2026-05-05 | 3.54 | Every iterator answers `has_next` by buffering one element |
| 31 | 2026-05-12 | 3.57 | `Object` is the implicit base of every class |
| 32 | 2026-06-26 | 3.23 | Numeric equality follows CPython's numeric tower |
| 33 | 2026-07-15 | 3.17 | Dunder access is banned by rule, at runtime too; `__init__` only on a `super()` receiver |
| 34 | 2026-07-15 | 3.30 | Only the exceptions POOP can reach are mirrored |
| 35 | 2026-07-15 | 3.31 | Mirrors match through `__instancecheck__`, with no translation layer |
| 36 | 2026-07-15 | 3.41 | `does_not_understand` answers with layered hints |
| 37 | 2026-07-15 | 3.47 | The class side is data descriptors on a `type` metaclass and refuses instance messages |
| 38 | 2026-07-17 | 3.42 | Wrong kinds are refused in POOP's words, wrong values in CPython's |
| 39 | 2026-07-17 | 3.48 | Substitutes mirror the full builtin signature; accessors are methods |
| 40 | 2026-07-25 | 3.16 | Programs are confined to a builtins allow-list |
| 41 | 2026-07-25 | 3.46 | The `message` descriptor is installed at class build; method blocks wrap on the bound result; a method is a block whichever way it is read |
| 42 | 2026-07-25 | 3.56 | Sets and views copy CPython's method/operator asymmetry |
| 43 | 2026-07-27 | 3.35 | POOP raises a reachable failure only through a mirror, and the report names it |
| 44 | 2026-07-27 | 3.39 | A diagnostic never names a banned construct; operator errors are reworded by a pinned regex |
| 45 | 2026-07-27 | 3.40 | Arity refusals keep CPython's sentence and name POOP's class |
| 46 | 2026-07-27 | 3.50 | Text codecs are limited to four encodings, constructors included |
| 47 | 2026-08-09 | 3.24 | `Boolean` stays outside `Int` and answers the int side |
| 48 | 2026-08-09 | 3.27 | `Range` stores an inclusive bound, decoded in one place, and reads its bounds by index |
| 49 | 2026-08-09 | 3.32 | `raise_` is a class-side message, `raise_from` an instance one |
| 50 | 2026-08-09 | 3.52 | `MemoryView` is a one-dimensional byte view that answers `index` and `count` |
| 51 | 2026-08-10 | 3.15 | A bare builtin name is the converter alias |
| 52 | 2026-08-10 | 3.58 | Native-demanding protocol slots are adapted at class build |
| 53 | 2026-08-10 | 3.59 | A builtin subclass constructs as the builtin does; a class refuses binary operators |
| 54 | 2026-08-11 | 3.36 | `Try` answers values and `else_` receives the value; it checks both arguments where written |
| 55 | 2026-08-11 | 3.63 | A source file is read the way CPython reads it |
| 56 | 2026-08-11 | 3.64 | `:explain` covers every message a validator composes |
| 57 | 2026-10-04 | 3.25 | Comparison rules live in `__eq__`, symmetric across subclasses |
| 58 | 2026-10-04 | 3.51 | `Bytes` and `ByteArray` share a mixin cloaked as `bytes` |
| 59 | 2026-10-09 | 3.28 | `FrozenDict` and `MappingProxy` are both kept |
| 60 | 2026-10-09 | 3.29 | Python 3.15's `sentinel` is wrapped faithfully |
| 61 | 2026-10-09 | 3.38 | The recursion limit is sized by frames per send |
| 62 | 2026-10-14 | 3.61 | Lazy imports break cycles; performance is guarded structurally |
| 63 | 2026-10-15 | 3.33 | Built exceptions have a POOP instance side |
| 64 | 2026-10-15 | 3.60 | A non-tty stdin is a program, not a REPL |
| 65 | 2026-10-19 | 3.62 | The uncaught report shows the chain, nearest first, by CPython's rule |
| 66 | commit day | 3.65 | Decisions live in `doc/adr/`, replacing `INFECTIONS.md` |

## Sections

Every `###` heading of `INFECTIONS.md`, with the ADRs that extract from it. A section with none is reference only and moves to `MIGRATION.md` (tasks 4.1, 4.2).

- L60 No `if`: reference only
- L67 No loops: reference only
- L75 No free functions: reference only
- L84 No `print`: reference only
- L90 No `assert`: reference only
- L96 No `raise`: reference only
- L102 No `try`: 9
- L111 No `with`: reference only
- L118 No `and`/`or`: 21
- L131 No `async`: 9
- L162 No `not`: reference only
- L168 No unary minus: reference only
- L176 No unary plus: reference only
- L182 No bitwise invert: reference only
- L188 No `is` / `is not`: reference only
- L195 No `global`/`nonlocal`: reference only
- L202 No `yield`: reference only
- L209 No walrus (`:=`): reference only
- L215 No decorator: 18
- L225 No class machinery outside its position: 18
- L245 No class keyword: 19
- L253 No dunder definition: 17
- L263 No `type` alias: 19
- L272 No `match/case`: reference only
- L278 No f-strings or t-strings: 22
- L291 No `len`: reference only
- L297 No `abs`: reference only
- L303 No `hash`: reference only
- L309 No `isinstance`: reference only
- L315 No `repr`: reference only
- L321 No `ascii`: reference only
- L327 No `issubclass`: reference only
- L333 No `callable`: reference only
- L339 No `id`: 20
- L345 No `all`: reference only
- L351 No `any`: reference only
- L357 No `min`/`max`: 39
- L400 No `bin`/`hex`/`oct`: reference only
- L408 No `chr`/`ord`: reference only
- L417 No `divmod`: reference only
- L423 No `pow`: 39
- L431 No `getattr`: reference only
- L438 No `hasattr`: reference only
- L444 No `format`: 22
- L454 `zip` → `Zip`: reference only
- L462 `enumerate` → `Enumerate`: reference only
- L468 No `iter`/`next`: 30
- L486 Dict views: 42
- L500 MappingProxy: reference only
- L504 No `setattr`/`delattr`: reference only
- L511 No introspection: reference only
- L519 No `dir`: 16
- L529 No dunder attributes: 33, 38, 48
- L567 No dunder names: 33
- L582 Builtins allow-list: 40, 44
- L601 No `type`: reference only
- L607 No `exec`/`eval`/`compile`: reference only
- L615 No `exit`/`quit`: reference only
- L622 No `breakpoint`: reference only
- L628 No `help`: reference only
- L634 No `input`: reference only
- L642 No `open`: reference only
- L650 No `del`: reference only
- L656 No `import`: reference only
- L665 No `_poop_*` prefix: reference only
- L675 No private attributes: 15
- L693 No namespace shadow: 14
- L708 No builtin shadow: reference only
- L716 No `sum`: reference only
- L727 No `map` / `filter`: 23
- L751 No `round`: reference only
- L760 No `sorted` / `reversed`: reference only
- L776 No `in` / `not in`: reference only
- L783 No subscript: 24, 44
- L806 No comprehension: reference only
- L816 Augmented assignment (`+=`, `-=`, `*=`, …): 27
- L820 `super`: 18
- L824 `property` / `classmethod` / `staticmethod`: reference only
- L828 Binary infix operators (`+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`): 27
- L846 Numeric comparisons follow CPython's numeric tower: 32, 47
- L856 PoopExcMeta: 34, 35, 43, 49, 61, 63
- L884 PoopMeta: 37
- L921 Object: 20, 36, 41, 57
- L968 NoneClass: 4
- L993 EllipsisClass: reference only
- L1003 Boolean: 47
- L1018 Block: 28, 41, 45
- L1041 Collection iterable methods: 24
- L1073 Builtin-mirroring method signatures: 39, 42
- L1106 Map / Filter: 23
- L1117 Range: 48
- L1143 Object.print: reference only
- L1162 Error: 25
- L1179 Try: 54
- L1200 With: 26
- L1224 Slice: reference only
- L1262 Int: reference only
- L1274 Float: reference only
- L1286 Ellipsis: reference only
- L1295 Boolean: reference only
- L1303 None: reference only
- L1309 Str: 2, 38, 46, 52, 53
- L1345 Bytes: reference only
- L1356 List: reference only
- L1363 Tuple: reference only
- L1370 Set: reference only
- L1377 Dict: reference only
- L1387 Complex: reference only
- L1397 ByteArray: 38, 58
- L1413 MemoryView: 50
- L1425 FrozenSet: reference only
- L1431 FrozenDict: 59
- L1442 Sentinel: 59, 60
- L1455 Range: reference only
- L1463 Raise: 49
- L1473 Class: 31

## Stale passages (task 1.2)

Checked with `uv run poop` at `5a3725cc`:

- Line 1254, "`Range.slice` returns `List`": stale. `range(10).slice(1, 3)` answers `range(1, 3)`, class `range`, as line 1139 says. ADR 48 states the `Range` answer; the 1254 note is not carried over.
- Line 1037, "the other spelling stays a leak": stale. `[1, 2].len` answers `<block>`, class `function`, since the `message` descriptor. ADR 41 keeps the measurement as *Context* (why the `__getattribute__` hook was rejected) and states the current behaviour.
- Lines 964-966, "POOP has no first-class metaclass or class-object type": stale. `int.name()` answers `int`, `int.superclass()` answers `object`, and `int.class_()` is refused with a hint; `is_instance(int)` still takes the class itself. ADR 37 states that a class is an object answering the class side, and that `is_instance` takes it; "a deliberate primitive leak" is not carried over.
