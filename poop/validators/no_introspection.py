from poop.validators._call_name import CallNameValidator


class NoIntrospectionValidator(CallNameValidator):
    forbidden = frozenset({"globals", "locals", "vars"})
    message = (
        "{name}() is forbidden — state lives in instances, not in scope introspection"
    )
