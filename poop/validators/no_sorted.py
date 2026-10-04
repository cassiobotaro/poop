from poop.validators._call_name import CallNameValidator


class NoSortedValidator(CallNameValidator):
    forbidden = frozenset({"sorted"})
    message = "sorted() is forbidden — use col.sorted() instead"
