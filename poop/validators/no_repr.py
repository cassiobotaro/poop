from poop.validators._call_name import make_call_name_validator

NoReprValidator = make_call_name_validator(
    forbidden={"repr"},
    message="repr() is forbidden — use obj.repr() instead",
)
