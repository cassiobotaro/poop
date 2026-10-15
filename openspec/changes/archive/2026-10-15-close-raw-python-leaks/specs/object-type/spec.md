# Spec Delta

## ADDED Requirements

### Requirement: does_not_understand receives the selector as a Str
When a message is not answered, the receiver's `does_not_understand` hook
SHALL be handed the selector as a POOP `Str`, so a hook that answers the name
answers an object every message reaches.

#### Scenario: The hook's answer is a POOP string
- **WHEN** a class defines `def does_not_understand(self, name): return name` and a program prints `P().foo`
- **THEN** it prints `foo` and `P().foo.upper()` answers `FOO`

#### Scenario: The hook can compare the selector
- **WHEN** the hook body is `return name.startswith("get_")`
- **THEN** `P().get_x` answers `True` as a POOP Boolean
