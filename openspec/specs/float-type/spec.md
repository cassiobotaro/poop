# float-type Specification

## Purpose

The messages a `Float` value and the `float` class answer in POOP, mirroring
CPython's `float` message for message and wording every refusal as a message
sent to an object.

## Requirements

### Requirement: The float class converts a real number with from_number
The `float` class SHALL answer `from_number(x)` with a `Float` holding the
value of `x`, for any `x` that is an integer, a boolean or a float, as Python
3.14's `float.from_number` does. A subclass of `float` SHALL answer an instance
of itself.

#### Scenario: An integer becomes a float
- **WHEN** a program sends `float.from_number(3)`
- **THEN** the answer prints `3.0` and is a `float`

#### Scenario: A boolean is the integer it stands for
- **WHEN** a program sends `float.from_number(True)`
- **THEN** the answer prints `1.0`

#### Scenario: A float is answered unchanged
- **WHEN** a program sends `float.from_number(2.5)`
- **THEN** the answer equals `2.5`

#### Scenario: A subclass answers itself
- **WHEN** a program defines `class Money(float)` and sends `Money.from_number(3)`
- **THEN** the answer is an instance of `Money`

### Requirement: from_number refuses a non-number in POOP's wording
`float.from_number` SHALL refuse a string, a complex, a collection or any other
non-real argument with a `TypeError` whose message names the message and the
argument's class in POOP's vocabulary, and never CPython's
`must be real number, not str`.

#### Scenario: A string is refused
- **WHEN** a program sends `float.from_number("3")`
- **THEN** a `TypeError` is raised whose message reads `#from_number expects a real number, got a str`

#### Scenario: A complex is refused
- **WHEN** a program sends `float.from_number(1j)`
- **THEN** a `TypeError` is raised whose message reads `#from_number expects a real number, got a complex`

#### Scenario: The refusal is catchable by its mirror
- **WHEN** a program wraps `float.from_number("x")` in `Try(...).except_(TypeError, handler).run()`
- **THEN** the handler runs

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
