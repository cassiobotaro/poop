from poop.validators._call_name import CallNameValidator


class NoMapValidator(CallNameValidator):
    forbidden = frozenset({"map"})
    message = "map() is forbidden — use col.map(block) instead"
