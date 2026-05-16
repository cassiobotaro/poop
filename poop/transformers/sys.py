from poop.types.sys import Args, Stdin, Stdout, Sys

NAMESPACE: dict[str, object] = {
    "sys": Sys,
    "args": Args,
    "Stdout": Stdout,
    "Stdin": Stdin,
}
