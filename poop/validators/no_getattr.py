from poop.validators._call_name import CallNameValidator


class NoGetattrValidator(CallNameValidator):
    forbidden = frozenset({"getattr"})
    message = "getattr() is forbidden — use obj.get_attr(name) instead"
