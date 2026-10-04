from poop.validators._call_name import CallNameValidator


class NoPrintValidator(CallNameValidator):
    forbidden = frozenset({"print"})
    message = "print is forbidden — use obj.print() instead"
