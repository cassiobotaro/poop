from poop.validators._call_name import CallNameValidator


class NoHashValidator(CallNameValidator):
    forbidden = frozenset({"hash"})
    message = "hash() is forbidden — use obj.hash() instead"
