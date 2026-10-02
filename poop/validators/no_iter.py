from poop.validators._call_name import CallNameValidator


class NoIterValidator(CallNameValidator):
    forbidden = frozenset({"iter", "next", "aiter", "anext"})
    message = "{name}() is forbidden — use col.iter() / it.next() instead"
