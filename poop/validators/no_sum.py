from poop.validators._call_name import CallNameValidator


class NoSumValidator(CallNameValidator):
    forbidden = frozenset({"sum"})
    message = "sum() is forbidden — use col.sum() instead"
