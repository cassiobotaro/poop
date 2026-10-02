from poop.validators._call_name import CallNameValidator


class NoInputValidator(CallNameValidator):
    forbidden = frozenset({"input"})
    message = "input() is forbidden — use prompt.input() instead"
