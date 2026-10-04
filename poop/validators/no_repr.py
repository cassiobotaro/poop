from poop.validators._call_name import CallNameValidator


class NoReprValidator(CallNameValidator):
    forbidden = frozenset({"repr"})
    message = "repr() is forbidden — use obj.repr() instead"
