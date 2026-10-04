from poop.validators._call_name import CallNameValidator


class NoChrValidator(CallNameValidator):
    forbidden = frozenset({"chr", "ord"})
    message = "{name}() is forbidden — use obj.{name}() instead"
