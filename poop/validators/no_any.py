from poop.validators._call_name import make_call_name_validator

NoAnyValidator = make_call_name_validator(
    forbidden={"any"},
    message="any() is forbidden — use col.any(block) instead",
)
