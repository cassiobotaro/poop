from poop.validators._call_name import make_call_name_validator

NoOpenValidator = make_call_name_validator(
    forbidden={"open"},
    message="open() is forbidden — POOP has no file I/O",
)
