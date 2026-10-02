from poop.validators._call_name import CallNameValidator


class NoExecValidator(CallNameValidator):
    forbidden = frozenset({"exec", "eval", "compile", "__import__"})
    message = "{name}() is forbidden — metaprogramming is not allowed"
