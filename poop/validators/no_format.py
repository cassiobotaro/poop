from poop.validators._call_name import make_call_name_validator

NoFormatValidator = make_call_name_validator(
    forbidden={"format"},
    message="format() is forbidden — use obj.format(spec) instead",
)
