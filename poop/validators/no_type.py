from poop.validators._call_name import CallNameValidator


class NoTypeValidator(CallNameValidator):
    forbidden = frozenset({"type"})
    message = "type() is forbidden — use obj.class_name() or polymorphism instead"
