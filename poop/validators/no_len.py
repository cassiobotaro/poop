from poop.validators._call_name import CallNameValidator


class NoLenValidator(CallNameValidator):
    forbidden = frozenset({"len"})
    message = "len() is forbidden — use obj.len() instead"
