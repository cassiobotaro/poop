# 51. A bare builtin name is the converter alias

Date: 2026-08-10

## Status

Accepted

## Context

Every converter transformer has two rewrites. `visit_Call` sends `list(x)` to the converter, and `visit_Name` sends a bare `list` somewhere else. For a long time the second went to the wrapper class, whose constructor means "build from these elements" rather than "convert". `_arity.py` closed that gap for the direct call; binding the name first reopened it one indirection away, mostly in silence:

- `x = list; x([1, 2])` answered `[[1, 2]]`;
- `x = tuple; x([1, 2])` answered `([1, 2],)`;
- `x = int; x(4.9)` answered an `int` holding 4.9, which then said `float does not understand #+ with an int`, a value whose class and contents disagree.

The spelling is not exotic. A constructor is an object, so `[list, set].at(0)([1, 2])` and `lambda c: c([1, 2])` are the same program, and passing a converter as a block is ordinary where iteration is `map`/`filter`.

The class itself cannot be the converter, because `poop/types/` builds its values by calling these classes directly (`Str(...)`, `List(*elements)`), which is the other meaning. The bare name still has to be a class, because that is what it is otherwise for: `(5).is_instance(int)`, `class Stack(list)`, `int.name()`. For the type-argument case, an `__instancecheck__` delegating to the wrapped class (the shape `PoopExcMeta` uses for the mirrors) was considered and cannot work. The alias is a subclass, and while `PoopMeta` derived from `ABCMeta`, `ABCMeta`'s subclass walk came straight back to it until the stack gave out.

## Decision

Each bare builtin name binds a `_poop_<name>_cls` alias (`poop/types/_alias.py`): a subclass of the wrapper whose metaclass answers a call with the converter. A program's own subclass, such as `class Stack(list)`, still constructs a `Stack`; ADR 53 records how.

`is_instance` and `is_subclass` call `unalias` on both the instance and the class sides, so the alias and the wrapper answer the type question as one class.

## Consequences

A converter reached through a name, a collection or a block converts as the direct call does.

The alias and the wrapper are two objects that both call themselves by the builtin's name. Every place that compares, climbs or constructs classes has to treat the pair as one class; ADR 53 records the places where that was done.

`poop/types/` keeps calling the wrapper classes directly to build values, unaffected by the alias.
