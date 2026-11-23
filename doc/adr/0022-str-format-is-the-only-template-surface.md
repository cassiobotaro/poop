# 22. `Str.format` is the only template surface

Date: 2026-04-22

## Status

Accepted

## Context

`no_fstring` bans f-strings (`ast.JoinedStr`) because `{...}` interpolation hides message sends and bypasses POOP's `Str`, and t-strings (`ast.TemplateStr`) because they share the interpolation and yield a raw `Template`. Its substitute is concatenation (`("Hello, " + name)`). A program still needs a template, and Python offers three: `str.format`, `format_map`, and printf-style `%`.

`str.format` resolves `{0.__class__}` and `{0[0]}` at runtime, from inside a string literal no validator can read. `"{0.__class__}".format(5)` printed `<class 'int'>`, reopening what `no_dunder_attribute` closes, and `{0[0]}` reopened what `no_subscript` closes, against the raw Python value, since `Str.format` deep-unwraps its arguments through `to_python`.

The failures were CPython's in all five modes. `"{a}".format(b=1)` answered a bare `KeyError: 'a'`; `"{}".format()` named the "positional args tuple", Python's calling convention; `"{:d}".format("a")` named a "format code" for an "object of type"; and the brace errors said `format string`, Python's name for what POOP calls a template.

`Str.__mod__` implemented printf formatting in full. It duplicated `format` with a second template language whose directives (`%d`, `%r`, `%-5.2f`) are Python conventions a POOP program has no other reason to learn, and with no forbidden construct to substitute. `"%(k)s" % mapping` is a key lookup written as syntax, so the same operation was refused through `format` and granted through `%`.

`format(x, spec)` is banned as a free function with `x.format(spec)` as its substitute. On a `Str` that collides with the template message: a spec is read as an argument for placeholders the string does not have, and `str.format` discards extra positional arguments, so `"ab".format(">6")` answered `'ab'`, unchanged and silently. The alternative was to have `Str.format` disambiguate on its argument, treating one `Str` that parses as a spec, with no placeholders in the receiver, as the `Object.format` sense. It reads better at the call site and was refused: it decides by inspection, on "a value whose class and contents disagree".

The `2026-10-14-text-mirrors-complete` change found `format_map` missing from `Str`. `"{a}-{b}".format_map({"a": 1, "b": 2})` is the message-shaped spelling of what POOP forced into a `**d` spread. Implementing it as `self.format(**to_python(mapping))` was rejected: a mapping with non-string keys would fail inside `**` in CPython's wording.

## Decision

`"{}".format(...)` is POOP's template surface, with `format_map` as its mapping form. Printf `%` is removed: `"%s" % (a,)` answers `str does not understand #% with a tuple`.

- A format field may not reach an attribute or an item. `Str._reject_field_access` refuses both spellings and recurses into nested specs (`"{0:{1.__class__}}"`). Only the field name is inspected, so `{:.2f}`, `{!r}`, `{name}` and `{:{width}}` are untouched.
- The template surface words its own failures: `the template asks for 'a', which no argument named: b`, `the template asks for more than the 1 value it was given`, `a str cannot be formatted with 'd'`. `_reject_field_access` runs inside the same guard, and its own refusal passes through untouched.
- `format` and `format_map` share `Str._fill_template`, so `"{a.__class__}".format_map(d)` is refused exactly as `"{0.__class__}".format(x)` is. A non-mapping is refused by `a_mapping` (`#… expects a mapping, got an int`), and a positional field in a `format_map` template keeps CPython's `Format string contains positional fields`, which names nothing POOP forbids.
- On a `Str`, the substitute for `format(x, spec)` is `"{:spec}".format(text)`, and the `no_format` ban names that exception.

## Consequences

`_reject_field_access` is the third half of the dunder ban, next to `_reject_dunder`: both guard a spelling that reaches the runtime as data. The five failing template programs are in the wording sweep's `_FAILING` list. `tests/test_substitutes.py` walks every Substitute column and sends what it names, which makes the `Str` exception falsifiable.
