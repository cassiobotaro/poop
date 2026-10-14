# method-blocks Specification

## Purpose

What a method read off a POOP object or class answers: a block that prints,
compares and calls, whichever kind of method it is and whichever side it is
read from, so a reader never meets CPython's `function` or `method`.

## Requirements

### Requirement: A static method read off an instance or its class is a block
A `staticmethod` of a wrapper (`maketrans` on `str`, `bytes`, `bytearray`)
SHALL answer a block when read off an instance or off the class, never
CPython's raw function.

#### Scenario: Read off the class
- **WHEN** a program sends `str.maketrans.print()`
- **THEN** the output is `<block>`

#### Scenario: Read off an instance
- **WHEN** a program sends `"".maketrans.print()`
- **THEN** the output is `<block>`

#### Scenario: Read off a byte class
- **WHEN** a program sends `bytes.maketrans.callable().print()`
- **THEN** the output is `True`

### Requirement: A class method read off the class is a block
A `classmethod` of a wrapper (`from_bytes`, `fromhex`, `fromkeys`,
`from_number`, `is_subclass`) SHALL answer a block when read off the class, as
it already does when read off an instance.

#### Scenario: Read off the class
- **WHEN** a program sends `int.from_bytes.print()`
- **THEN** the output is `<block>`

#### Scenario: Read off an instance still answers a block
- **WHEN** a program sends `(5).from_bytes.print()`
- **THEN** the output is `<block>`

### Requirement: Two reads of one static or class method are equal
Reading the same `staticmethod` or `classmethod` twice SHALL answer blocks
that compare equal and hash alike, as two reads of an instance method do.

#### Scenario: A static method read twice
- **WHEN** a program sends `(str.maketrans == str.maketrans).print()`
- **THEN** the output is `True`

#### Scenario: A class method read twice
- **WHEN** a program sends `(int.from_bytes == int.from_bytes).print()`
- **THEN** the output is `True`

#### Scenario: Two different methods are not equal
- **WHEN** a program sends `(str.maketrans == bytes.maketrans).print()`
- **THEN** the output is `False`

### Requirement: The block calls as the method did, with the method's arity wording
The block answered for a static or class method SHALL call exactly as the
method does and SHALL keep CPython's cloaked arity sentence for a wrong call,
as a block made from an instance method does.

#### Scenario: A static method call
- **WHEN** a program sends `str.maketrans("a", "b").print()`
- **THEN** the output is `{97: 98}`

#### Scenario: A class method call
- **WHEN** a program sends `int.from_bytes(b"\x05").print()`
- **THEN** the output is `5`

#### Scenario: A wrong-arity call keeps the method's sentence
- **WHEN** a program sends `str.maketrans()`
- **THEN** a `TypeError` is raised whose message reads `str.maketrans() missing 1 required positional argument: 'x'`

### Requirement: An instance method read off the class is still refused
Reading a plain instance method off the class SHALL keep answering the
class-side refusal, never a block.

#### Scenario: The refusal is unchanged
- **WHEN** a program sends `str.upper()`
- **THEN** an `AttributeError` is raised whose message reads `str does not understand #upper — #upper asks an instance; send it to one`
