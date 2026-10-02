from poop.validators._call_name import CallNameValidator


class NoIssubclassValidator(CallNameValidator):
    forbidden = frozenset({"issubclass"})
    message = "issubclass() is forbidden — use Class.is_subclass(Other) instead"
