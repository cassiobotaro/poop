from poop.validators._call_name import CallNameValidator


class NoIssubclassValidator(CallNameValidator):
    forbidden = frozenset({"issubclass"})
    message = "issubclass() is forbidden — use Klass.is_subclass(Other) instead"
