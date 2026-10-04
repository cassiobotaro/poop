from poop.validators._call_name import CallNameValidator


class NoMinValidator(CallNameValidator):
    forbidden = frozenset({"min"})
    message = "min() is forbidden — use a.min(b) instead"
