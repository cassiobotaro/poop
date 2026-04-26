from poop.validators._call_name import make_call_name_validator

NoHashValidator = make_call_name_validator(
    forbidden={"hash"},
    message="hash() is forbidden — use obj.hash() instead",
)
