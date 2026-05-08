# Lesson 1 — Strings

**Goal:** print text, read input from the user, and concatenate strings
— but the POOP way.

## What's new

In Python you write `print("Hello")` — calling the global function
`print` with a string argument. POOP forbids the global `print`.
Instead, **the string itself does the printing**, by receiving the
message `.print()`:

```python
"Hello".print()
```

Same with reading input. Python writes `input("Name? ")`; POOP sends
`.input()` to the prompt string:

```python
name = "Name? ".input()
```

The shift you'll keep noticing: a Python *function* that takes a value
becomes a *method* on the value.

## Walk-through

Save this to `hello.py`:

```python
"Hello".print()
```

Run it:

```bash
poop hello.py
```

You'll see:

```
Hello
```

A string with whitespace works the same way:

```python
"Hello, World!".print()
```

Concatenation is just `+`:

```python
("Hello, " + "World!").print()
```

You can also try these in the [REPL](../repl.md) — just remember
that `.print()` returns `none` and the REPL echoes `None` on the
next line:

```
>>> "Hello".print()
Hello
None
```

That's the REPL displaying the return value, not your program
printing anything extra.

Now make it interactive. Save this to `greet.py`:

```python
name = "What is your name? ".input()
("Hello, " + name + "!").print()
```

Run it:

```bash
poop greet.py
```

You'll be prompted for a name and greeted by it.

## Try it

Write a program that asks for two strings — a greeting and a name —
and prints them joined by a comma and a space. Example:

```
$ poop greet.py
Greeting? Hi
Name? Alice
Hi, Alice
```

## Anchor example

[`examples/greet.py`](https://github.com/cassiobotaro/poop/blob/main/examples/greet.py) — the greeting program in two lines, the way the language is meant to look.

## Reference

- [Python vs POOP — Builtins](../python-vs-poop/builtins.md) for the
  full list of forbidden builtins (`print`, `input`, `len`, …) and
  their POOP replacements.
- [Next lesson — Conditionals →](02-conditionals.md)
