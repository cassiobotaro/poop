from poop.validators._call_name import make_call_name_validator

NoAllValidator = make_call_name_validator(
    forbidden={"all"},
    message="all() is forbidden — use col.all(block) instead",
)
