from poop.validators._call_name import CallNameValidator


class NoPowValidator(CallNameValidator):
    forbidden = frozenset({"pow"})
    message = "pow() is forbidden — use a.pow(b) instead"
