from poop.types.sys import Stdin, Stdout, Sys

NAMESPACE: dict[str, object] = {
    "sys": Sys,
    "Stdout": Stdout,
    "Stdin": Stdin,
}
