from poop.validators._call_name import make_call_name_validator

NoOpenValidator = make_call_name_validator(
    forbidden={"open"},
    message="open() is forbidden — use Path('foo').read_text() / write_text() instead",
)
