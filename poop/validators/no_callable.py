from poop.validators._call_name import CallNameValidator


class NoCallableValidator(CallNameValidator):
    forbidden = frozenset({"callable"})
    message = "callable() is forbidden — use obj.callable() instead"
