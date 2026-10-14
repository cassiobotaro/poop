# Spec Delta

## Purpose

Where the prologue that converts `*args` and `**kwargs` into POOP values is
inserted in a method body.

## ADDED Requirements

### Requirement: The variadic prologue follows the docstring
The statements that rebind `*args` and `**kwargs` SHALL be inserted after a
docstring when the body has one, and first otherwise.

#### Scenario: A variadic method with a docstring
- **WHEN** `poop --transformers-only` runs a file holding `def m(self, *args):` with the docstring `"""doc"""` and `return args`
- **THEN** the dump shows `"""doc"""` first and `args = _poop_tuple_from(args)` second

#### Scenario: A variadic method without a docstring
- **WHEN** `poop --transformers-only` runs a file holding `def m(self, **kw):` with the body `return kw`
- **THEN** the dump shows `kw = _poop_dict_from_kwargs(kw)` as the first statement
