from poop.validators._call_name import CallNameValidator


class NoReversedValidator(CallNameValidator):
    forbidden = frozenset({"reversed"})
    message = "reversed() is forbidden — use col.reversed() instead"
