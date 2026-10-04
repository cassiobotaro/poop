from poop.validators._call_name import CallNameValidator


class NoAsciiValidator(CallNameValidator):
    forbidden = frozenset({"ascii"})
    message = "ascii() is forbidden — use obj.ascii() instead"
