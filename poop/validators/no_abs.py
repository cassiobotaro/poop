from poop.validators._call_name import CallNameValidator


class NoAbsValidator(CallNameValidator):
    forbidden = frozenset({"abs"})
    message = "abs() is forbidden — use obj.abs() instead"
