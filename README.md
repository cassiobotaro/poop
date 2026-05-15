<p align="center">
  <img src="poop.png" alt="POOP logo" width="600">
</p>

# POOP 💩

**POOP** is an acronym for **P**ython **O**bject **O**riented **P**rogramming.

A Python interpreter infected by Smalltalk.

## Development

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync --dev

# Run
poop <file.py>
uv run python main.py <file.py>  # alternative without installing

# Lint and format
uv run ruff check --fix
uv run ruff format

# Type check (examples/ excluded — uses runtime-injected names)
uv run ty check poop/ tests/

# Tests with coverage
uv run pytest
```

Git hooks are managed by [prek](https://prek.j178.dev) and run ruff and ty on every commit.

## Usage

```bash
poop examples/hello_world.py   # run a file
poop                            # interactive REPL (Ctrl+D to exit)
```

## Quickstart

POOP rewrites Python so that **every operation is a message sent to an object** — no free functions, no control-flow statements. Two mechanisms drive this:

- **Validators** reject forbidden constructs (`if`, `for`, `while`, `print(...)`, `len(x)`, …).
- **Transformers** rewrite the AST before execution so every literal becomes a POOP type (`Int`, `Str`, `Boolean`, `List`, …) and `range()` / `bool()` / `list()` / … return their POOP equivalents.

### Key substitutions

| Python | POOP |
|---|---|
| `print(x)` | `x.print()` |
| `if cond:` / `else:` | `cond.if_true(lambda: …)` / `cond.if_false(lambda: …)` |
| `for x in col:` | `col.do(lambda x: …)` |
| `while cond:` | `(lambda: cond).while_true(lambda: …)` |
| `not x` | `x.not_()` |
| `-x` | `x.negated()` |
| `len(x)` | `x.len()` |
| `x[i]` | `x.at(i)` |
| `x[a:b]` | `x.slice(a, b)` |
| `x and y` | `x.and_(lambda: y)` |
| `x or y` | `x.or_(lambda: y)` |
| `math.sqrt(x)` | `math.sqrt(x)` |
| `random.choice(xs)` | `random.choice(xs)` |
| `random.Random(seed)` | `Random(seed)` |
| `errno.EPERM` | `errno.EPERM` |
| `getpass.getuser()` | `getpass.getuser()` |
| `secrets.token_hex(16)` | `secrets.token_hex(16)` |
| `base64.b64encode(b)` | `b.b64encode()` |
| `base64.b64decode(s)` | `s.b64decode()` |
| `binascii.crc32(b)` | `binascii.crc32(b)` |
| `mimetypes.guess_type(url)` | `mimetypes.guess_type(url)` |
| `webbrowser.open(url)` | `webbrowser.open(url)` |
| `glob.glob("*.py")` | `glob.glob("*.py")` |
| `fnmatch.fnmatch(n, p)` | `fnmatch.fnmatch(n, p)` |
| `copy.deepcopy(x)` | `copy.deepcopy(x)` |
| `pprint.pformat(x)` | `pprint.pformat(x)` |
| `bisect.insort(xs, n)` | `bisect.insort(xs, n)` |
| `heapq.heappush(h, x)` | `heapq.heappush(h, x)` |
| `shlex.split(cmd)` | `shlex.split(cmd)` |
| `uuid.uuid4()` | `uuid.uuid4()` |
| `uuid.UUID(s)` | `UUID(s)` |
| `json.dumps(obj)` | `json.dumps(obj)` |
| `json.loads(s)` | `json.loads(s)` |
| `tomllib.loads(s)` | `tomllib.loads(s)` |
| `hmac.new(k, m).hexdigest()` | `hmac.new(k, m).hexdigest()` |
| `graphlib.TopologicalSorter()` | `TopologicalSorter()` |
| `re.match(p, s).group()` | `re.match(p, s).group()` |

For the full set of Python → POOP recipes (iteration, comprehensions, exceptions, file I/O, …), see [`MIGRATION.md`](MIGRATION.md).

### Hello, World

```python
"Hello, World!".print()
```

### FizzBuzz

```python
class FizzBuzz:
    def run(self):
        range(1, 101).do(
            lambda i: (i % 15 == 0).if_true_if_false(
                lambda: "FizzBuzz".print(),
                lambda: (i % 3 == 0).if_true_if_false(
                    lambda: "Fizz".print(),
                    lambda: (i % 5 == 0).if_true_if_false(
                        lambda: "Buzz".print(),
                        lambda: i.print(),
                    ),
                ),
            )
        )

FizzBuzz().run()
```

### Leap year

```python
class Year:
    def __init__(self, value):
        self._value = value

    def is_leap(self):
        return (self._value % 400 == 0).or_(
            lambda: (self._value % 4 == 0).and_(
                lambda: (self._value % 100 == 0).not_()
            )
        )

Year(2000).is_leap().print()  # true
Year(1900).is_leap().print()  # false
```

More examples in [`examples/`](examples/).

## Type annotations

Type annotations (`x: int`, `def f(x: int) -> str:`) are not evaluated at
runtime in Python and do not cause errors in POOP programs. However, they are
misleading: POOP transforms all literals to its own types (`Int`, `Str`, …),
so a variable annotated as `int` will hold an `Int` at runtime.

Avoid type annotations in POOP programs. The `type` keyword (`type X = int`)
is explicitly banned by the validator pipeline.
