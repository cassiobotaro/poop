from poop.validators._call_name import CallNameValidator


class NoAllValidator(CallNameValidator):
    forbidden = frozenset({"all"})
    message = "all() is forbidden — use col.all(block) instead"
