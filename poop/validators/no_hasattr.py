from poop.validators._call_name import CallNameValidator


class NoHasattrValidator(CallNameValidator):
    forbidden = frozenset({"hasattr"})
    message = "hasattr() is forbidden — use obj.has_attr(name) instead"
