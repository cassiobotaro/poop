from poop.validators._call_name import make_call_name_validator

NoPowValidator = make_call_name_validator(
    forbidden={"pow"},
    message="pow() is forbidden — use a.pow(b) instead",
)
