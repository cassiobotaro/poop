from poop.validators._call_name import CallNameValidator


class NoDivmodValidator(CallNameValidator):
    forbidden = frozenset({"divmod"})
    message = "divmod() is forbidden — use a.divmod(b) instead"
