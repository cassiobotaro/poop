from poop.validators._call_name import CallNameValidator


class NoBinValidator(CallNameValidator):
    forbidden = frozenset({"bin", "hex", "oct"})
    message = "{name}() is forbidden — use n.{name}() instead"
