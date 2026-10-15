from poop.validators._call_name import CallNameValidator


class NoExitValidator(CallNameValidator):
    forbidden = frozenset({"exit", "quit"})
    message = "{name}() is forbidden — POOP offers no substitute"
