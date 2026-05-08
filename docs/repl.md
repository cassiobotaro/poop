# REPL

POOP ships a REPL — a "read-eval-print loop" that lets you type
expressions one at a time and see the result. It's the fastest way to
explore a method or sanity-check a snippet.

## Launching it

Run `poop` with no arguments:

```bash
poop
```

You'll see:

```
POOP 💩  — Python infected by Smalltalk. Ctrl+D to exit.
>>>
```

The cyan `>>>` is your prompt. Type Python source; press Enter to
evaluate. Press **Ctrl+D** to exit.

## Your first session

```
>>> 2 + 3
5
>>> "Hello, World"
'Hello, World'
>>> _
'Hello, World'
>>> [1, 2, 3].sum()
6
```

Two things to notice:

- **String values render with their quotes** (`'Hello, World'`) because
  the REPL shows each value's `repr`, not its plain text. To print a
  string without quotes, send it `.print()`.
- **`_` holds the last value** — handy for chaining without naming
  variables.

## What's already in scope

The REPL pre-loads everything in `DEFAULT_NAMESPACE`
(`poop/transformers/__init__.py`). You can use these names without any
import:

| Name | What it is |
|---|---|
| `True` / `False` / `None` | The POOP boolean and none singletons |
| `range` / `list` / `dict` / `set` / `tuple` / `frozenset` | Constructors that return POOP collection types |
| `enumerate` / `zip` | Iterable wrappers |
| `Slice` | Reusable slice value (`Slice(1, 4)`) |
| `Try` / `With` | Replacements for `try` and `with` statements |
| `Block` | Wrapper around a callable, exposing `while_true` / `while_false` |
| `Error` | Exception wrapper passed to `Try.except_` handlers |
| `raise_` | Helper to raise an exception value |

There's no `import` step for any of this — they're injected before
your code runs.

## `print()` echoes `None`

When you call a method that returns `none` (notably `.print()`), the
REPL displays the printed text **and then** echoes `None` because the
REPL's display hook reports every top-level value:

```
>>> "Hello".print()
Hello
None
```

This is harmless. To avoid the echo, use a bare expression so its
value is the thing you want to inspect:

```
>>> "Hello"
'Hello'
```

## Multi-line input

If a line ends with `:` (the start of a class, function, or `if/for/while`
header — `if/for/while` are forbidden but Python's parser still accepts
the colon), the next prompt switches to a dim `...` and the REPL
auto-indents four spaces:

```
>>> class Greeter:
...     def hello(self, name):
...         return "Hi, " + name
...
>>> Greeter().hello("Alice")
'Hi, Alice'
```

Submit a blank line to close the block.

If you press **Ctrl+C** while in continuation mode, the buffer is
discarded and you return to a fresh `>>>` prompt.

## Tab completion

Press **Tab** to complete:

- a name in the current namespace (`ran<TAB>` → `range(`)
- an attribute on a value (`"hi".<TAB>` → lists every method on `Str`)

Callable matches get a trailing `(` to remind you they're methods.
Names starting with `_poop_` and dunder names (`__init__`) are hidden.

## History

Every line you submit is saved to `~/.poop_history` (capped at 1000
lines). Use **↑** / **↓** to scroll through previous input, even
across REPL sessions.

## Reading errors

POOP errors print as `poop: <message>` (in red on a TTY) instead of a
full Python traceback. Two flavors you'll meet:

**Validator rejection** — when you try a forbidden Python construct.
Includes line/column from the parser:

```
>>> len([1, 2, 3])
poop: len() is forbidden — use obj.len() instead (line 1, col 0)
```

**Runtime error** — when the program runs but a method fails:

```
>>> [].at(0)
poop: list index out of range
```

The buffer is cleared after either kind of error, so the next prompt
starts fresh.

## Exit

- **Ctrl+D** (EOF) — exits the REPL.
- **Ctrl+C** — clears the current input buffer and returns you to
  `>>>`. It does **not** exit on its own.

## Next steps

- Looking up a specific replacement? See [Python vs POOP](python-vs-poop/index.md).
- Want to read source files instead? `poop examples/hello_world.py` runs
  any of the [bundled examples](https://github.com/cassiobotaro/poop/tree/main/examples).
