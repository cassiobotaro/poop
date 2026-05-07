# Getting started

POOP requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

## Install

```bash
git clone https://github.com/cassiobotaro/poop.git
cd poop
uv sync --dev
```

## Run a POOP program

```bash
poop examples/hello_world.py
# or, without installing:
uv run python main.py examples/hello_world.py
```

## Your first program

Create `hello.py`:

```python
"Hello, World!".print()
```

Run it:

```bash
poop hello.py
```

## A larger example — FizzBuzz

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

More examples live in
[`examples/`](https://github.com/cassiobotaro/poop/tree/main/examples)
in the repository.

## Type annotations

Type annotations (`x: int`, `def f(x: int) -> str:`) are not evaluated
at runtime in Python and do not cause errors in POOP programs. However,
they are misleading: POOP transforms all literals to its own types
(`Int`, `Str`, …), so a variable annotated as `int` will hold an `Int`
at runtime.

Avoid type annotations in POOP programs. The `type` keyword
(`type X = int`) is explicitly banned by the validator pipeline.
