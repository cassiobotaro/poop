"""The two consoles the CLI and the REPL write through.

One per stream, so colour is decided per destination: values and prompts go to
stdout, diagnostics to stderr. rich detects each stream's tty independently and
honours `NO_COLOR`, so `poop file 2>err.log` colours neither the redirected file
nor a non-terminal, while an interactive stdout stays coloured.
"""

from rich.console import Console

OUT = Console()
ERR = Console(stderr=True)


def in_colour(console: Console) -> bool:
    """Whether `console` is a terminal that wants colour."""
    return console.is_terminal and not console.no_color
