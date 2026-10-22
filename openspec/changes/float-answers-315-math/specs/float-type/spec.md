# Spec Delta

## ADDED Requirements

### Requirement: A Float answers whether it is NaN, infinite or finite
A `Float` SHALL answer `isnan()`, `isinf()` and `isfinite()` with the
`Boolean` that `math.isnan`, `math.isinf` and `math.isfinite` answer for its
value.

#### Scenario: NaN is NaN
- **WHEN** a program sends `float("nan").isnan().print()`
- **THEN** it prints `True`

#### Scenario: A number is not NaN
- **WHEN** a program sends `(1.5).isnan().print()`
- **THEN** it prints `False`

#### Scenario: Infinity is infinite
- **WHEN** a program sends `float("inf").isinf().print()`
- **THEN** it prints `True`

#### Scenario: A number is finite
- **WHEN** a program sends `(1.5).isfinite().print()`
- **THEN** it prints `True`

#### Scenario: Infinity is not finite
- **WHEN** a program sends `float("-inf").isfinite().print()`
- **THEN** it prints `False`

### Requirement: A Float answers whether it is normal or subnormal
A `Float` SHALL answer `isnormal()` and `issubnormal()` with the `Boolean`
that Python 3.15's `math.isnormal` and `math.issubnormal` answer for its
value: zero, NaN and infinity are neither, and a value below the smallest
normal magnitude is subnormal.

#### Scenario: One is normal
- **WHEN** a program sends `(1.0).isnormal().print()`
- **THEN** it prints `True`

#### Scenario: Zero is not normal
- **WHEN** a program sends `(0.0).isnormal().print()`
- **THEN** it prints `False`

#### Scenario: The smallest float is subnormal
- **WHEN** a program sends `(5e-324).issubnormal().print()`
- **THEN** it prints `True`

#### Scenario: One is not subnormal
- **WHEN** a program sends `(1.0).issubnormal().print()`
- **THEN** it prints `False`

### Requirement: A Float answers its sign bit
A `Float` SHALL answer `signbit()` with `True` when its sign bit is set and
`False` otherwise, as Python 3.15's `math.signbit` does, so a negative zero
answers `True` where `< 0` answers `False`.

#### Scenario: A negative number
- **WHEN** a program sends `(-2.5).signbit().print()`
- **THEN** it prints `True`

#### Scenario: Negative zero
- **WHEN** a program sends `(-0.0).signbit().print()`
- **THEN** it prints `True`

#### Scenario: Positive zero
- **WHEN** a program sends `(0.0).signbit().print()`
- **THEN** it prints `False`
