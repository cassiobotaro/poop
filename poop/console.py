"""The two consoles the CLI and the REPL write through.

One per stream, so colour is decided per destination: values and prompts go to
stdout, diagnostics to stderr. rich detects each stream's tty independently and
honours `NO_COLOR`, so `poop file 2>err.log` colours neither the redirected file
nor a non-terminal, while an interactive stdout stays coloured.
"""

from rich.console import Console
from rich.text import Text

OUT = Console()
ERR = Console(stderr=True)


def in_colour(console: Console) -> bool:
    """Whether `console` is a terminal that wants colour."""
    return console.is_terminal and not console.no_color


def error_line(console: Console, text: str) -> None:
    """One diagnostic line on `console`: red on a colour terminal, plain elsewhere.

    The CLI's `cannot read` line, the REPL's `_error` and the location-less
    error report all come through here, so none decides the colour on its
    own and none stays uncoloured on a terminal where the others are red.
    The console already knows whether it is a terminal, so the style is
    applied here and rich drops it where it does not belong.
    """
    console.print(Text(text, style="red"), soft_wrap=True, highlight=False)
