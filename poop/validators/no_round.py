from poop.validators._call_name import CallNameValidator


class NoRoundValidator(CallNameValidator):
    forbidden = frozenset({"round"})
    message = "round() is forbidden — use obj.round() instead"
