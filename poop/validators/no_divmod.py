from poop.validators._call_name import make_call_name_validator

NoDivmodValidator = make_call_name_validator(
    forbidden={"divmod"},
    message="divmod() is forbidden — use a.divmod(b) instead",
)
