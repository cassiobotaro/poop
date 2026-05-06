from poop.validators._call_name import make_call_name_validator

NoInputValidator = make_call_name_validator(
    forbidden={"input"},
    message="input() is forbidden — use prompt.input() instead",
)
