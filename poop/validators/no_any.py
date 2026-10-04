from poop.validators._call_name import CallNameValidator


class NoAnyValidator(CallNameValidator):
    forbidden = frozenset({"any"})
    message = "any() is forbidden — use col.any(block) instead"
