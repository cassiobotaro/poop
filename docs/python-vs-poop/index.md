# Python vs POOP

POOP rejects most of Python's syntax for control flow and most of its
builtins. The replacements look unfamiliar at first because POOP makes
**every operation a method call on an object** — there are no statements
that "do" things, only objects that receive messages and decide what to
do with them.

This section is a side-by-side translation guide. It assumes you know
Python and does not assume you know Smalltalk.

## How to read each entry

Each comparison follows the same shape:

- **Python** — what you would normally write.
- **POOP** — the equivalent that the validators accept.
- **Why** — one sentence explaining what is happening, in Python terms.
- **See also** — a runnable file in
  [`examples/`](https://github.com/cassiobotaro/poop/tree/main/examples)
  that uses the construct in context.

You can run any of the linked examples with:

```bash
poop examples/<file>.py
```

## Topics

- [Conditionals](conditionals.md) — replacing `if`, `if/else`, `and`,
  `or`, `not`, `assert`.
- [Loops](loops.md) — replacing `for`, `while`, `enumerate`, `zip`,
  `break`, `continue`.
- [Builtins](builtins.md) — replacing `print`, `len`, `sum`, `map`,
  `filter`, `isinstance`, `try/except`, `with`, and friends.

!!! info "Why message-passing?"
    POOP draws the idea from Smalltalk, where `2 + 3` is the message `+`
    sent to the integer `2` with argument `3`. You don't need to know
    Smalltalk to read this guide — but if you're curious, look for the
    "Smalltalk origin" callouts sprinkled through each page.
