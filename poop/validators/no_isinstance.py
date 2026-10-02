from poop.validators._call_name import CallNameValidator


class NoIsinstanceValidator(CallNameValidator):
    forbidden = frozenset({"isinstance"})
    message = "isinstance() is forbidden — use obj.is_instance(Type) instead"
