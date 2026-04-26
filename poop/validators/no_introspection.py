from poop.validators._call_name import make_call_name_validator

NoIntrospectionValidator = make_call_name_validator(
    forbidden={"globals", "locals", "vars"},
    message='{name}() is forbidden — state lives in instances, not in scope introspection',
)
