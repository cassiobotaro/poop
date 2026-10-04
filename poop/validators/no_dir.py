from poop.validators._call_name import CallNameValidator


class NoDirValidator(CallNameValidator):
    forbidden = frozenset({"dir"})
    message = "dir() is forbidden — use obj.dir() instead"
