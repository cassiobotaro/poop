from poop.validators._call_name import make_call_name_validator

NoFilterValidator = make_call_name_validator(
    forbidden={"filter"},
    message="filter() is forbidden — use col.filter(block) instead",
)
