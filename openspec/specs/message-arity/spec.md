# message-arity Specification

## Purpose
Which class a message's wrong-arity sentence names. The sentence keeps
CPython's shape, and the class inside it is the one CPython would name: the
class that defines the message, as a program can write it.

## Requirements

### Requirement: A message a shared mixin defines names the receiver's builtin
A wrong-arity call to a message that a shared implementation defines, rather
than a builtin, SHALL name the receiver's builtin class in CPython's
sentence, never `object`, which does not answer the message.

#### Scenario: map on a list
- **WHEN** a program runs `[1].map(lambda x: x, 2)`
- **THEN** a `TypeError` is raised reading `list.map() takes from 1 to 2 positional arguments but 3 were given`

#### Scenario: has_next on an iterator
- **WHEN** a program runs `[1].iter().has_next(1)`
- **THEN** a `TypeError` is raised reading `list_iterator.has_next() takes 1 positional argument but 2 were given`

#### Scenario: mapping on a dict view
- **WHEN** a program runs `{"a": 1}.keys().mapping(1)`
- **THEN** a `TypeError` is raised reading `dict_keys.mapping() takes 1 positional argument but 2 were given`

### Requirement: bytearray and frozendict name themselves
A wrong-arity call to a message `bytearray` shares with `bytes`, or
`frozendict` with `dict`, SHALL name the receiver's own class, as CPython
does: both types define their own methods there.

#### Scenario: bytearray
- **WHEN** a program runs `bytearray(b"a").lower(1)`
- **THEN** a `TypeError` is raised reading `bytearray.lower() takes 1 positional argument but 2 were given`

#### Scenario: frozendict
- **WHEN** a program runs `frozendict({"a": 1}).keys(1)`
- **THEN** a `TypeError` is raised reading `frozendict.keys() takes 1 positional argument but 2 were given`

### Requirement: A class-side message names the class
A wrong-arity call to a class-side message SHALL name the receiving class,
as CPython's `int.mro(1)` names `int`, including a program's own class.

#### Scenario: A builtin class
- **WHEN** a program runs `int.hash(1)`
- **THEN** a `TypeError` is raised reading `int.hash() takes 1 positional argument but 2 were given`

#### Scenario: A program's class
- **WHEN** a program defines `class Foo(Object)` and runs `Foo.repr(1)`
- **THEN** a `TypeError` is raised reading `Foo.repr() takes 1 positional argument but 2 were given`

### Requirement: The class CPython would name is kept
A message defined by the root `object`, and a message a program's subclass
inherits from a builtin, SHALL keep naming that class, as CPython names the
defining class.

#### Scenario: A message object defines
- **WHEN** a program runs `(5).repr(1)`
- **THEN** a `TypeError` is raised reading `object.repr() takes 1 positional argument but 2 were given`

#### Scenario: A program's subclass of list
- **WHEN** a program defines `class Stack(list)` and runs `Stack().append()`
- **THEN** a `TypeError` is raised reading `list.append() missing 1 required positional argument: 'obj'`

#### Scenario: A message a POOP construct defines
- **WHEN** a program runs `Try(lambda: 1).except_(ValueError)`
- **THEN** a `TypeError` is raised reading `Try.except_() missing 1 required positional argument: 'handler'`

### Requirement: A caught error names its exception's class
A wrong-arity call to a message a caught error defines SHALL name the class
of the exception it wraps, the class the error answers to `class_()`, never
`object`. A message `Object` defines SHALL keep naming `object`.

#### Scenario: message on a caught ValueError
- **WHEN** a handler for `ValueError` runs `e.message(1)`
- **THEN** a `TypeError` is raised reading `ValueError.message() takes 1 positional argument but 2 were given`

#### Scenario: A message object defines
- **WHEN** a handler for `ValueError` runs `e.repr(1)`
- **THEN** a `TypeError` is raised reading `object.repr() takes 1 positional argument but 2 were given`

### Requirement: A missing block in the branch family is refused with the hint
The branch messages (`if_true`, `if_false`, `if_true_if_false`,
`if_false_if_true`, `and_` and `or_` on a boolean; `if_none`, `if_not_none`
and both pairs on `None` and on every object; `while_true` and `while_false`
on a block) SHALL refuse a missing block with the sentence they give a
non-block, showing every block the message takes.

#### Scenario: if_true with nothing
- **WHEN** a program runs `True.if_true()`
- **THEN** a `TypeError` is raised reading `#if_true expects a block, got nothing — write .if_true(lambda: …)`

#### Scenario: A boolean pair with one block
- **WHEN** a program runs `True.if_true_if_false(lambda: 1)`
- **THEN** a `TypeError` is raised reading `#if_true_if_false expects a block, got nothing — write .if_true_if_false(lambda: …, lambda: …)`

#### Scenario: A boolean pair handed a non-block
- **WHEN** a program runs `True.if_false_if_true(5, 5)`
- **THEN** a `TypeError` is raised reading `#if_false_if_true expects a block, got an int — write .if_false_if_true(lambda: …, lambda: …)`

#### Scenario: and_ with nothing
- **WHEN** a program runs `True.and_()`
- **THEN** a `TypeError` is raised reading `#and_ expects a block, got nothing — write .and_(lambda: …)`

#### Scenario: if_none on None
- **WHEN** a program runs `None.if_none()`
- **THEN** a `TypeError` is raised reading `#if_none expects a block, got nothing — write .if_none(lambda: …)`

#### Scenario: A null pair on an object
- **WHEN** a program runs `(5).if_none_if_not_none()`
- **THEN** a `TypeError` is raised reading `#if_none_if_not_none expects a block, got nothing — write .if_none_if_not_none(lambda: …, lambda x: …)`

#### Scenario: while_true with nothing
- **WHEN** a program runs `(lambda: True).while_true()`
- **THEN** a `TypeError` is raised reading `#while_true expects a block, got nothing — write .while_true(lambda: …)`
