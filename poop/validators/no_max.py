from poop.validators._call_name import CallNameValidator


class NoMaxValidator(CallNameValidator):
    forbidden = frozenset({"max"})
    message = "max() is forbidden — use a.max(b) instead"
