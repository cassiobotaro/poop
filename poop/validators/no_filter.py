from poop.validators._call_name import CallNameValidator


class NoFilterValidator(CallNameValidator):
    forbidden = frozenset({"filter"})
    message = "filter() is forbidden — use col.filter(block) instead"
