# Spec Delta

## ADDED Requirements

### Requirement: Type parameters are refused at validation
The validator SHALL refuse a PEP 695 type parameter on a class, a function or
a `type` statement — a `TypeVar`, a `ParamSpec` or a `TypeVarTuple` — before
the program runs, and `--validators-only` SHALL list each one.

#### Scenario: A generic class is refused
- **WHEN** a program contains `class X[T]:` followed by `pass`
- **THEN** validation fails with `type parameters are forbidden — POOP has no static types; drop the [T]` pointing at line 1

#### Scenario: A generic method is refused
- **WHEN** a method in a class body is written `def m[T](self):`
- **THEN** validation fails with `type parameters are forbidden — POOP has no static types; drop the [T]`

#### Scenario: The parameter's own spelling is named
- **WHEN** a class is written `class X[*Ts]:` or `class X[**P]:`
- **THEN** validation fails with the same sentence, ending `drop the [*Ts]` and `drop the [**P]` respectively

#### Scenario: Every occurrence is listed
- **WHEN** `--validators-only` runs on a file with a generic class on line 1 and a generic method on line 4
- **THEN** both lines are reported, in source order
