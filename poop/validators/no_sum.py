from poop.validators._call_name import make_call_name_validator

NoSumValidator = make_call_name_validator(
    forbidden={"sum"},
    message="sum() is forbidden — use col.sum() instead",
)
