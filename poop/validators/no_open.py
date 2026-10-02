from poop.validators._call_name import CallNameValidator


class NoOpenValidator(CallNameValidator):
    forbidden = frozenset({"open"})
    message = "open() is forbidden — POOP has no file I/O"
