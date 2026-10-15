# value-equality Specification

## Purpose
How a POOP wrapper compares with another wrapper of the same value, with a
subclass of itself, and across the groups CPython compares by value.

## Requirements

### Requirement: A subclass of a wrapper equals the wrapper by value
A wrapper and an instance of a program's subclass of it SHALL compare equal
when their values are equal, in both operand orders, and SHALL hash alike,
so one can be looked up by the other.

#### Scenario: A str subclass equals the str, both ways
- **WHEN** a program defines `class Name(str): pass` and prints `Name("a") == "a"` and `"a" == Name("a")`
- **THEN** both print `True`

#### Scenario: A list subclass equals the list
- **WHEN** a program defines `class Stack(list): pass` and prints `Stack([1]) == [1]`
- **THEN** it prints `True`

#### Scenario: A dict keyed by the subclass is found by the value
- **WHEN** a program runs `{Name("a"): 1}.at("a").print()`
- **THEN** it prints `1`

#### Scenario: Different values stay unequal
- **WHEN** a program prints `Name("a") == "b"`
- **THEN** it prints `False`
