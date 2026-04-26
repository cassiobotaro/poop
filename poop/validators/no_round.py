from poop.validators._call_name import make_call_name_validator

NoRoundValidator = make_call_name_validator(
    forbidden={"round"},
    message="round() is forbidden — use obj.round() instead",
)
